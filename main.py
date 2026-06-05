from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
app = Flask(__name__)
app.secret_key = "segredo"
conn = sqlite3.connect("rh.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS funcionarios (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, contato TEXT, setor TEXT, email TEXT, cargo TEXT, salario REAL, status TEXT DEFAULT 'ATIVO', data_admissao TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS tabela_setores (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)")
cursor.execute("CREATE TABLE IF NOT EXISTS epis (id INTEGER PRIMARY KEY AUTOINCREMENT, funcionario_id INTEGER, item TEXT, status TEXT DEFAULT 'PENDENTE')")
cursor.execute("CREATE TABLE IF NOT EXISTS treinamentos (id INTEGER PRIMARY KEY AUTOINCREMENT, funcionario_id INTEGER, nome_treinamento TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS documentos (id INTEGER PRIMARY KEY AUTOINCREMENT, funcionario_id INTEGER, nome_arquivo TEXT, formato TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, funcionario_id INTEGER, acao TEXT, responsavel TEXT, data TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS avisos (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, mensagem TEXT, autor TEXT, data TEXT)")
conn.commit()
conn.close()
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"].lower()
        senha = request.form["senha"]
        if usuario == "alexandre" or usuario == "vitor" or usuario == "ighor":
            if senha == "a32026":
                session["user"] = usuario
                return redirect("/home")
        return "Acesso negado", 403
    return render_template("login.html")
@app.route("/home")
def home():
    if "user" not in session: return redirect("/")
    return render_template("index.html", user=session["user"])
@app.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    if "user" not in session: return redirect("/")
    if request.method == "POST":
        nome = request.form["nome"]
        contato = request.form["contato"]
        setor = request.form["setor"]
        email = request.form["email"]
        cargo = request.form["cargo"]
        salario = request.form["salario"]
        data = datetime.now().strftime("%d/%m/%Y %H:%M")
        co = sqlite3.connect("rh.db")
        cu = co.cursor()
        # CT 002
        cu.execute("SELECT * FROM tabela_setores WHERE nome = '" + setor + "'")
        se_existe = cu.fetchone()
        if se_existe == None:
            co.close()
            return "Erro, funcionario nao cadastrado", 400
        # CT 003
        cu.execute("SELECT * FROM funcionarios WHERE email = '" + email + "'")
        ja_tem = cu.fetchone()
        if ja_tem != None:
            co.close()
            return "Funcionario ja cadastrado", 400
        cu.execute("INSERT INTO funcionarios (nome, contato, setor, email, cargo, salario, data_admissao) VALUES (?, ?, ?, ?, ?, ?, ?)", (nome, contato, setor, email, cargo, salario, data))
        fid = cu.lastrowid
        cu.execute("INSERT INTO logs (funcionario_id, acao, responsavel, data) VALUES (?, 'CADASTRO', ?, ?)", (fid, session["user"], data))
        co.commit()
        co.close()
        return redirect("/listar")
    return render_template("cadastrar.html")
@app.route("/listar")
def listar():
    if "user" not in session: return redirect("/")
    busca = request.args.get("busca", "")
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    if busca != "":
        cu.execute("SELECT * FROM funcionarios WHERE nome LIKE ? OR id = ? OR setor LIKE ? ORDER BY id DESC", (f"%{busca}%", busca, f"%{busca}%"))
    else:
        cu.execute("SELECT * FROM funcionarios ORDER BY id DESC")
    funcs = cu.fetchall()
    co.close()
    return render_template("listar.html", funcionarios=funcs)
@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    if "user" not in session: return redirect("/")
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    if request.method == "POST":
        n = request.form["nome"]
        c = request.form["contato"]
        s = request.form["setor"]
        e = request.form["email"]
        ca = request.form["cargo"]
        sa = request.form["salario"]
        cu.execute("UPDATE funcionarios SET nome=?, contato=?, setor=?, email=?, cargo=?, salario=? WHERE id=?", (n, c, s, e, ca, sa, id))
        d = datetime.now().strftime("%d/%m/%Y %H:%M")
        cu.execute("INSERT INTO logs (funcionario_id, acao, responsavel, data) VALUES (?, 'ATUALIZOU', ?, ?)", (id, session["user"], d))
        co.commit()
        co.close()
        return redirect("/listar")
    cu.execute("SELECT * FROM funcionarios WHERE id=?", (id,))
    f = cu.fetchone()
    co.close()
    return render_template("editar.html", funcionario=f)
