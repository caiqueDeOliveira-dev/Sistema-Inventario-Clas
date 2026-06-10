import sqlite3
import random
import os 
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
from datetime import datetime
import requests
from dotenv import load_dotenv 

# --- CARREGAMENTO SILENCIOSO E SEGURO DO .ENV ---
# O Python apenas lê o arquivo nos bastidores de forma direta, sem avisos na tela
caminho_atual = os.path.dirname(os.path.abspath(__file__))
caminho_env = os.path.join(caminho_atual, '.env')
load_dotenv(dotenv_path=caminho_env)
# -----------------------------------------------

# ==========================================
# 1. CAMADA DE DADOS (BACKEND / BANCO)
# ==========================================
class BancoDados:
    @staticmethod
    def conectar():
        conn = sqlite3.connect('comunidade_v2.db')
        cursor = conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON;')
        return conn, cursor

    @staticmethod
    def inicializar():
        conn, cursor = BancoDados.conectar()
        cursor.execute('''CREATE TABLE IF NOT EXISTS clas 
                       (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, tag TEXT UNIQUE)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS membros 
                       (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, cargo TEXT, cla_id INTEGER, 
                       FOREIGN KEY(cla_id) REFERENCES clas(id) ON DELETE CASCADE)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS historico_sorteios 
                       (id INTEGER PRIMARY KEY AUTOINCREMENT, cla_id INTEGER, ganhador TEXT, data_hora TEXT,
                        FOREIGN KEY(cla_id) REFERENCES clas(id) ON DELETE CASCADE)''')
        conn.commit()
        conn.close()

