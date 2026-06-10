import sqlite3
import tkinter as tk
from tkinter import messagebox

# === 1. LOGICA DO BANCO DE DADOS (Igual ao que você já fez) ===
def inicializar_banco():
    conexao = sqlite3.connect('comunidade.db')
    cursor = conexao.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS clas (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT NOT NULL, tag TEXT UNIQUE)')
    conexao.commit()
    conexao.close()

def salvar_cla_no_banco(nome, tag):
    if not nome or not tag:
        messagebox.showerror("Erro", "Todos os campos devem ser preenchidos!")
        return
    
    try:
        conexao = sqlite3.connect('comunidade.db')
        cursor = conexao.cursor()
        cursor.execute('INSERT INTO clas (nome, tag) VALUES (?, ?)', (nome, tag))
        conexao.commit()
        conexao.close()
        messagebox.showinfo("Sucesso", f"Clã '{nome}' cadastrado com sucesso!")
        # Limpa os campos após cadastrar
        campo_nome.delete(0, tk.END)
        campo_tag.delete(0, tk.END)
    except sqlite3.IntegrityError:
        messagebox.showerror("Erro", f"A tag '{tag}' já está em uso!")

# === 2. CONSTRUÇÃO DA INTERFACE VISUAL ===
inicializar_banco()

# Cria a janela principal
janela = tk.Tk()
janela.title("Gerenciador de Clãs")
janela.geometry("400x300")
janela.configure(bg="#212529") # Fundo escuro estilizado

# Título da Tela
titulo = tk.Label(janela, text="CADASTRO DE CLÃ", font=("Arial", 16, "bold"), fg="#ffffff", bg="#212529")
titulo.pack(pady=20)

# Campo: Nome do Clã
label_nome = tk.Label(janela, text="Nome do Clã:", font=("Arial", 10), fg="#cccccc", bg="#212529")
label_nome.pack()
campo_nome = tk.Entry(janela, font=("Arial", 12), width=30)
campo_nome.pack(pady=5)

# Campo: Tag do Clã
label_tag = tk.Label(janela, text="Tag do Clã:", font=("Arial", 10), fg="#cccccc", bg="#212529")
label_tag.pack()
campo_tag = tk.Entry(janela, font=("Arial", 12), width=30)
campo_tag.pack(pady=5)

# Botão Salvar (Dispara a função de salvar passando o que o usuário digitou)
botao_salvar = tk.Button(
    janela, 
    text="Cadastrar Clã", 
    font=("Arial", 11, "bold"), 
    fg="#ffffff", 
    bg="#198754", # Botão verde estilo Bootstrap
    command=lambda: salvar_cla_no_banco(campo_nome.get(), campo_tag.get())
)
botao_salvar.pack(pady=20)

# Mantém a janela aberta e rodando
janela.mainloop()