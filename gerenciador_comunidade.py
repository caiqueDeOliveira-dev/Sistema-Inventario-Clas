import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

# ==========================================
# 1. FUNÇÕES DO BANCO DE DADOS (BACKEND)
# ==========================================
def conectar_banco():
    conexao = sqlite3.connect('comunidade.db')
    cursor = conexao.cursor()
    cursor.execute('PRAGMA foreign_keys = ON;')
    return conexao, cursor

def inicializar_sistema():
    conexao, cursor = conectar_banco()
    # Tabela de Clãs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            tag TEXT UNIQUE NOT NULL
        )
    ''')
    # Tabela de Membros
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS membros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cla_id INTEGER,
            FOREIGN KEY (cla_id) REFERENCES clas (id) ON DELETE CASCADE
        )
    ''')
    conexao.commit()
    conexao.close()

# ==========================================
# 2. LÓGICA DE NEGÓCIO / AÇÕES DO APP
# ==========================================
def acao_cadastrar_cla():
    nome = entry_nome_cla.get().strip()
    tag = entry_tag_cla.get().strip()
    
    if not nome or not tag:
        messagebox.showwarning("Aviso", "Preencha todos os campos do Clã!")
        return
    
    try:
        conexao, cursor = conectar_banco()
        cursor.execute('INSERT INTO clas (nome, tag) VALUES (?, ?)', (nome, tag))
        conexao.commit()
        conexao.close()
        messagebox.showinfo("Sucesso", f"Clã '{nome}' [{tag}] criado!")
        entry_nome_cla.delete(0, tk.END)
        entry_tag_cla.delete(0, tk.END)
        atualizar_combobox_clas()
        acao_atualizar_relatorio()
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", f"A TAG '{tag}' já está sendo usada!")

def acao_cadastrar_membro():
    nome = entry_nome_membro.get().strip()
    cla_selecionado = combo_clas.get()
    
    if not nome or not cla_selecionado:
        messagebox.showwarning("Aviso", "Preencha o nome do jogador e selecione um clã!")
        return
    
    # Extrai o ID do clã que está no formato "ID - Nome"
    cla_id = cla_selecionado.split(" - ")[0]
    
    conexao, cursor = conectar_banco()
    cursor.execute('INSERT INTO membros (nome, cla_id) VALUES (?, ?)', (nome, cla_id))
    conexao.commit()
    conexao.close()
    
    messagebox.showinfo("Sucesso", f"Jogador '{nome}' recrutado com sucesso!")
    entry_nome_membro.delete(0, tk.END)
    acao_atualizar_relatorio()

def acao_atualizar_relatorio():
    # Limpa a tabela visual
    for linha in tabela.get_children():
        tabela.delete(linha)
        
    conexao, cursor = conectar_banco()
    query = '''
        SELECT membros.id, membros.nome, clas.nome, clas.tag 
        FROM membros 
        INNER JOIN clas ON membros.cla_id = clas.id
        ORDER BY clas.nome, membros.nome
    '''
    cursor.execute(query)
    for linha in cursor.fetchall():
        tabela.insert("", tk.END, values=(linha[0], linha[1], f"{linha[2]} [{linha[3]}]"))
    conexao.close()

def atualizar_combobox_clas():
    conexao, cursor = conectar_banco()
    cursor.execute('SELECT id, nome, tag FROM clas ORDER BY nome')
    lista = [f"{r[0]} - {r[1]} [{r[2]}]" for r in cursor.fetchall()]
    conexao.close()
    combo_clas['values'] = lista
    if lista:
        combo_clas.current(0)

# ==========================================
# 3. INTERFACE GRÁFICA (ESTILIZAÇÃO DARK)
# ==========================================
inicializar_sistema()

root = tk.Tk()
root.title("HQ Comunidade - Sistema de Gestão de Clãs")
root.geometry("650x500")
root.configure(bg="#121212")

# Customizando o estilo das abas e tabelas
estilo = ttk.Style()
estilo.theme_use("default")
estilo.configure("TNotebook", background="#121212", borderwidth=0)
estilo.configure("TNotebook.Tab", background="#1e1e1e", foreground="#ffffff", padding=[15, 5], font=("Arial", 10, "bold"))
estilo.map("TNotebook.Tab", background=[("selected", "#ff3333")], foreground=[("selected", "#ffffff")])

# Criador de abas (Notebook)
abas = ttk.Notebook(root)
abas.pack(fill="both", expand=True, padx=10, pady=10)

