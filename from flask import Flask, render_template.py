from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
app = Flask(__name__)
app.secret_key = "segredo"
# =========================
# CONECTAR BANCO
# =========================
def conectar():
    return sqlite3.connect("rh.db")
# =========================
# CRIAR TABELAS
# =========================
def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    # FUNCIONARIOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        contato TEXT,
        setor TEXT,
        email TEXT,
        cargo TEXT,
        salario REAL,
        status TEXT DEFAULT 'ATIVO',
        data_admissao TEXT
    )
    """)
    # LOGS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        funcionario_id INTEGER,
        acao TEXT,
        responsavel TEXT,
        data TEXT
    )
    """)
    # AVISOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS avisos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        mensagem TEXT,
        autor TEXT,
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
            session["user"] = usuario
            return redirect("/home")
        else:
            return "Acesso negado"

    return render_template("login.html")
# =========================
# HOME
# =========================
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template(
        "index.html",
        user=session["user"]
    )
# =========================
# CADASTRAR
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
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO funcionarios
        (nome, contato, setor, email, cargo, salario, data_admissao)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            nome,
            contato,
            setor,
            email,
            cargo,
            salario,
            data
        ))
        funcionario_id = cursor.lastrowid
        # LOG
        cursor.execute("""
        INSERT INTO logs
        (funcionario_id, acao, responsavel, data)
        VALUES (?, ?, ?, ?)
        """, (
            funcionario_id,
            "CADASTRO",
            session["user"],
            data
        ))
        conn.commit()
        conn.close()
        return redirect("/listar")
    return render_template("cadastrar.html")
# =========================
# LISTAR
# =========================
@app.route("/listar")
def listar():
    if "user" not in session:
        return redirect("/")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM funcionarios
    ORDER BY id DESC
    """)
    funcionarios = cursor.fetchall()
    conn.close()
    return render_template(
        "listar.html",
        funcionarios=funcionarios
    )
# =========================
# EDITAR
# =========================
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if "user" not in session:
        return redirect("/")
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
        SET nome=?,
            contato=?,
            setor=?,
            email=?,
            cargo=?,
            salario=?
        WHERE id=?
        """, (
            nome,
            contato,
            setor,
            email,
            cargo,
            salario,
            id
        ))
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        # LOG
        cursor.execute("""
        INSERT INTO logs
        (funcionario_id, acao, responsavel, data)
        VALUES (?, ?, ?, ?)
        """, (
            id,
            "ATUALIZOU",
            session["user"],
            data
        ))
        conn.commit()
        conn.close()
        return redirect("/listar")
    cursor.execute("""
    SELECT * FROM funcionarios
    WHERE id=?
    """, (id,))
    funcionario = cursor.fetchone()
    conn.close()
    return render_template(
        "editar.html",
        funcionario=funcionario
    )
# =========================
# DESLIGAR
# =========================
@app.route("/desligar/<int:id>")
def desligar(id):
    if "user" not in session:
        return redirect("/")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE funcionarios
    SET status='DESLIGADO'
    WHERE id=?
    """, (id,))
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    # LOG
    cursor.execute("""
    INSERT INTO logs
    (funcionario_id, acao, responsavel, data)
    VALUES (?, ?, ?, ?)
    """, (
        id,
        "DESLIGOU",
        session["user"],
        data
    ))
    conn.commit()
    conn.close()
    return redirect("/listar")
# =========================
# DELETAR
# =========================
@app.route("/deletar/<int:id>")
def deletar(id):
    if "user" not in session:
        return redirect("/")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    DELETE FROM funcionarios
    WHERE id=?
    """, (id,))
    conn.commit()
    conn.close()
    return redirect("/listar")
# =========================
# LOGS
# =========================
@app.route("/logs")
def logs():
    if "user" not in session:
        return redirect("/")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM logs
    ORDER BY id DESC
    """)
    logs = cursor.fetchall()
    conn.close()
    return render_template(
        "logs.html",
        logs=logs
    )
# =========================
# RESUMO
# =========================
@app.route("/resumo")
def resumo():
    if "user" not in session:
        return redirect("/")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT COUNT(*) FROM funcionarios
    """)
    total = cursor.fetchone()[0]
    cursor.execute("""
    SELECT COUNT(*) FROM funcionarios
    WHERE status='ATIVO'
    """)
    ativos = cursor.fetchone()[0]
    cursor.execute("""
    SELECT COUNT(*) FROM funcionarios
    WHERE status='DESLIGADO'
    """)
    desligados = cursor.fetchone()[0]
    conn.close()
    return render_template(
        "resumo.html",
        total=total,
        ativos=ativos,
        desligados=desligados
    )
# =========================
# SETORES
# =========================
@app.route("/setores")
def setores():
    if "user" not in session:
        return redirect("/")
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT setor, COUNT(*)
    FROM funcionarios
    WHERE status='ATIVO'
    GROUP BY setor
    """)
    setores = cursor.fetchall()
    conn.close()
    return render_template(
        "setores.html",
        setores=setores
    )
# =========================
# AVISOS
# =========================
@app.route("/avisos", methods=["GET", "POST"])
def avisos():
    if "user" not in session:
        return redirect("/")
    conn = conectar()
    cursor = conn.cursor()
    if request.method == "POST":
        titulo = request.form["titulo"]
        mensagem = request.form["mensagem"]
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        cursor.execute("""
        INSERT INTO avisos
        (titulo, mensagem, autor, data)
        VALUES (?, ?, ?, ?)
        """, (
            titulo,
            mensagem,
            session["user"],
            data
        ))
        conn.commit()
    cursor.execute("""
    SELECT * FROM avisos
    ORDER BY id DESC
    """)
    avisos = cursor.fetchall()
    conn.close()
    return render_template(
        "avisos.html",
        avisos=avisos
    )
# =========================
# LIMPAR LOGS
# =========================
@app.route("/limpar_logs")
def limpar_logs():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs")
    conn.commit()
    conn.close()
    return redirect("/logs")
# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
# =========================
# INICIAR
# =========================
if __name__ == "__main__":
    app.run(debug=True)