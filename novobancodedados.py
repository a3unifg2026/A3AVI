import sqlite3
conn = sqlite3.connect("rh.db")
cursor = conn.cursor()
cursor.execute("ALTER TABLE funcionarios ADD COLUMN email TEXT")
cursor.execute("ALTER TABLE funcionarios ADD COLUMN cargo TEXT")
conn.commit()
conn.close()
print("Banco atualizado com sucesso.")