# -*- coding: utf-8 -*-
"""
👶 Chá Rifa da Mariana - VISUALIZAÇÃO CLIENTE
🎀 Tela simplificada apenas para visualização dos números
"""

import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================
st.set_page_config(
    page_title="👶 Chá Rifa da Mariana",
    page_icon="🎀",
    layout="wide",
    initial_sidebar_state="collapsed"
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

/* Botões da grade - Disponíveis */
.available {
    background: linear-gradient(45deg, #a8e6cf, #dcedc1) !important;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(168,230,207,0.4);
    cursor: default;
}

/* Botões da grade - Reservados */
.reserved {
    background: linear-gradient(45deg, #ff6b6b, #ff8e8e) !important;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(255,107,107,0.4);
    cursor: default;
}

/* Botões da grade - Pagos */
.paid {
    background: linear-gradient(45deg, #ffd93d, #ffed4e) !important;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(255,217,61,0.4);
    cursor: default;
}

/* Cards do dashboard */
.metric-card {
    background: white;
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0 4px 15px rgba(255,154,162,0.2);
    text-align: center;
}

/* Esconder elementos do Streamlit */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================================
# CONFIGURAÇÃO DO GOOGLE SHEETS
# ============================================================================
SPREADSHEET_ID = st.secrets.get("spreadsheet_id", "SUA_PLANILHA_ID_AQUI")
SERVICE_ACCOUNT_INFO = st.secrets.get("service_account", None)


@st.cache_resource
def get_gspread_client():
    """Inicializa o cliente do Google Sheets com cache."""
    if SERVICE_ACCOUNT_INFO:
        credentials = Credentials.from_service_account_info(
            SERVICE_ACCOUNT_INFO,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        return gspread.authorize(credentials)
    return None


@st.cache_data(ttl=10)
def get_sheet_data(spreadsheet_id):
    """Busca dados da planilha com cache de 10 segundos."""
    try:
        client = get_gspread_client()
        if client is None:
            return None

        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1
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


def get_fralda_size(number):
    """Determina o tamanho da fralda: 1-20=P, 21-55=M, 56-100=G"""
    if 1 <= number <= 20:
        return "P"
    elif 21 <= number <= 55:
        return "M"
    else:
        return "G"


# ============================================================================
# HEADER
# ============================================================================
st.markdown("""
<div style='text-align: center;'>
    <h1 style='font-size: 3em; margin-bottom: 0;'>👶 Chá Rifa da Mariana 🎀</h1>
    <p style='font-size: 1.3em; color: #ff6b8a;'>🎉 Ajude a mamãe a preparar o enxoval do bebê!</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# DASHBOARD SIMPLIFICADO
# ============================================================================
sheet_data = get_sheet_data(SPREADSHEET_ID)

if sheet_data is None:
    st.warning("⚠️ Não foi possível carregar os dados.")
    st.stop()

# Calcular estatísticas
total_numeros = 100
disponiveis = sum(1 for e in sheet_data if e.get('Status') == 'Disponível')
reservados = sum(1 for e in sheet_data if e.get('Status') == 'Reservado')
pagos = sum(1 for e in sheet_data if e.get('Status') == 'Pago')

# Dashboard em colunas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h2 style="color: #555; margin: 0; font-size: 2em; text-shadow: 0 0 3px rgba(0,0,0,0.1);">{total_numeros}</h2>
        <p style="margin: 0; color: #666; font-weight: 600;">Total</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h2 style="color: #2d5a3d; margin: 0; font-size: 2em; text-shadow: 0 0 3px rgba(168,230,207,0.5);">{disponiveis}</h2>
        <p style="margin: 0; color: #2d5a3d; font-weight: 600;">Disponíveis</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h2 style="color: #8b0000; margin: 0; font-size: 2em; text-shadow: 0 0 3px rgba(255,107,107,0.5);">{reservados}</h2>
        <p style="margin: 0; color: #8b0000; font-weight: 600;">Reservados</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <h2 style="color: #8b6b00; margin: 0; font-size: 2em; text-shadow: 0 0 3px rgba(255,217,61,0.5);">{pagos}</h2>
        <p style="margin: 0; color: #8b6b00; font-weight: 600;">Pagos</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# LEGENDA
# ============================================================================
st.markdown("### 📖 Legenda")
legenda_col1, legenda_col2, legenda_col3 = st.columns(3)

with legenda_col1:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 10px; padding: 10px; background: white; border-radius: 10px; border: 2px solid #a8e6cf;'>
        <div style='width: 30px; height: 30px; background: linear-gradient(45deg, #a8e6cf, #dcedc1); border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);'></div>
        <span style='font-size: 1.1em; color: #2d5a3d; font-weight: bold;'>🟩 Disponível</span>
    </div>
    """, unsafe_allow_html=True)

with legenda_col2:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 10px; padding: 10px; background: white; border-radius: 10px; border: 2px solid #ff6b6b;'>
        <div style='width: 30px; height: 30px; background: linear-gradient(45deg, #ff6b6b, #ff8e8e); border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);'></div>
        <span style='font-size: 1.1em; color: #8b0000; font-weight: bold;'>🟥 Reservado</span>
    </div>
    """, unsafe_allow_html=True)

with legenda_col3:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 10px; padding: 10px; background: white; border-radius: 10px; border: 2px solid #ffd93d;'>
        <div style='width: 30px; height: 30px; background: linear-gradient(45deg, #ffd93d, #ffed4e); border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);'></div>
        <span style='font-size: 1.1em; color: #8b6b00; font-weight: bold;'>🟨 Pago</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================================
# GRADE 10x10 DE NÚMEROS (APENAS VISUALIZAÇÃO)
# ============================================================================
st.markdown("## 🎯 Números Disponíveis")

for row in range(10):
    cols = st.columns(10, gap="small")
    for col_idx, col in enumerate(cols):
        number = row * 10 + col_idx + 1
        fralda_size = get_fralda_size(number)

        entry = next((e for e in sheet_data if int(e.get('Número', 0)) == number), None)
        status = entry.get('Status', 'Disponível') if entry else 'Disponível'
        nome = entry.get('Nome', '') if entry else ''

        with col:
            if status == 'Disponível':
                btn_text = f"{number}\n🩲 {fralda_size}"
                st.button(
                    btn_text,
                    key=f"num_{number}",
                    use_container_width=True,
                    disabled=True,
                    help=f"Fralda Tamanho {fralda_size}"
                )
            elif status == 'Reservado':
                nome_curto = nome[:8] + "..." if len(nome) > 8 else nome
                btn_text = f"{number}\n🔒 {nome_curto}"
                st.button(
                    btn_text,
                    key=f"num_{number}",
                    use_container_width=True,
                    disabled=True,
                    help=f"Reservado por {nome}"
                )
            else:  # Pago
                nome_curto = nome[:8] + "..." if len(nome) > 8 else nome
                btn_text = f"{number}\n✅ {nome_curto}"
                st.button(
                    btn_text,
                    key=f"num_{number}",
                    use_container_width=True,
                    disabled=True,
                    help=f"Pago por {nome}"
                )

st.markdown("---")

# ============================================================================
# LISTA DE DISPONÍVEIS (DESTAQUE)
# ============================================================================
st.markdown("## 🟩 Números Livres para Reserva")

disponiveis_list = [e for e in sheet_data if e.get('Status') == 'Disponível']

if disponiveis_list:
    # Criar grupos de 10 para exibição
    cols = st.columns(10)
    for idx, entry in enumerate(sorted(disponiveis_list, key=lambda x: int(x.get('Número', 0)))):
        col_idx = idx % 10
        with cols[col_idx]:
            num = entry.get('Número', '?')
            fralda = get_fralda_size(int(num))
            st.markdown(f"""
            <div style='background: linear-gradient(45deg, #a8e6cf, #dcedc1);
                        padding: 10px; border-radius: 8px; text-align: center;
                        margin: 5px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1);'>
                <strong style='font-size: 1.2em; color: #2d5a3d;'>{num}</strong>
                <br><small style='color: #4a7c59;'>Fralda {fralda}</small>
            </div>
            """, unsafe_allow_html=True)
else:
    st.info("🎉 Todos os números foram reservados!")

st.markdown("---")

# ============================================================================
# RODAPÉ COM CONTATO
# ============================================================================
st.markdown("""
<div style='text-align: center; padding: 20px; background: white; border-radius: 15px; margin-top: 20px;'>
    <h3 style='color: #ff6b8a; margin-bottom: 10px;'>💕 Quer reservar um número?</h3>
    <p style='font-size: 1.1em; color: #666;'>
        Entre em contato com a organizadora para reservar seu número!
    </p>
    <p style='font-size: 1.3em; color: #ff6b8a; font-weight: bold;'>
        📱 (11) 98071-5234
    </p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh a cada 30 segundos
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = 0

# Botão de refresh manual
col_refresh, col_space = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 Atualizar", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
