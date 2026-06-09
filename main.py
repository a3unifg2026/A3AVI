import csv
import io
import os
import sqlite3
from datetime import datetime

from flask import Flask, Response, flash, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))

DATABASE = "rh.db"


def get_db():
    """Retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa as tabelas do banco de dados."""
    conn = get_db()
    cursor = conn.cursor()
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
            data_admissao TEXT,
            data_desligamento TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tabela_setores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS epis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER,
            item TEXT,
            status TEXT DEFAULT 'PENDENTE'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS treinamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER,
            nome_treinamento TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            funcionario_id INTEGER,
            nome_arquivo TEXT,
            formato TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            descricao TEXT,
            acao TEXT,
            responsavel TEXT,
            data TEXT
        )
    """)
    # Migração: se a tabela logs existia com schema antigo (funcionario_id),
    # recriar com o novo schema (descricao)
    cursor.execute("PRAGMA table_info(logs)")
    colunas = [col[1] for col in cursor.fetchall()]
    if "descricao" not in colunas:
        cursor.execute("DROP TABLE logs")
        cursor.execute("""
            CREATE TABLE logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descricao TEXT,
                acao TEXT,
                responsavel TEXT,
                data TEXT
            )
        """)
    # Migração: adicionar data_desligamento se não existir
    cursor.execute("PRAGMA table_info(funcionarios)")
    colunas_func = [col[1] for col in cursor.fetchall()]
    if "data_desligamento" not in colunas_func:
        cursor.execute("ALTER TABLE funcionarios ADD COLUMN data_desligamento TEXT")
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


def registrar_log(descricao, acao, responsavel):
    """Registra uma ação no log de auditoria."""
    conn = get_db()
    cursor = conn.cursor()
    data = datetime.now().strftime("%d/%m/%Y %H:%M")
    cursor.execute(
        "INSERT INTO logs (descricao, acao, responsavel, data) VALUES (?, ?, ?, ?)",
        (descricao, acao, responsavel, data)
    )
    conn.commit()
    conn.close()


init_db()


# ===== AUTENTICAÇÃO =====

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"].lower()
        senha = request.form["senha"]
        if usuario in ("alexandre", "vitor", "ighor") and senha == "a32026":
            session["user"] = usuario
            flash("Login realizado com sucesso!", "success")
            return redirect("/home")
        flash("Usuário ou senha inválidos.", "error")
        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ===== PÁGINAS PRINCIPAIS =====

@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    return render_template("index.html", user=session["user"])


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
        data_admissao = datetime.now().strftime("%d/%m/%Y %H:%M")

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM tabela_setores WHERE nome = ?", (setor,))
        setor_existe = cursor.fetchone()
        if setor_existe is None:
            conn.close()
            flash("Erro: o setor informado não existe. Cadastre-o primeiro.", "error")
            return redirect("/cadastrar")

        cursor.execute("SELECT * FROM funcionarios WHERE email = ?", (email,))
        email_duplicado = cursor.fetchone()
        if email_duplicado is not None:
            conn.close()
            flash("Erro: já existe um funcionário com este e-mail.", "error")
            return redirect("/cadastrar")

        cursor.execute(
            "INSERT INTO funcionarios (nome, contato, setor, email, cargo, salario, data_admissao) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (nome, contato, setor, email, cargo, salario, data_admissao)
        )
        conn.commit()
        conn.close()
        registrar_log(f"Funcionário '{nome}' cadastrado", "CADASTRO", session["user"])
        flash(f"Funcionário '{nome}' cadastrado com sucesso!", "success")
        return redirect("/listar")
    return render_template("cadastrar.html")


@app.route("/listar")
def listar():
    if "user" not in session:
        return redirect("/")
    busca = request.args.get("busca", "")
    filtro = request.args.get("filtro", "todos")
    conn = get_db()
    cursor = conn.cursor()

    if busca:
        if filtro == "ativos":
            cursor.execute(
                "SELECT * FROM funcionarios WHERE (nome LIKE ? OR id = ? OR setor LIKE ?) AND status = 'ATIVO' ORDER BY id DESC",
                (f"%{busca}%", busca, f"%{busca}%")
            )
        elif filtro == "desligados":
            cursor.execute(
                "SELECT * FROM funcionarios WHERE (nome LIKE ? OR id = ? OR setor LIKE ?) AND status = 'DESLIGADO' ORDER BY id DESC",
                (f"%{busca}%", busca, f"%{busca}%")
            )
        else:
            cursor.execute(
                "SELECT * FROM funcionarios WHERE nome LIKE ? OR id = ? OR setor LIKE ? ORDER BY id DESC",
                (f"%{busca}%", busca, f"%{busca}%")
            )
    else:
        if filtro == "ativos":
            cursor.execute("SELECT * FROM funcionarios WHERE status = 'ATIVO' ORDER BY id DESC")
        elif filtro == "desligados":
            cursor.execute("SELECT * FROM funcionarios WHERE status = 'DESLIGADO' ORDER BY id DESC")
        else:
            cursor.execute("SELECT * FROM funcionarios ORDER BY id DESC")

    funcionarios = cursor.fetchall()
    conn.close()
    return render_template("listar.html", funcionarios=funcionarios, filtro=filtro)


@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    if request.method == "POST":
        nome = request.form["nome"]
        contato = request.form["contato"]
        setor = request.form["setor"]
        email = request.form["email"]
        cargo = request.form["cargo"]
        salario = request.form["salario"]
        cursor.execute(
            "UPDATE funcionarios SET nome=?, contato=?, setor=?, email=?, cargo=?, salario=? WHERE id=?",
            (nome, contato, setor, email, cargo, salario, id)
        )
        conn.commit()
        conn.close()
        registrar_log(f"Funcionário #{id} '{nome}' atualizado", "ATUALIZOU", session["user"])
        flash("Funcionário atualizado com sucesso!", "success")
        return redirect("/listar")
    cursor.execute("SELECT * FROM funcionarios WHERE id=?", (id,))
    funcionario = cursor.fetchone()
    conn.close()
    return render_template("editar.html", funcionario=funcionario)


@app.route("/desligar/<int:id>", methods=["POST"])
def desligar(id):
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM epis WHERE funcionario_id = ? AND status = 'PENDENTE'", (id,)
    )
    pendentes = cursor.fetchone()[0]
    if pendentes > 0:
        conn.close()
        flash("Não é possível desligar: funcionário possui EPIs pendentes.", "error")
        return redirect("/listar")
    data_desligamento = datetime.now().strftime("%d/%m/%Y %H:%M")
    cursor.execute(
        "UPDATE funcionarios SET status='DESLIGADO', data_desligamento=? WHERE id=?",
        (data_desligamento, id)
    )
    cursor.execute("SELECT nome FROM funcionarios WHERE id=?", (id,))
    func = cursor.fetchone()
    conn.commit()
    conn.close()
    nome = func["nome"] if func else f"#{id}"
    registrar_log(f"Funcionário '{nome}' desligado", "DESLIGOU", session["user"])
    flash("Funcionário desligado com sucesso.", "info")
    return redirect("/listar")


@app.route("/excluir/<int:id>", methods=["POST"])
def excluir_funcionario(id):
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM funcionarios WHERE id=?", (id,))
    func = cursor.fetchone()
    nome = func["nome"] if func else f"#{id}"
    cursor.execute("DELETE FROM funcionarios WHERE id=?", (id,))
    conn.commit()
    conn.close()
    registrar_log(f"Funcionário '{nome}' excluído permanentemente", "EXCLUIU", session["user"])
    flash(f"Funcionário '{nome}' excluído permanentemente.", "info")
    return redirect("/listar")


@app.route("/exportar_csv")
def exportar_csv():
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM funcionarios ORDER BY id")
    funcionarios = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["ID", "Nome", "Contato", "Setor", "Email", "Cargo", "Salário", "Status", "Data Admissão", "Data Desligamento"])
    for f in funcionarios:
        writer.writerow([f["id"], f["nome"], f["contato"], f["setor"], f["email"], f["cargo"], f["salario"], f["status"], f["data_admissao"], f["data_desligamento"] or ""])

    output.seek(0)
    registrar_log("Lista de funcionários exportada em CSV", "EXPORTOU", session["user"])
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=funcionarios.csv"}
    )


# ===== SETORES =====

@app.route("/setores")
def setores():
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM tabela_setores")
    lista_setores = cursor.fetchall()
    conn.close()
    return render_template("setores.html", setores=lista_setores)


@app.route("/cadastrar_setor", methods=["POST"])
def cadastrar_setor():
    if "user" not in session:
        return redirect("/")
    nome = request.form["nome"]
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO tabela_setores (nome) VALUES (?)", (nome,))
        conn.commit()
        registrar_log(f"Setor '{nome}' cadastrado", "CRIOU SETOR", session["user"])
        flash(f"Setor '{nome}' cadastrado com sucesso!", "success")
    except sqlite3.IntegrityError:
        flash("Erro: este setor já existe.", "error")
    conn.close()
    return redirect("/setores")


@app.route("/excluir_setor/<string:nome>", methods=["POST"])
def excluir_setor(nome):
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM funcionarios WHERE setor = ? AND status = 'ATIVO'", (nome,)
    )
    if cursor.fetchone()[0] > 0:
        conn.close()
        flash("Não é possível excluir: setor possui funcionários ativos.", "error")
        return redirect("/setores")
    cursor.execute("DELETE FROM tabela_setores WHERE nome = ?", (nome,))
    conn.commit()
    conn.close()
    registrar_log(f"Setor '{nome}' excluído", "EXCLUIU SETOR", session["user"])
    flash(f"Setor '{nome}' excluído.", "info")
    return redirect("/setores")


# ===== EPIs E TREINAMENTOS =====

@app.route("/registrar_epi", methods=["POST"])
def registrar_epi():
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO epis (funcionario_id, item, status) VALUES (?, ?, ?)",
        (request.form["funcionario_id"], request.form["item"], request.form.get("status", "PENDENTE"))
    )
    conn.commit()
    conn.close()
    flash("EPI registrado com sucesso!", "success")
    return redirect("/listar")


@app.route("/registrar_treinamento", methods=["POST"])
def registrar_treinamento():
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO treinamentos (funcionario_id, nome_treinamento) VALUES (?, ?)",
        (request.form["funcionario_id"], request.form["nome_treinamento"])
    )
    conn.commit()
    conn.close()
    flash("Treinamento registrado!", "success")
    return redirect("/listar")


# ===== VAGAS E DOCUMENTOS =====

@app.route("/vagas/recrutar", methods=["POST"])
def recrutar():
    if request.form.get("status_rede") == "offline":
        return "Falha na conexão", 503
    return "Candidatos filtrados para esta vaga"


@app.route("/avaliar_desempenho", methods=["POST"])
def avaliar_desempenho():
    return "Avaliação registrada"


@app.route("/upload_documento", methods=["POST"])
def upload_documento():
    nome_arquivo = request.form["nome_arquivo"]
    if ".pdf" not in nome_arquivo.lower():
        return "Documento rejeitado: apenas PDF é aceito.", 400
    return "Documento armazenado"


# ===== LOGS =====

@app.route("/logs")
def logs():
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY id DESC")
    lista_logs = cursor.fetchall()
    conn.close()
    return render_template("logs.html", logs=lista_logs)


@app.route("/limpar_logs", methods=["POST"])
def limpar_logs():
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM logs")
    conn.commit()
    conn.close()
    flash("Logs limpos com sucesso.", "info")
    return redirect("/logs")


# ===== RESUMO E AVISOS =====

@app.route("/resumo")
def resumo():
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM funcionarios")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE status='ATIVO'")
    ativos = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE status='DESLIGADO'")
    desligados = cursor.fetchone()[0]
    conn.close()
    return render_template("resumo.html", total=total, ativos=ativos, desligados=desligados)


@app.route("/avisos", methods=["GET", "POST"])
def avisos():
    if "user" not in session:
        return redirect("/")
    conn = get_db()
    cursor = conn.cursor()
    if request.method == "POST":
        titulo = request.form["titulo"]
        mensagem = request.form["mensagem"]
        data_aviso = datetime.now().strftime("%d/%m/%Y %H:%M")
        cursor.execute(
            "INSERT INTO avisos (titulo, mensagem, autor, data) VALUES (?, ?, ?, ?)",
            (titulo, mensagem, session["user"], data_aviso)
        )
        conn.commit()
        registrar_log(f"Aviso '{titulo}' publicado", "PUBLICOU AVISO", session["user"])
        flash("Aviso publicado!", "success")
    cursor.execute("SELECT * FROM avisos ORDER BY id DESC")
    lista_avisos = cursor.fetchall()
    conn.close()
    return render_template("avisos.html", avisos=lista_avisos)


if __name__ == "__main__":
    app.run(debug=True)
