# -*- coding: utf-8 -*-
"""
👶 Chá Rifa da Mariana - VISUALIZAÇÃO CLIENTE (SIMPLIFICADA)
🎀 Tela focada apenas nos números disponíveis
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
# CSS CUSTOMIZADO - FOCO EM LIMPEZA
# ============================================================================
CUSTOM_CSS = """
<style>
.main {
    background: linear-gradient(135deg, #fff5f7 0%, #ffe4e6 100%);
    min-height: 100vh;
}
h1, h2, h3 {
    font-family: 'Comic Sans MS', 'Comic Sans', cursive !important;
    color: #ff6b8a;
    text-align: center;
}
/* Esconder elementos desnecessários */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Estilo dos cards de números livres */
.number-card {
    background: linear-gradient(45deg, #a8e6cf, #dcedc1);
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    margin: 8px 0;
    box-shadow: 0 4px 10px rgba(168,230,207,0.4);
    border: 2px solid white;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ============================================================================
# FUNÇÕES DE DADOS (MANTIDAS)
# ============================================================================
SPREADSHEET_ID = st.secrets.get("spreadsheet_id", "")
SERVICE_ACCOUNT_INFO = st.secrets.get("service_account", None)

@st.cache_resource
def get_gspread_client():
    if SERVICE_ACCOUNT_INFO:
        credentials = Credentials.from_service_account_info(
            SERVICE_ACCOUNT_INFO,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        return gspread.authorize(credentials)
    return None

@st.cache_data(ttl=10)
def get_sheet_data(spreadsheet_id):
    try:
        client = get_gspread_client()
        if not client: return None
        spreadsheet = client.open_by_key(spreadsheet_id)
        worksheet = spreadsheet.sheet1
        return worksheet.get_all_records()
    except:
        return None

def get_fralda_size(number):
    if 1 <= number <= 20: return "P"
    elif 21 <= number <= 55: return "M"
    else: return "G"

# ============================================================================
# INTERFACE PRINCIPAL
# ============================================================================
st.markdown("<h1>👶 Chá Rifa da Mariana 🎀</h1>", unsafe_allow_html=True)

sheet_data = get_sheet_data(SPREADSHEET_ID)

if sheet_data:
    disponiveis_list = [e for e in sheet_data if e.get('Status') == 'Disponível']
    
    st.markdown("---")
    st.markdown("## 🟩 Números Livres para Reserva")
    
    if disponiveis_list:
        # Força o Streamlit a manter as colunas lado a lado no celular com CSS Flexbox
        st.markdown("""
            <style>
                [data-testid="stHorizontalBlock"] {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    justify-content: center;
                }
                [data-testid="column"] {
                    min-width: 70px !important; /* Tamanho mínimo do botão no celular */
                    flex: 1 1 15% !important; /* Garante cerca de 4 a 5 por linha */
                }
            </style>
        """, unsafe_allow_html=True)

        # Dados do WhatsApp
        telefone_mae = "5511980715234"
        sorted_list = sorted(disponiveis_list, key=lambda x: int(x.get('Número', 0)))
        
        # Criamos um container flexível
        container = st.container()
        cols = container.columns(5) # Definimos 5, mas o CSS acima vai controlar a quebra
        
        for idx, entry in enumerate(sorted_list):
            with cols[idx % 5]:
                num = entry.get('Número', '?')
                fralda = get_fralda_size(int(num))
                
                mensagem = f"Olá! Gostaria de reservar o número {num} (Fralda {fralda}) para o Chá Rifa da Mariana. 👶🎀"
                link_whatsapp = f"https://wa.me/{telefone_mae}?text={mensagem.replace(' ', '%20')}"
                
                st.markdown(f"""
                <a href="{link_whatsapp}" target="_blank" style="text-decoration: none;">
                    <div style='background: linear-gradient(45deg, #a8e6cf, #dcedc1);
                                padding: 10px 2px; border-radius: 10px; text-align: center;
                                margin-bottom: 5px; border: 2px solid white; 
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
                        <strong style='font-size: 1.1em; color: #2d5a3d; display: block;'>{num}</strong>
                        <span style='color: #4a7c59; font-size: 0.6em; font-weight: bold;'>RESERVAR</span>
                    </div>
                </a>
                """, unsafe_allow_html=True)

# ============================================================================
# RODAPÉ DE CONTATO
# ============================================================================
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 25px; background: white; border-radius: 20px; border: 3px dashed #ffb7b2;'>
    <h3 style='margin-bottom: 5px;'>💕 Como reservar?</h3>
    <p style='font-size: 1.2em; color: #666;'>Mande uma mensagem para a mamãe com o número escolhido:</p>
    <p style='font-size: 1.8em; color: #ff6b8a; font-weight: bold;'>📱 (11) 98071-5234</p>
</div>
""", unsafe_allow_html=True)

# Botão de atualizar pequeno no canto
if st.button("🔄 Atualizar Lista"):
    st.cache_data.clear()
    st.rerun()
