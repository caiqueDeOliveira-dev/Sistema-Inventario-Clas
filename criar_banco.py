import sqlite3
conexao = sqlite3.connect('comunidade.db')
cursor = conexao.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS clas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, tag TEXT UNIQUE)')
cursor.execute('CREATE TABLE IF NOT EXISTS membros (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, cla_id INTEGER, FOREIGN KEY (cla_id) REFERENCES clas (id))')
conexao.commit()
conexao.close()
print('Banco de dados e tabelas criados com sucesso!')