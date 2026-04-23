import sqlite3
from datetime import datetime

# =========================
# BANCO DE DADOS
# =========================
conn = sqlite3.connect("rh.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS funcionarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
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

usuario_logado = None

# =========================
# LOG
# =========================
def registrar_log(func_id, acao):
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO logs (funcionario_id, acao, responsavel, data)
    VALUES (?, ?, ?, ?)
    """, (func_id, acao, usuario_logado, data))

# =========================
# LOGIN
# =========================
def login():
    global usuario_logado

    admins = ["alexandre", "vitor", "ighor"]
    senha_correta = "a32026"

    usuario = input("Usuário: ").strip().lower()
    senha = input("Senha: ").strip()

    if usuario in admins and senha == senha_correta:
        usuario_logado = usuario.capitalize()
        print(f"\nBem-vindo, {usuario_logado}!")
        return True
    else:
        print("\nAcesso negado.")
        return False

# =========================
# FORMATAR FUNCIONÁRIO
# =========================
def mostrar_funcionario(f):
    print("\n--- Funcionário ---")
    print(f"ID: {f[0]} | Nome: {f[1]} | Status: {f[5]}")
    print(f"Setor: {f[3]} | Salário: R$ {f[4]:.2f}")
    print(f"Contato: {f[2]} | Admissão: {f[6]}")
    print("--------------------")

# =========================
# CADASTRAR
# =========================
def cadastrar():
    nome = input("Nome: ").strip()
    if not nome:
        print("Nome não pode ser vazio.")
        return

    contato = input("Contato: ")
    setor = input("Setor/Cargo: ")

    try:
        salario = float(input("Salário: "))
    except ValueError:
        print("Salário inválido.")
        return

    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO funcionarios (nome, contato, setor, salario, data_admissao)
    VALUES (?, ?, ?, ?, ?)
    """, (nome, contato, setor, salario, data))

    func_id = cursor.lastrowid
    registrar_log(func_id, f"CADASTRO de {nome}")

    conn.commit()
    print(f"Funcionário {nome} cadastrado com ID {func_id}!")

# =========================
# CONSULTAR
# =========================
def consultar():
    try:
        id_func = int(input("ID do funcionário: "))
    except ValueError:
        print("ID inválido.")
        return

    cursor.execute("SELECT * FROM funcionarios WHERE id = ?", (id_func,))
    f = cursor.fetchone()

    if f:
        mostrar_funcionario(f)
    else:
        print("Funcionário não encontrado.")

# =========================
# LISTAR TODOS
# =========================
def listar_todos():
    cursor.execute("SELECT * FROM funcionarios ORDER BY id ASC")
    funcionarios = cursor.fetchall()

    if not funcionarios:
        print("Nenhum funcionário cadastrado.")
        return

    for f in funcionarios:
        mostrar_funcionario(f)

# =========================
# ATUALIZAR
# =========================
def atualizar():
    try:
        id_func = int(input("ID para atualizar: "))
    except ValueError:
        print("ID inválido.")
        return

    cursor.execute("SELECT * FROM funcionarios WHERE id = ?", (id_func,))
    f = cursor.fetchone()

    if not f:
        print("Funcionário não encontrado.")
        return

    if f[5] == "DESLIGADO":
        print("Funcionário já está desligado. Não pode ser editado.")
        return

    print(f"Editando: {f[1]}")

    nome = input("Novo nome (Enter para manter): ") or f[1]
    contato = input("Novo contato (Enter para manter): ") or f[2]
    setor = input("Novo setor (Enter para manter): ") or f[3]

    salario_str = input("Novo salário (Enter para manter): ")

    try:
        salario = float(salario_str) if salario_str else f[4]
    except ValueError:
        print("Salário inválido.")
        return

    cursor.execute("""
    UPDATE funcionarios
    SET nome=?, contato=?, setor=?, salario=?
    WHERE id=?
    """, (nome, contato, setor, salario, id_func))

    registrar_log(id_func, f"ATUALIZAÇÃO por {usuario_logado}")

    conn.commit()
    print("Dados atualizados com sucesso!")

# =========================
# DESLIGAMENTO
# =========================
def desligar():
    try:
        id_func = int(input("ID para desligamento: "))
    except ValueError:
        print("ID inválido.")
        return

    cursor.execute("SELECT * FROM funcionarios WHERE id = ?", (id_func,))
    f = cursor.fetchone()

    if not f:
        print("Funcionário não encontrado.")
        return

    if f[5] == "DESLIGADO":
        print("Funcionário já está desligado.")
        return

    motivo = input("Motivo do desligamento: ")

    cursor.execute("UPDATE funcionarios SET status='DESLIGADO' WHERE id=?", (id_func,))
    registrar_log(id_func, f"DESLIGAMENTO: {motivo}")

    conn.commit()
    print(f"Funcionário {f[1]} desligado com sucesso.")

# =========================
# MOSTRAR LOGS
# =========================
def mostrar_logs():
    cursor.execute("SELECT * FROM logs ORDER BY id ASC")
    logs = cursor.fetchall()

    if not logs:
        print("Nenhum log registrado.")
        return

    print("\n--- LOGS ---")
    for log in logs:
        print(f"Func ID {log[1]} | {log[2]} | Por: {log[3]} | Data: {log[4]}")
    print("-------------")

# =========================
# LOGS POR FUNCIONÁRIO
# =========================
def logs_por_funcionario():
    try:
        id_func = int(input("ID do funcionário: "))
    except ValueError:
        print("ID inválido.")
        return

    cursor.execute("SELECT * FROM logs WHERE funcionario_id=? ORDER BY id ASC", (id_func,))
    logs = cursor.fetchall()

    if not logs:
        print("Nenhum log encontrado para esse funcionário.")
        return

    for log in logs:
        print(f"{log[2]} | Por: {log[3]} | Data: {log[4]}")

# =========================
# RESUMO
# =========================
def resumo():
    cursor.execute("SELECT COUNT(*) FROM funcionarios")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE status='ATIVO'")
    ativos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE status='DESLIGADO'")
    desligados = cursor.fetchone()[0]

    print("\n--- RESUMO ---")
    print(f"Total: {total}")
    print(f"Ativos: {ativos}")
    print(f"Desligados: {desligados}")
    print("----------------")

# =========================
# MENU
# =========================
def menu():
    while True:
        print("\n--- PAINEL RH IACorp ---")
        print("1 - Cadastrar Funcionário")
        print("2 - Consultar por ID")
        print("3 - Listar Todos")
        print("4 - Atualizar Cadastro")
        print("5 - Desligar Funcionário")
        print("6 - Ver Logs")
        print("7 - Logs por Funcionário")
        print("8 - Ver Resumo")
        print("9 - Sair")

        op = input("Escolha: ")

        if op == "1": cadastrar()
        elif op == "2": consultar()
        elif op == "3": listar_todos()
        elif op == "4": atualizar()
        elif op == "5": desligar()
        elif op == "6": mostrar_logs()
        elif op == "7": logs_por_funcionario()
        elif op == "8": resumo()
        elif op == "9": break
        else: print("Opção inválida.")

# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    try:
        if login():
            menu()
    finally:
        conn.close()