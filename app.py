from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "segredo"

# =========================
# BANCO
# =========================
def conectar():
    return sqlite3.connect("rh.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        contato TEXT,
        setor TEXT,
        salario REAL,
        status TEXT DEFAULT 'ATIVO',
        data_admissao TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        funcionario_id INTEGER,
        acao TEXT,
        responsavel TEXT,
        data TEXT
    )
    """)

    conn.commit()
    conn.close()

criar_tabelas()

# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"].lower()
        senha = request.form["senha"]

        if usuario in ["alexandre", "vitor", "ighor"] and senha == "a32026":
            session["user"] = usuario.capitalize()
            return redirect("/home")

        return "Acesso negado"

    return render_template("login.html")


@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("index.html", user=session["user"])


# =========================
# CADASTRO
# =========================
@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        nome = request.form["nome"]
        contato = request.form["contato"]
        setor = request.form["setor"]
        email = request.form["email"]
        cargo = request.form["cargo"]
        salario = request.form["salario"]

        conn = conectar()
        cursor = conn.cursor()

        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO funcionarios (nome, contato, setor, email, cargo, salario, data_admissao)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome, contato, setor, email, cargo, salario, data))

        func_id = cursor.lastrowid

        cursor.execute("""
        INSERT INTO logs (funcionario_id, acao, responsavel, data)
        VALUES (?, ?, ?, ?)
        """, (func_id, "CADASTRO", session["user"], data))

        conn.commit()
        conn.close()

        return redirect("/listar")

    return render_template("cadastrar.html")


# =========================
# LISTAR
# =========================
@app.route("/listar")
def listar():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM funcionarios")
    dados = cursor.fetchall()

    conn.close()

    return render_template("listar.html", funcionarios=dados)


# =========================
# EDITAR
# =========================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = conectar()
    cursor = conn.cursor()

    if request.method == "POST":
        nome = request.form["nome"]
        contato = request.form["contato"]
        setor = request.form["setor"]
        email = request.form["email"]
        cargo = request.form["cargo"]
        salario = request.form["salario"]

        cursor.execute("""
        UPDATE funcionarios
        SET nome=?, contato=?, setor=?, email=?, cargo=?, salario=?
        WHERE id=?
        """, (nome, contato, setor, email, cargo, salario, id))

        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
        INSERT INTO logs (funcionario_id, acao, responsavel, data)
        VALUES (?, ?, ?, ?)
        """, (id, "ATUALIZAÇÃO", session["user"], data))

        conn.commit()
        conn.close()

        return redirect("/listar")

    cursor.execute("SELECT * FROM funcionarios WHERE id=?", (id,))
    func = cursor.fetchone()
    
    conn.close()

    return render_template("editar.html", f=func)


# =========================
# DESLIGAR
# =========================
@app.route("/desligar/<int:id>")
def desligar(id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("UPDATE funcionarios SET status='DESLIGADO' WHERE id=?", (id,))

    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO logs (funcionario_id, acao, responsavel, data)
    VALUES (?, ?, ?, ?)
    """, (id, "DESLIGAMENTO", session["user"], data))

    conn.commit()
    conn.close()

    return redirect("/listar")


# =========================
# LOGS
# =========================
@app.route("/logs")
def logs():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM logs")
    dados = cursor.fetchall()

    conn.close()

    return render_template("logs.html", logs=dados)

@app.route("/limpar_logs")
def limpar_logs():
    if "user" not in session:
        return redirect("/")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM logs")

    conn.commit()
    conn.close()

    return redirect("/logs")


# =========================
# RESUMO
# =========================
@app.route("/resumo")
def resumo():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM funcionarios")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE status='ATIVO'")
    ativos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE status='DESLIGADO'")
    desligados = cursor.fetchone()[0]

    conn.close()

    return render_template("resumo.html", total=total, ativos=ativos, desligados=desligados)


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/deletar/<int:id>")
def deletar(id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM funcionarios WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/listar")


if __name__ == "__main__":
    app.run(debug=True)