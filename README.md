# 👶 Chá Rifa da Mariana 🎀

Aplicação web completa para gerenciamento de rifa de chá de bebê, desenvolvida com **Streamlit** e integrada ao **Google Sheets**.

![Status](https://img.shields.io/badge/status-concluído-success)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.32.0-red)

---

## 📋 Índice

- [Funcionalidades](#-funcionalidades)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Como Usar](#-como-usar)
- [Estrutura da Planilha](#-estrutura-da-planilha)
- [Solução de Problemas](#-solução-de-problemas)

---

## ✨ Funcionalidades

- 🎯 **Grade 10x10 interativa** com números de 1 a 100
- 🎨 **Tema rosa bebê** personalizado e responsivo
- 🟩 **Verde** = Número disponível
- 🟥 **Vermelho** = Número reservado
- 🟨 **Amarelo** = Número pago
- 📊 **Dashboard em tempo real** com estatísticas
- 🩲 **Classificação automática** de fraldas (P, M, G)
- 🔒 **Proteção contra reserva duplicada**
- 📱 **Formulário modal** para nome e telefone
- 🎉 **Animações** de balões ao reservar
- ♻️ **Auto-refresh** dos dados (cache de 10s)

---

## 🛠️ Pré-requisitos

- Python 3.8 ou superior
- Conta no Google (para Google Sheets)
- Projeto no Google Cloud Console

---

## 📥 Instalação

### 1. Clone ou baixe o projeto

```bash
cd D:\Documentos\APPS_JONAS\CHA-RIFA
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração

### Passo 1: Criar Planilha no Google Sheets

1. Acesse [Google Sheets](https://sheets.google.com)
2. Crie uma nova planilha chamada "Chá Rifa da Mariana"
3. Copie o **ID da planilha** da URL:
   ```
   https://docs.google.com/spreadsheets/d/SEU_ID_AQUI/edit
                                      ^^^^^^^^^^^^^^^
   ```

### Passo 2: Configurar Google Cloud

1. Acesse o [Google Cloud Console](https://console.cloud.google.com)
2. Crie um **novo projeto** (ex: "cha-rifa-mariana")
3. Ative a **Google Sheets API**:
   - Menu ☰ → APIs & Services → Library
   - Pesquise "Google Sheets API" → Enable

### Passo 3: Criar Service Account

1. Menu ☰ → APIs & Services → Credentials
2. **Create Credentials** → Service Account
3. Preencha:
   - **Nome:** cha-rifa-service
   - **Descrição:** Serviço para rifa do chá de bebê
4. Clique em **Create and Continue**
5. Pule a etapa de roles (não é necessário)
6. Clique em **Done**

### Passo 4: Gerar Chave JSON

1. Na lista de Service Accounts, clique na criada
2. Aba **Keys** → **Add Key** → **Create new key**
3. Selecione **JSON** → **Create**
4. Um arquivo JSON será baixado

### Passo 5: Compartilhar Planilha

1. Abra sua planilha no Google Sheets
2. Clique em **Compartilhar** (canto superior direito)
3. Adicione o **email da Service Account** (ex: `cha-rifa@project.iam.gserviceaccount.com`)
4. Dê permissão de **Editor**

### Passo 6: Configurar secrets.toml

Edite o arquivo `.streamlit/secrets.toml`:

```toml
spreadsheet_id = "COLE_SEU_ID_AQUI"

[service_account]
# Copie TODO o conteúdo do JSON baixado aqui
type = "service_account"
project_id = "..."
private_key_id = "..."
# ... (todas as outras chaves)
```

---

## 🚀 Como Usar

### Iniciar a aplicação (ADMIN - com reservas)

```bash
streamlit run app.py
```

A aplicação abrirá automaticamente no seu navegador em `http://localhost:8501`

### Iniciar a tela de VISUALIZAÇÃO (CLIENTE - apenas consulta)

```bash
streamlit run view.py --server.port 8503
```

A tela de visualização abrirá em `http://localhost:8503`

> **Dica:** Use a tela de visualização para enviar o link às clientes que querem apenas ver os números disponíveis!

### Fluxo de Uso

1. **Visualizar grade:** Números disponíveis em verde
2. **Clicar em número verde:** Abre modal de reserva
3. **Preencher nome e telefone:** Confirmar reserva
4. **Número fica vermelho:** Status "Reservado"
5. **Ao confirmar pagamento:** Clique no número vermelho → Marcar como pago
6. **Número fica amarelo:** Status "Pago"

---

## 📊 Estrutura da Planilha

A planilha terá automaticamente as seguintes colunas:

| Número | Nome       | Telefone       | Status    |
|--------|------------|----------------|-----------|
| 1      | João       | (11) 99999-9999| Reservado |
| 2      | Disponível |                | Disponível|
| 3      | Maria      | (11) 98888-8888| Pago      |

### Tamanhos de Fralda

| Números  | Tamanho |
|----------|---------|
| 1 - 20   | P       |
| 21 - 55  | M       |
| 56 - 100 | G       |

---

## 🔧 Solução de Problemas

### ❌ "Erro ao conectar à planilha"

- Verifique se o `spreadsheet_id` está correto
- Confirme que a planilha está compartilhada com a Service Account
- Verifique se a Google Sheets API está ativa

### ❌ "Erro de autenticação"

- Verifique se o JSON da Service Account está completo no `secrets.toml`
- Confirme que a chave não expirou
- Gere uma nova chave se necessário

### ❌ "Número já está reservado"

- O sistema tem proteção contra race conditions
- Atualize a página (F5) para ver o status mais recente
- Outro usuário pode ter reservado simultaneamente

### ❌ Aplicação não inicia

```bash
# Verifique a instalação das dependências
pip install -r requirements.txt

# Verifique a versão do Python
python --version  # Deve ser 3.8+
```

---

## 📁 Estrutura do Projeto

```
CHA-RIFA/
├── app.py                 # Aplicação principal
├── requirements.txt       # Dependências Python
├── README.md             # Este arquivo
├── .streamlit/
│   └── secrets.toml      # Configurações (NÃO COMPARTILHE!)
└── .gitignore            # Arquivos ignorados pelo git
```

---

## 🎨 Cores e Estética

| Elemento     | Cor                  |
|--------------|----------------------|
| Fundo        | #fff5f7 → #ffe4e6    |
| Disponível   | #a8e6cf → #dcedc1    |
| Reservado    | #ff6b6b → #ff8e8e    |
| Pago         | #ffd93d → #ffed4e    |
| Botões       | #ff9aa2 → #ffb7b2    |
| Títulos      | #ff6b8a              |

---

## 📞 Suporte

Para dúvidas ou problemas, abra uma issue no repositório do projeto.

---

**Desenvolvido com 💕 para o Chá Rifa da Mariana**