# --- ABA 1: GERENCIAR CLÃS ---
aba_cla = tk.Frame(abas, bg="#1e1e1e")
abas.add(aba_cla, text="🛡️ Novo Clã")

tk.Label(aba_cla, text="CRIAR DIVISÃO / CLÃ", font=("Arial", 14, "bold"), fg="#ff3333", bg="#1e1e1e").pack(pady=20)
tk.Label(aba_cla, text="Nome do Clã:", fg="#ffffff", bg="#1e1e1e", font=("Arial", 11)).pack(pady=5)
entry_nome_cla = tk.Entry(aba_cla, font=("Arial", 12), width=30, bg="#2d2d2d", fg="#ffffff", insertbackground="white", bd=0)
entry_nome_cla.pack(pady=5)

tk.Label(aba_cla, text="Tag do Clã (Ex: CaOS):", fg="#ffffff", bg="#1e1e1e", font=("Arial", 11)).pack(pady=5)
entry_tag_cla = tk.Entry(aba_cla, font=("Arial", 12), width=15, bg="#2d2d2d", fg="#ffffff", insertbackground="white", bd=0)
entry_tag_cla.pack(pady=5)

# CORREÇÃO AQUI: Trocado 'padding=8' por 'padx=10, pady=5'
btn_salvar_cla = tk.Button(aba_cla, text="FUNDAR CLÃ", font=("Arial", 11, "bold"), bg="#ff3333", fg="#ffffff", activebackground="#cc0000", activeforeground="white", bd=0, padx=10, pady=5, command=acao_cadastrar_cla)
btn_salvar_cla.pack(pady=30)

# --- ABA 2: GERENCIAR MEMBROS ---
aba_membros = tk.Frame(abas, bg="#1e1e1e")
abas.add(aba_membros, text="👤 Recrutar Jogador")

tk.Label(aba_membros, text="RECRUTAR NOVO JOGADOR", font=("Arial", 14, "bold"), fg="#ff3333", bg="#1e1e1e").pack(pady=20)
tk.Label(aba_membros, text="Nome do Jogador / Nick:", fg="#ffffff", bg="#1e1e1e", font=("Arial", 11)).pack(pady=5)
entry_nome_membro = tk.Entry(aba_membros, font=("Arial", 12), width=30, bg="#2d2d2d", fg="#ffffff", insertbackground="white", bd=0)
entry_nome_membro.pack(pady=5)

tk.Label(aba_membros, text="Selecionar Clã Alvo:", fg="#ffffff", bg="#1e1e1e", font=("Arial", 11)).pack(pady=5)
combo_clas = ttk.Combobox(aba_membros, font=("Arial", 11), width=28, state="readonly")
combo_clas.pack(pady=5)

# CORREÇÃO AQUI: Trocado 'padding=8' por 'padx=10, pady=5'
btn_salvar_membro = tk.Button(aba_membros, text="VINCULAR AO CLÃ", font=("Arial", 11, "bold"), bg="#ff3333", fg="#ffffff", activebackground="#cc0000", activeforeground="white", bd=0, padx=10, pady=5, command=acao_cadastrar_membro)
btn_salvar_membro.pack(pady=30)

# --- ABA 3: RELATÓRIO GERAL (TABELA) ---
aba_relatorio = tk.Frame(abas, bg="#1e1e1e")
abas.add(aba_relatorio, text="📋 Elenco Atual")

tk.Label(aba_relatorio, text="MEMBROS REGISTRADOS NA COMUNIDADE", font=("Arial", 12, "bold"), fg="#ffffff", bg="#1e1e1e").pack(pady=10)

colunas = ("id", "jogador", "cla")
tabela = ttk.Treeview(aba_relatorio, columns=colunas, show="headings", height=15)
tabela.heading("id", text="ID")
tabela.heading("jogador", text="Jogador")
tabela.heading("cla", text="Clã Associado")

tabela.column("id", width=50, anchor="center")
tabela.column("jogador", width=250, anchor="w")
tabela.column("cla", width=250, anchor="w")
tabela.pack(fill="both", expand=True, padx=10, pady=5)

# CORREÇÃO AQUI: Trocado 'padding=5' por 'padx=10, pady=3'
btn_atualizar = tk.Button(aba_relatorio, text="🔄 Atualizar Lista", font=("Arial", 10, "bold"), bg="#2d2d2d", fg="#ffffff", bd=0, padx=10, pady=3, command=acao_atualizar_relatorio)
btn_atualizar.pack(pady=5)

atualizar_combobox_clas()
acao_atualizar_relatorio()

root.mainloop()