"""
👶 Chá Rifa da Mariana - Aplicação de Gerenciamento de Rifa
🎀 Aplicação Streamlit completa para gestão de rifa de chá de bebê
"""

# -*- coding: utf-8 -*-
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import re

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="👶 Chá Rifa da Mariana",
    page_icon="🎀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CSS CUSTOMIZADO - TEMA ROSA BEBÊ
# ============================================================================
CUSTOM_CSS = """
<style>
/* Fundo principal - Gradiente Rosa Bebê */
.main {
    background: linear-gradient(135deg, #fff5f7 0%, #ffe4e6 100%);
    min-height: 100vh;
}

/* Títulos com Comic Sans */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Comic Sans MS', 'Comic Sans', cursive !important;
    color: #ff6b8a;
}

/* Header principal */
.stApp > header {
    background: linear-gradient(45deg, #ff9aa2, #ffb7b2);
    box-shadow: 0 4px 20px rgba(255,154,162,0.3);
}

/* Botões personalizados */
.stButton > button {
    background: linear-gradient(45deg, #ff9aa2, #ffb7b2);
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(255,154,162,0.4);
    border: none;
    padding: 10px 20px;
    font-weight: bold;
    color: white;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(255,154,162,0.6);
}

/* Botões da grade - Disponíveis */
.available {
    background: linear-gradient(45deg, #a8e6cf, #dcedc1) !important;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(168,230,207,0.4);
}

/* Botões da grade - Reservados */
.reserved {
    background: linear-gradient(45deg, #ff6b6b, #ff8e8e) !important;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(255,107,107,0.4);
}

/* Botões da grade - Pagos */
.paid {
    background: linear-gradient(45deg, #ffd93d, #ffed4e) !important;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(255,217,61,0.4);
}

/* Cards do dashboard */
.metric-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(255,154,162,0.2);
    text-align: center;
}

/* Modal customizado */
.stModal {
    background: linear-gradient(135deg, #fff5f7 0%, #ffe4e6 100%);
    border-radius: 20px;
}

/* Inputs - Texto escuro para melhor contraste */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    border-radius: 10px;
    border: 2px solid #ffb7b2;
    background: white;
    color: #333333 !important;
}

.stTextInput label,
.stNumberInput label {
    color: #ff6b8a !important;
    font-weight: bold;
}

/* Selectbox - Texto escuro */
.stSelectbox > div > div {
    border-radius: 10px;
    border: 2px solid #ffb7b2;
    background: white;
    color: #333333 !important;
}

.stSelectbox label {
    color: #ff6b8a !important;
    font-weight: bold;
}

/* Divider rosa */
hr {
    border-color: #ffb7b2 !important;
}

/* Esconder footer do Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================================
# CONFIGURAÇÃO DO GOOGLE SHEETS
# ============================================================================

# IDs e credenciais - substitua pelos seus valores
SPREADSHEET_ID = st.secrets.get("spreadsheet_id", "SUA_PLANILHA_ID_AQUI")
SERVICE_ACCOUNT_INFO = st.secrets.get("service_account", None)


@st.cache_resource
def get_gspread_client():
    """
    Inicializa o cliente do Google Sheets com cache.
    """
    if SERVICE_ACCOUNT_INFO:
        credentials = Credentials.from_service_account_info(
            SERVICE_ACCOUNT_INFO,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        return gspread.authorize(credentials)
    return None


@st.cache_data(ttl=10)
def get_sheet_data(spreadsheet_id):
    """
    Busca dados da planilha com cache de 10 segundos.
    Retorna lista de dicionários com os dados.
    """
    try:
        client = get_gspread_client()
        if client is None:
            return None

        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1

        # Buscar todos os dados
        all_records = worksheet.get_all_records()

        # Garantir que todos os números de 1 a 100 existam
        existing_numbers = {int(r.get('Número', 0)) for r in all_records if r.get('Número')}

        for num in range(1, 101):
            if num not in existing_numbers:
                all_records.append({
                    'Número': num,
                    'Nome': 'Disponível',
                    'Telefone': '',
                    'Status': 'Disponível'
                })

        return all_records

    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
        return None


def initialize_sheet(spreadsheet_id):
    """
    Inicializa a estrutura da planilha se estiver vazia.
    """
    try:
        client = get_gspread_client()
        if client is None:
            return False, "Cliente do Google Sheets não inicializado"

        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1

        # Verificar se está vazia
        existing_data = worksheet.get_all_values()

        if len(existing_data) <= 1:  # Apenas header ou vazia
            # Criar header
            worksheet.append_row(['Número', 'Nome', 'Telefone', 'Status'])

            # Criar 100 números como disponíveis
            for num in range(1, 101):
                worksheet.append_row([num, 'Disponível', '', 'Disponível'])

            return True, "Planilha inicializada com sucesso!"

        return True, "Planilha já possui dados"

    except Exception as e:
        return False, f"Erro ao inicializar: {str(e)}"


def update_sheet_entry(spreadsheet_id, number, name, phone, status):
    """
    Atualiza uma entrada na planilha.
    """
    try:
        client = get_gspread_client()
        if client is None:
            return False, "Cliente não inicializado"

        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1

        # Encontrar a linha do número
        all_data = worksheet.get_all_values()

        for idx, row in enumerate(all_data, start=1):
            if idx > 0 and str(row[0]) == str(number):
                # Atualizar a linha
                worksheet.update(f'B{idx}', name)
                worksheet.update(f'C{idx}', phone)
                worksheet.update(f'D{idx}', status)
                return True, "Atualizado com sucesso!"

        # Se não encontrou, adicionar nova linha
        worksheet.append_row([number, name, phone, status])
        return True, "Adicionado com sucesso!"

    except Exception as e:
        return False, f"Erro: {str(e)}"


def reserve_number(spreadsheet_id, number, name, phone):
    """
    Reserva um número com verificação de lock para evitar race conditions.
    """
    # Refresh dos dados para verificar estado atual
    st.cache_data.clear()
    current_data = get_sheet_data(spreadsheet_id)

    if current_data is None:
        return False, "Erro ao verificar status atual"

    # Verificar se o número está realmente disponível
    for entry in current_data:
        if int(entry.get('Número', 0)) == number:
            status = entry.get('Status', 'Disponível')
            if status != 'Disponível':
                return False, f"Número {number} já está {status}!"
            break

    # Proceder com reserva
    return update_sheet_entry(spreadsheet_id, number, name, phone, 'Reservado')


def mark_as_paid(spreadsheet_id, number):
    """
    Marca um número como pago.
    """
    st.cache_data.clear()
    current_data = get_sheet_data(spreadsheet_id)

    if current_data is None:
        return False, "Erro ao verificar status atual"

    # Encontrar dados atuais
    current_name = "Desconhecido"
    current_phone = ""

    for entry in current_data:
        if int(entry.get('Número', 0)) == number:
            current_name = entry.get('Nome', 'Desconhecido')
            current_phone = entry.get('Telefone', '')
            break

    return update_sheet_entry(spreadsheet_id, number, current_name, current_phone, 'Pago')


def get_fralda_size(number):
    """
    Determina o tamanho da fralda baseado no número.
    1-20 = P, 21-55 = M, 56-100 = G
    """
    if 1 <= number <= 20:
        return "P"
    elif 21 <= number <= 55:
        return "M"
    else:
        return "G"


# ============================================================================
# HEADER PRINCIPAL
# ============================================================================
st.title("👶 Chá Rifa da Mariana 🎀")
st.markdown("### 🎉 Ajude a mamãe a preparar o enxoval do bebê!")
st.markdown("---")

# ============================================================================
# INICIALIZAÇÃO DA PLANILHA (botão na sidebar)
# ============================================================================
with st.sidebar:
    st.header("⚙️ Configurações")

    if st.button("📋 Inicializar Planilha", use_container_width=True):
        with st.spinner("Inicializando planilha..."):
            success, message = initialize_sheet(SPREADSHEET_ID)
            if success:
                st.success(message)
                st.cache_data.clear()
            else:
                st.error(message)

    st.markdown("---")
    st.info("💡 Clique em um número **verde** para reservar!")
    st.markdown("---")
    st.markdown("**Legenda:**")
    st.markdown("🟩 Verde = Disponível")
    st.markdown("🟥 Vermelho = Reservado")
    st.markdown("🟨 Amarelo = Pago")

# ============================================================================
# DASHBOARD - SIDEBAR COM ESTATÍSTICAS
# ============================================================================
# Buscar dados atualizados
sheet_data = get_sheet_data(SPREADSHEET_ID)

if sheet_data is None:
    st.warning("⚠️ Não foi possível conectar à planilha. Verifique as credenciais.")
    st.stop()

# Calcular estatísticas
total_numeros = 100
disponiveis = sum(1 for e in sheet_data if e.get('Status') == 'Disponível')
reservados = sum(1 for e in sheet_data if e.get('Status') == 'Reservado')
pagos = sum(1 for e in sheet_data if e.get('Status') == 'Pago')

# Exibir dashboard na sidebar
with st.sidebar:
    st.header("📊 Dashboard")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #a8e6cf; margin: 0;">{total_numeros}</h3>
            <p style="margin: 0; font-size: 12px;">Total</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #a8e6cf; margin: 0;">{disponiveis}</h3>
            <p style="margin: 0; font-size: 12px;">Disponíveis</p>
        </div>
        """, unsafe_allow_html=True)

    col3, col4 = st.columns(2)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ff6b6b; margin: 0;">{reservados}</h3>
            <p style="margin: 0; font-size: 12px;">Reservados</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ffd93d; margin: 0;">{pagos}</h3>
            <p style="margin: 0; font-size: 12px;">Pagos</p>
        </div>
        """, unsafe_allow_html=True)

    # Barra de progresso
    progresso = (reservados + pagos) / total_numeros * 100
    st.progress(progresso / 100)
    st.caption(f"{progresso:.1f}% preenchido")

# ============================================================================
# GRADE 10x10 DE NÚMEROS
# ============================================================================
st.markdown("## 🎯 Escolha seu número da sorte!")

# Criar grade 10x10 usando columns
for row in range(10):
    cols = st.columns(10, gap="small")
    for col_idx, col in enumerate(cols):
        number = row * 10 + col_idx + 1
        fralda_size = get_fralda_size(number)

        # Encontrar status do número
        entry = next((e for e in sheet_data if int(e.get('Número', 0)) == number), None)
        status = entry.get('Status', 'Disponível') if entry else 'Disponível'
        nome = entry.get('Nome', '') if entry else ''

        with col:
            # Configurar estilo baseado no status
            if status == 'Disponível':
                btn_class = "available"
                btn_text = f"{number}\n🩲 {fralda_size}"
            elif status == 'Reservado':
                btn_class = "reserved"
                btn_text = f"{number}\n🔒 {nome[:10]}..."
            else:  # Pago
                btn_class = "paid"
                btn_text = f"{number}\n✅ {nome[:10]}..."

            # Botão do número
            if st.button(
                btn_text,
                key=f"num_{number}",
                use_container_width=True,
                help=f"Número {number} - Fralda Tamanho {fralda_size} - {status}"
            ):
                if status == 'Disponível':
                    # Abrir modal de reserva
                    st.session_state['modal_open'] = True
                    st.session_state['selected_number'] = number
                    st.session_state['fralda_size'] = fralda_size
                elif status == 'Reservado':
                    # Mostrar opção de marcar como pago
                    st.session_state['show_paid_modal'] = True
                    st.session_state['paid_number'] = number
                    st.session_state['paid_name'] = nome

# ============================================================================
# MODAL DE RESERVA
# ============================================================================
if st.session_state.get('modal_open', False):
    selected_num = st.session_state.get('selected_number')
    fralda = st.session_state.get('fralda_size', 'M')

    st.markdown("---")
    st.markdown(f"### 🎀 Reservar Número {selected_num}")
    st.info(f"🩲 Tamanho da fralda: **{fralda}**")

    with st.form(key="reservation_form"):
        col_name, col_phone = st.columns(2)

        with col_name:
            nome = st.text_input("👤 Seu nome:", placeholder="Digite seu nome")

        with col_phone:
            telefone = st.text_input("📱 Seu telefone:", placeholder="(XX) XXXXX-XXXX")

        submit_btn = st.form_submit_button("✅ Confirmar Reserva", use_container_width=True)

        if submit_btn:
            if not nome or not telefone:
                st.error("❌ Por favor, preencha nome e telefone!")
            else:
                # Validar telefone
                phone_clean = re.sub(r'\D', '', telefone)
                if len(phone_clean) < 10:
                    st.error("❌ Telefone inválido!")
                else:
                    # Format telefone
                    if len(phone_clean) == 11:
                        telefone_formatado = f"({phone_clean[:2]}) {phone_clean[2:7]}-{phone_clean[7:]}"
                    else:
                        telefone_formatado = f"({phone_clean[:2]}) {phone_clean[2:6]}-{phone_clean[6:]}"

                    with st.spinner("Reservando número..."):
                        success, message = reserve_number(
                            SPREADSHEET_ID,
                            selected_num,
                            nome,
                            telefone_formatado
                        )

                        if success:
                            st.success(f"🎉 Número {selected_num} reservado com sucesso!")
                            st.balloons()
                            st.session_state['modal_open'] = False
                            st.session_state['selected_number'] = None
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

    # Botão para fechar modal
    if st.button("❌ Cancelar", use_container_width=True):
        st.session_state['modal_open'] = False
        st.session_state['selected_number'] = None
        st.rerun()

# ============================================================================
# MODAL PARA MARCAR COMO PAGO
# ============================================================================
if st.session_state.get('show_paid_modal', False):
    paid_num = st.session_state.get('paid_number')
    paid_name = st.session_state.get('paid_name', 'Desconhecido')

    st.markdown("---")
    st.markdown(f"### ✅ Confirmar Pagamento")
    st.info(f"🎫 Número {paid_num} - {paid_name}")

    col_confirm, col_cancel = st.columns(2)

    with col_confirm:
        if st.button("✅ Confirmar como PAGO", use_container_width=True, key="confirm_paid"):
            with st.spinner("Atualizando status..."):
                success, message = mark_as_paid(SPREADSHEET_ID, paid_num)

                if success:
                    st.success(f"🎉 Pagamento confirmado!")
                    st.balloons()
                    st.session_state['show_paid_modal'] = False
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

    with col_cancel:
        if st.button("❌ Cancelar", use_container_width=True, key="cancel_paid"):
            st.session_state['show_paid_modal'] = False
            st.rerun()

# ============================================================================
# LISTA DE RESERVADOS E PAGOS (opcional, abaixo da grade)
# ============================================================================
st.markdown("---")
st.markdown("### 📋 Lista de Participantes")

col_reservados, col_pagos = st.columns(2)

with col_reservados:
    st.markdown("#### 🔒 Reservados")
    reservados_list = [e for e in sheet_data if e.get('Status') == 'Reservado']
    if reservados_list:
        for entry in sorted(reservados_list, key=lambda x: int(x.get('Número', 0))):
            num = entry.get('Número', '?')
            nome = entry.get('Nome', 'Desconhecido')
            fralda = get_fralda_size(int(num))
            st.markdown(f"🎀 **{num}** - {nome} (Fralda {fralda})")
    else:
        st.info("Nenhum reservado ainda")

with col_pagos:
    st.markdown("#### ✅ Pagos")
    pagos_list = [e for e in sheet_data if e.get('Status') == 'Pago']
    if pagos_list:
        for entry in sorted(pagos_list, key=lambda x: int(x.get('Número', 0))):
            num = entry.get('Número', '?')
            nome = entry.get('Nome', 'Desconhecido')
            fralda = get_fralda_size(int(num))
            st.markdown(f"💕 **{num}** - {nome} (Fralda {fralda})")
    else:
        st.info("Nenhum pago ainda")

# ============================================================================
# AUTO-REFRESH (opcional)
# ============================================================================
# st.rerun() automático a cada 60s pode ser habilitado se necessário
# if st.session_state.get('auto_refresh', False):
#     import time
#     time.sleep(60)
#     st.rerun()