# ==========================================
# 2. SUB-TELA: DASHBOARD INTERNO DO CLÃ
# ==========================================
class DashboardCla:
    def __init__(self, root_parent, cla_id, cla_nome):
        self.cla_id = cla_id
        self.cla_nome = cla_nome
        
        # Puxa a URL que está guardada em segurança no arquivo .env
        self.DISCORD_WEBHOOK_URL = os.getenv("DISCORD_URL")
        
        self.dash = tk.Toplevel(root_parent)
        self.dash.title(f"Dashboard - {cla_nome}")
        self.dash.geometry("800x670")
        self.dash.configure(bg="#121212")

        tk.Label(self.dash, text=f"PAINEL DE CONTROLE: {cla_nome}", font=("Arial", 16, "bold"), fg="#ff3333", bg="#121212").pack(pady=15)

        self.abas_dash = ttk.Notebook(self.dash)
        self.abas_dash.pack(fill="both", expand=True, padx=10, pady=10)

        self.configurar_aba_elenco()
        self.configurar_aba_sorteio()
        
        self.carregar_elenco()
        self.carregar_historico_sorteios()

    def configurar_aba_elenco(self):
        self.aba_elenco = tk.Frame(self.abas_dash, bg="#1e1e1e")
        self.abas_dash.add(self.aba_elenco, text="👥 Elenco")

        # Barra de Busca
        frame_busca = tk.Frame(self.aba_elenco, bg="#1e1e1e")
        frame_busca.pack(fill="x", padx=20, pady=10)
        tk.Label(frame_busca, text="🔍 Buscar Jogador:", fg="#ffffff", bg="#1e1e1e", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))
        self.ent_busca = tk.Entry(frame_busca, font=("Arial", 11), bg="#2d2d2d", fg="#ffffff", bd=0, insertbackground="white")
        self.ent_busca.pack(side="left", fill="x", expand=True, ipady=3)
        self.ent_busca.bind("<KeyRelease>", self.filtrar_jogadores)

        # Listas de Exibição
        tk.Label(self.aba_elenco, text="⭐ LIDERANÇA", fg="#ffcc00", bg="#1e1e1e", font=("Arial", 10, "bold")).pack(pady=5)
        self.lista_lideres = tk.Listbox(self.aba_elenco, height=5, bg="#2d2d2d", fg="#ffffff", font=("Arial", 11), bd=0)
        self.lista_lideres.pack(fill="x", padx=20)

        tk.Label(self.aba_elenco, text="⚔️ MEMBROS", fg="#ffffff", bg="#1e1e1e", font=("Arial", 10, "bold")).pack(pady=5)
        self.lista_membros = tk.Listbox(self.aba_elenco, height=8, bg="#2d2d2d", fg="#ffffff", font=("Arial", 11), bd=0)
        self.lista_membros.pack(fill="x", padx=20)

        # Barra de Ações
        frame_botoes = tk.Frame(self.aba_elenco, bg="#1e1e1e")
        frame_botoes.pack(fill="x", padx=20, pady=15)

        btn_excluir = tk.Button(frame_botoes, text="❌ EXCLUIR", bg="#cc0000", fg="white", font=("Arial", 9, "bold"), pady=8, bd=0, command=self.excluir_membro)
        btn_excluir.pack(side="left", fill="x", expand=True, padx=(0, 2))

        btn_exportar = tk.Button(frame_botoes, text="📥 BAIXAR .TXT", bg="#333", fg="white", font=("Arial", 9, "bold"), pady=8, bd=0, command=self.exportar_relatorio)
        btn_exportar.pack(side="left", fill="x", expand=True, padx=2)

        btn_discord = tk.Button(frame_botoes, text="🚀 ENVIAR P/ DISCORD", bg="#5865F2", fg="white", font=("Arial", 9, "bold"), pady=8, bd=0, command=self.enviar_para_discord)
        btn_discord.pack(side="left", fill="x", expand=True, padx=(2, 0))

    def configurar_aba_sorteio(self):
        self.aba_sorteio = tk.Frame(self.abas_dash, bg="#1e1e1e")
        self.abas_dash.add(self.aba_sorteio, text="🎁 Sorteio de Itens")

        tk.Label(self.aba_sorteio, text="SORTEIO DE ITENS DA TROPA", font=("Arial", 12, "bold"), fg="#ff3333", bg="#1e1e1e").pack(pady=10)
        self.label_ganhador = tk.Label(self.aba_sorteio, text="Quem será o sortudo?", font=("Arial", 14, "italic"), fg="#ffffff", bg="#1e1e1e")
        self.label_ganhador.pack(pady=15)

        tk.Button(self.aba_sorteio, text="🎰 GERAR GANHADOR", bg="#ff3333", fg="white", font=("Arial", 11, "bold"), padx=15, pady=5, bd=0, command=self.realizar_sorteio).pack()

        tk.Label(self.aba_sorteio, text="📊 HISTÓRICO DE AUDITORIA (ÚLTIMOS SORTEIOS)", font=("Arial", 10, "bold"), fg="#aaa", bg="#1e1e1e").pack(pady=(25, 5))
        
        colunas = ("ganhador", "data_hora")
        self.tabela_historico = ttk.Treeview(self.aba_sorteio, columns=colunas, show="headings", height=6)
        self.tabela_historico.heading("ganhador", text="Jogador Premiado")
        self.tabela_historico.heading("data_hora", text="Data e Hora do Sorteio")
        self.tabela_historico.column("ganhador", width=250, anchor="w")
        self.tabela_historico.column("data_hora", width=250, anchor="center")
        self.tabela_historico.pack(fill="both", expand=True, padx=20, pady=10)

    def filtrar_jogadores(self, event):
        texto_busca = self.ent_busca.get().strip()
        self.carregar_elenco(texto_busca)

    def carregar_elenco(self, pesquisa=""):
        self.lista_lideres.delete(0, tk.END)
        self.lista_membros.delete(0, tk.END)
        self.map_lideres, self.map_membros = {}, {}
        
        conn, cursor = BancoDados.conectar()
        if pesquisa == "":
            cursor.execute("SELECT id, nome, cargo FROM membros WHERE cla_id = ?", (self.cla_id,))
        else:
            cursor.execute("SELECT id, nome, cargo FROM membros WHERE cla_id = ? AND nome LIKE ?", (self.cla_id, f"%{pesquisa}%"))
        
        il, im = 0, 0
        for m_id, nome, cargo in cursor.fetchall():
            if cargo == "Líder":
                self.lista_lideres.insert(tk.END, f"  ♛ {nome}")
                self.map_lideres[il] = (m_id, nome)
                il += 1
            else:
                self.lista_membros.insert(tk.END, f"  • {nome}")
                self.map_membros[im] = (m_id, nome)
                im += 1
        conn.close()

    def carregar_historico_sorteios(self):
        for linha in self.tabela_historico.get_children():
            self.tabela_historico.delete(linha)
        conn, cursor = BancoDados.conectar()
        cursor.execute("SELECT ganhador, data_hora FROM historico_sorteios WHERE cla_id = ? ORDER BY id DESC", (self.cla_id,))
        for ganhador, data_hora in cursor.fetchall():
            self.tabela_historico.insert("", tk.END, values=(ganhador, data_hora))
        conn.close()

    def excluir_membro(self):
        membro_id = None
        m_nome = ""
        if self.lista_lideres.curselection():
            membro_id, m_nome = self.map_lideres[self.lista_lideres.curselection()[0]]
        elif self.lista_membros.curselection():
            membro_id, m_nome = self.map_membros[self.lista_membros.curselection()[0]]

        if not membro_id:
            messagebox.showwarning("Aviso", "Selecione alguém na lista para remover!")
            return

        if messagebox.askyesno("Confirmar", f"Remover {m_nome} do clã?"):
            conn, cursor = BancoDados.conectar()
            cursor.execute("DELETE FROM membros WHERE id = ?", (membro_id,))
            conn.commit()
            conn.close()
            self.carregar_elenco(self.ent_busca.get().strip())

    def gerar_texto_relatorio(self):
        conn, cursor = BancoDados.conectar()
        cursor.execute("SELECT nome, cargo FROM membros WHERE cla_id = ? ORDER BY cargo DESC, nome ASC", (self.cla_id,))
        jogadores = cursor.fetchall()
        conn.close()

        if not jogadores:
            return None

        linhas = [
            f"🏰 **ELENCO OFICIAL: {self.cla_nome.upper()}** 🏰",
            f"📅 *Relatório atualizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}*\n",
            "⭐ **LIDERANÇA:**"
        ]
        
        lideres = [f"👑  {nome}" for nome, cargo in jogadores if cargo == "Líder"]
        linhas.extend(lideres) if lideres else linhas.append("*Nenhum líder definido*")

        linhas.append("\n⚔️ **GUERREIROS / MEMBROS:**")
        membros = [f"•  {nome}" for nome, cargo in jogadores if cargo == "Membro"]
        linhas.extend(membros) if membros else linhas.append("*Nenhum membro recrutado*")
            
        linhas.append(f"\n📊 **Total de Operacionais:** {len(jogadores)} jogadores.")
        return "\n".join(linhas)

    def exportar_relatorio(self):
        texto_final = self.gerar_texto_relatorio()
        if not texto_final:
            messagebox.showwarning("Aviso", "Não há jogadores cadastrados neste clã!")
            return

        caminho_arquivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivo de Texto", "*.txt")],
            initialfile=f"Elenco_{self.cla_nome.replace(' ', '_')}.txt",
            title="Salvar Relatório"
        )

        if caminho_arquivo:
            try:
                with open(caminho_arquivo, "w", encoding="utf-8") as arquivo:
                    arquivo.write(texto_final)
                messagebox.showinfo("Sucesso", "Relatório baixado!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar: {e}")

    def enviar_para_discord(self):
        # Proteção: Alerta amigável caso a variável não exista no arquivo .env
        if not self.DISCORD_WEBHOOK_URL:
            messagebox.showwarning("Configuração Necessária", "Não encontrei a variável 'DISCORD_URL' dentro do arquivo .env!")
            return

        texto_final = self.gerar_texto_relatorio()
        if not texto_final:
            messagebox.showwarning("Aviso", "Não há jogadores cadastrados neste clã para enviar!")
            return

        dados_envio = {"content": texto_final}

        try:
            resposta = requests.post(self.DISCORD_WEBHOOK_URL, json=dados_envio)
            if resposta.status_code == 204:
                messagebox.showinfo("Sucesso!", "O elenco foi disparado para o Discord!")
            else:
                messagebox.showerror("Erro na API", f"O Discord recusou o envio. Código: {resposta.status_code}")
        except Exception as e:
            messagebox.showerror("Falha de Conexão", f"Não foi possível conectar à internet: {e}")

    def realizar_sorteio(self):
        try:
            conn, cursor = BancoDados.conectar()
            cursor.execute("SELECT nome FROM membros WHERE cla_id = ? AND cargo = 'Membro'", (self.cla_id,))
            participantes = [row[0] for row in cursor.fetchall()]

            if not participantes:
                messagebox.showwarning("Aviso", "Sem membros comuns cadastrados para sortear!")
                conn.close()
                return

            ganhador = random.choice(participantes)
            momento_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
            
            cursor.execute("INSERT INTO historico_sorteios (cla_id, ganhador, data_hora) VALUES (?, ?, ?)", 
                           (self.cla_id, ganhador, momento_atual))
            conn.commit()
            conn.close()

            self.label_ganhador.config(text=f"🏆 {ganhador} 🏆", fg="#00ff00", font=("Arial", 20, "bold"))
            self.carregar_historico_sorteios()
            
            if self.DISCORD_WEBHOOK_URL:
                msg_sorteio = f"🎰 **SORTEIO DA TROPA!** 🎰\n🏆 O grande vencedor do item de hoje foi: **{ganhador}**\n*Parabéns!*"
                requests.post(self.DISCORD_WEBHOOK_URL, json={"content": msg_sorteio})

            messagebox.showinfo("SORTEIO FINALIZADO", f"Parabéns! O ganhador foi: {ganhador}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao sortear: {e}")


