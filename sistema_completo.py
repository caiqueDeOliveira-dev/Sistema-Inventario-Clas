import sqlite3

def inicializar_banco():
    """Cria o banco de dados e as tabelas se elas não existirem."""
    conexao = sqlite3.connect('comunidade.db')
    cursor = conexao.cursor()
    # Ativa o suporte a Chaves Estrangeiras no SQLite
    cursor.execute('PRAGMA foreign_keys = ON;')
    
    # Criação da tabela de Clãs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tag TEXT UNIQUE
        )
    ''')
    
    # Criação da tabela de Membros (Jogadores)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cla_id INTEGER,
            FOREIGN KEY (cla_id) REFERENCES clas (id)
        )
    ''')
    conexao.commit()
    conexao.close()

def cadastrar_cla():
    """Cadastra um novo clã no banco de dados."""
    conexao = sqlite3.connect('comunidade.db')
    cursor = conexao.cursor()
    print('\n--- CADASTRO DE CLÃ ---')
    nome = input('Nome do Clã: ')
    tag = input('Tag do Clã: ')
    
    if not nome or not tag:
        print('[Erro] Os campos não podem ser vazios.')
        conexao.close()
        return

    try:
        cursor.execute('INSERT INTO clas (nome, tag) VALUES (?, ?)', (nome, tag))
        conexao.commit()
        print(f'[Sucesso] Clã "{nome}" ({tag}) cadastrado com sucesso!')
    except sqlite3.IntegrityError:
        print(f'[Erro] A tag "{tag}" já está sendo usada por outro clã!')
    
    conexao.close()

def cadastrar_membro():
    """Cadastra um jogador e vincula a um clã existente."""
    conexao = sqlite3.connect('comunidade.db')
    cursor = conexao.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;') # Garante a checagem do ID
    
    print('\n--- CADASTRO DE JOGADOR ---')
    nome = input('Nome do Jogador: ')
    
    try:
        cla_id = int(input('ID do Clã que ele vai entrar: '))
        cursor.execute('INSERT INTO membros (nome, cla_id) VALUES (?, ?)', (nome, cla_id))
        conexao.commit()
        print(f'[Sucesso] Jogador "{nome}" vinculado ao Clã ID {cla_id}!')
    except ValueError:
        print('[Erro] O ID do clã precisa ser um número inteiro.')
    except sqlite3.IntegrityError:
        print('[Erro] Esse ID de Clã não existe! Cadastre o clã primeiro.')
        
    conexao.close()

def listar_relatorio():
    """Exibe o relatório juntando dados de ambas as tabelas (INNER JOIN)."""
    conexao = sqlite3.connect('comunidade.db')
    cursor = conexao.cursor()
    
    query = '''
        SELECT membros.id, membros.nome, clas.nome, clas.tag 
        FROM membros 
        INNER JOIN clas ON membros.cla_id = clas.id
    '''
    cursor.execute(query)
    resultados = cursor.fetchall()
    
    print('\n=========================================')
    print('      RELATÓRIO DE JOGADORES E CLÃS      ')
    print('=========================================')
    
    if not resultados:
        print('Nenhum jogador cadastrado ou vinculado a clãs ainda.')
    else:
        for r in resultados:
            print(f'ID Jogador: {r[0]} | Nome: {r[1]} -> Clã: {r[2]} ({r[3]})')
            
    print('=========================================\n')
    conexao.close()

def menu():
    """Menu principal interativo do sistema."""
    inicializar_banco()
    while True:
        print('=== SISTEMA DE GERENCIAMENTO DE CLÃS ===')
        print('1. Cadastrar Novo Clã')
        print('2. Cadastrar Novo Jogador (Vincular)')
        print('3. Ver Relatório Completo')
        print('4. Sair do Programa')
        
        opcao = input('Escolha uma opção (1-4): ')
        
        if opcao == '1':
            cadastrar_cla()
        elif opcao == '2':
            cadastrar_membro()
        elif opcao == '3':
            listar_relatorio()
        elif opcao == '4':
            print('Encerrando o sistema... Até mais!')
            break
        else:
            print('[Erro] Opção inválida! Tente novamente.\n')

if __name__ == '__main__':
    menu()