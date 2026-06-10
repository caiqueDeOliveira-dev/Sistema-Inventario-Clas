# Sistema de Gerenciamento de Comunidades (Tropa do CaOS)

Este software é uma solução robusta de gerenciamento de clãs e comunidades, focada em organização de membros, auditoria de sorteios e automação de relatórios via Discord Webhooks.

## 🚀 Funcionalidades
- **Gestão de Elenco:** Cadastro, remoção e busca em tempo real.
- **Auditoria:** Histórico completo de sorteios com persistência em SQLite.
- **Automação:** Disparo automático de relatórios formatados para canais do Discord.
- **Segurança:** Uso de variáveis de ambiente (`.env`) para proteção de tokens de API.

## 🛠️ Tecnologias Utilizadas
- **Linguagem:** Python 3.14
- **Interface:** Tkinter (GUI)
- **Banco de Dados:** SQLite3
- **Integração:** `requests` para comunicação com a API do Discord
- **Configuração:** `python-dotenv` para gestão de variáveis de ambiente

## ⚙️ Como Instalar
1. Clone o repositório.
2. Crie um ambiente virtual: `python -m venv .venv`
3. Ative o ambiente e instale as dependências:
   ```bash
   pip install -r requirements.txt

   ## 📸 Visual do Projeto

**Interface Principal:**
![Interface Principal](assets/dashboard_main.png)

**Painel de Gestão:**
![Painel de Gestão](assets/painel_cla.png)