# ==========================================
# 3. INTERFACE PRINCIPAL (DASHBOARD GENERAL)
# ==========================================
class AppPrincipal:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestão de Comunidade - HQ")
        self.root.geometry("850x600")
        self.root.configure(bg="#121212")
        
        BancoDados.inicializar()
        self.configurar_layout()
        self.atualizar_dados_telas()

    def configurar_layout(self):
        fe = tk.Frame(self.root, bg="#121212", padx=20)
        fe.pack(side="left", fill="y")

        tk.Label(fe, text="🛡️ FUNDAR CLÃ", fg="#ff3333", bg="#121212", font=("Arial", 12, "bold")).pack(pady=10)
        self.ent_nome = tk.Entry(fe, font=("Arial", 10)); self.ent_nome.pack()
        tk.Label(fe, text="Nome do Clã", bg="#121212", fg="#888").pack()
        self.ent_tag = tk.Entry(fe, font=("Arial", 10)); self.ent_tag.pack()
        tk.Label(fe, text="TAG (Única)", bg="#121212", fg="#888").pack()
        tk.Button(fe, text="Criar Divisão", command=self.cadastrar_cla, bg="#ff3333", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

        tk.Label(fe, text="\n👤 RECRUTAR", fg="#ff3333", bg="#121212", font=("Arial", 12, "bold")).pack(pady=10)
        self.ent_nick = tk.Entry(fe, font=("Arial", 10)); self.ent_nick.pack()
        tk.Label(fe, text="Nickname do Jogador", bg="#121212", fg="#888").pack(pady=2)
        
        self.combo_cargo = ttk.Combobox(fe, values=["Membro", "Líder"], state="readonly")
        self.combo_cargo.current(0); self.combo_cargo.pack(pady=2)
        
        self.combo_selecionar_cla = ttk.Combobox(fe, state="readonly")
        self.combo_selecionar_cla.pack(pady=5)
        tk.Button(fe, text="Salvar Recruta", command=self.cadastrar_membro, bg="#ff3333", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

        fd = tk.Frame(self.root, bg="#1e1e1e", padx=20)
        fd.pack(side="right", fill="both", expand=True)

        tk.Label(fd, text="🏰 DIVISÕES ATIVAS DA COMUNIDADE", fg="white", bg="#1e1e1e", font=("Arial", 13, "bold")).pack(pady=20)
        self.lista_main_clas = tk.Listbox(fd, bg="#2d2d2d", fg="white", font=("Arial", 12), bd=0, highlightthickness=0)
        self.lista_main_clas.pack(fill="both", expand=True, pady=10)

        tk.Button(fd, text="⚙️ ENTRAR NO PAINEL DO CLÃ", bg="#ff3333", fg="white", font=("Arial", 11, "bold"), pady=12, bd=0, command=self.entrar_dashboard).pack(fill="x", pady=20)

    def cadastrar_cla(self):
        nome, tag = self.ent_nome.get().strip(), self.ent_tag.get().strip()
        if not nome or not tag:
            messagebox.showwarning("Aviso", "Campos vazios!")
            return
        try:
            conn, cursor = BancoDados.conectar()
            cursor.execute("INSERT INTO clas (nome, tag) VALUES (?,?)", (nome, tag))
            conn.commit()
            conn.close()
            self.ent_nome.delete(0, tk.END); self.ent_tag.delete(0, tk.END)
            self.atualizar_dados_telas()
            messagebox.showinfo("Sucesso", "Novo clã adicionado às fileiras!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Essa TAG já pertence a outra facção.")

    def cadastrar_membro(self):
        nome = self.ent_nick.get().strip()
        cargo = self.combo_cargo.get()
        cla_info = self.combo_selecionar_cla.get()
        if not nome or not cla_info:
            messagebox.showwarning("Aviso", "Selecione o clã e digite o nick!")
            return
        
        cla_id = cla_info.split(" - ")[0]
        conn, cursor = BancoDados.conectar()
        cursor.execute("INSERT INTO membros (nome, cargo, cla_id) VALUES (?,?,?)", (nome, cargo, cla_id))
        conn.commit()
        conn.close()
        self.ent_nick.delete(0, tk.END)
        messagebox.showinfo("Sucesso", f"{nome} agora é {cargo}!")

    def atualizar_dados_telas(self):
        self.lista_main_clas.delete(0, tk.END)
        conn, cursor = BancoDados.conectar()
        cursor.execute("SELECT id, nome, tag FROM clas ORDER BY nome")
        todos_clas = cursor.fetchall()
        
        for r in todos_clas:
            self.lista_main_clas.insert(tk.END, f"{r[0]} - {r[1]} [{r[2]}]")
            
        self.combo_selecionar_cla['values'] = [f"{r[0]} - {r[1]}" for r in todos_clas]
        if todos_clas:
            self.combo_selecionar_cla.current(0)
        conn.close()

    def entrar_dashboard(self):
        selecionado = self.lista_main_clas.get(tk.ACTIVE)
        if selecionado:
            id_cla = selecionado.split(" - ")[0]
            nome_cla = selecionado.split(" - ")[1]
            DashboardCla(self.root, id_cla, nome_cla)

if __name__ == "__main__":
    janela_raiz = tk.Tk()
    app = AppPrincipal(janela_raiz)
    janela_raiz.mainloop()