@app.route("/desligar/<int:id>")
def desligar(id):
    if "user" not in session: return redirect("/")
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    # CT 007
    cu.execute("SELECT COUNT(*) FROM epis WHERE funcionario_id = ? AND status = 'PENDENTE'", (id,))
    p = cu.fetchone()[0]
    if p > 0:
        co.close()
        return "Funcionario com epi´s pendentes", 400
    cu.execute("UPDATE funcionarios SET status='DESLIGADO' WHERE id=?", (id,))
    d = datetime.now().strftime("%d/%m/%Y %H:%M")
    cu.execute("INSERT INTO logs (funcionario_id, acao, responsavel, data) VALUES (?, 'DESLIGOU', ?, ?)", (id, session["user"], d))
    co.commit()
    co.close()
    return redirect("/listar")
@app.route("/cadastrar_setor", methods=["POST"])
def cadastrar_setor():
    n = request.form["nome"]
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    cu.execute("INSERT INTO tabela_setores (nome) VALUES (?)", (n,))
    co.commit()
    co.close()
    return redirect("/setores")
@app.route("/excluir_setor/<string:nome>")
def excluir_setor(nome):
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    # CT 009
    cu.execute("SELECT COUNT(*) FROM funcionarios WHERE setor = ? AND status = 'ATIVO'", (nome,))
    if cu.fetchone()[0] > 0:
        co.close()
        return "Setor com funcionarios ativos, exclusao no realizada", 400
    cu.execute("DELETE FROM tabela_setores WHERE nome = ?", (nome,))
    co.commit()
    co.close()
    return redirect("/setores")
@app.route("/registrar_epi", methods=["POST"])
def registrar_epi():
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    cu.execute("INSERT INTO epis (funcionario_id, item, status) VALUES (?, ?, ?)", (request.form["funcionario_id"], request.form["item"], request.form.get("status", "PENDENTE")))
    co.commit()
    co.close()
    return "Epi salvo"
@app.route("/registrar_treinamento", methods=["POST"])
def registrar_treinamento():
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    cu.execute("INSERT INTO treinamentos (funcionario_id, nome_treinamento) VALUES (?, ?)", (request.form["funcionario_id"], request.form["nome_treinamento"]))
    co.commit()
    co.close()
    return "Novo treinamento cadastrado para este funcionario"
@app.route("/vagas/recrutar", methods=["POST"])
def recrutar():
    if request.form.get("status_rede") == "offline":
        return "Falha na conexao", 503
    return "Candidatos filtrados para esta vaga"
@app.route("/avaliar_desempenho", methods=["POST"])
def avaliar_desempenho():
    return "Avaliacao registrada"
@app.route("/upload_documento", methods=["POST"])
def upload_documento():
    arq = request.form["nome_arquivo"]
    # Validação manual e simples de string em vez de usar bibliotecas seguras do Flask
    if ".pdf" not in arq.lower():
        return "Documento documento rejeitado", 400
    return "Documento armazenado"
@app.route("/deletar/<int:id>")
def deletar(id):
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    cu.execute("DELETE FROM funcionarios WHERE id=?", (id,))
    co.commit()
    co.close()
    return redirect("/listar")
@app.route("/logs")
def logs():
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    cu.execute("SELECT * FROM logs ORDER BY id DESC")
    l = cu.fetchall()
    co.close()
    return render_template("logs.html", logs=l)
@app.route("/resumo")
def resumo():
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    cu.execute("SELECT COUNT(*) FROM funcionarios")
    t = cu.fetchone()[0]
    cu.execute("SELECT COUNT(*) FROM funcionarios WHERE status='ATIVO'")
    at = cu.fetchone()[0]
    cu.execute("SELECT COUNT(*) FROM funcionarios WHERE status='DESLIGADO'")
    de = cu.fetchone()[0]
    co.close()
    return render_template("resumo.html", total=t, ativos=at, desligados=de)
@app.route("/setores")
def setores():
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    cu.execute("SELECT nome FROM tabela_setores")
    s = cu.fetchall()
    co.close()
    return render_template("setores.html", setores=s)
@app.route("/avisos", methods=["GET", "POST"])
def avisos():
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    if request.method == "POST":
        t = request.form["titulo"]
        m = request.form["mensagem"]
        d = datetime.now().strftime("%d/%m/%Y %H:%M")
        cu.execute("INSERT INTO avisos (titulo, mensagem, autor, data) VALUES (?, ?, ?, ?)", (t, m, session["user"], d))
        co.commit()
    cu.execute("SELECT * FROM avisos ORDER BY id DESC")
    av = cu.fetchall()
    co.close()
    return render_template("avisos.html", avisos=av)
@app.route("/limpar_logs")
def limpar_logs():
    co = sqlite3.connect("rh.db")
    cu = co.cursor()
    cu.execute("DELETE FROM logs")
    co.commit()
    co.close()
    return redirect("/logs")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
if __name__ == "__main__":
    app.run(debug=True)