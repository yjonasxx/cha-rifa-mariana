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
        st.markdown("---")
        st.markdown("## 🟩 Escolha seu número (Toque para reservar)")
        
        # Ordenar os números corretamente do 1 ao 100
        sorted_list = sorted(disponiveis_list, key=lambda x: int(x.get('Número', 0)))
        
        # Dados do WhatsApp
        telefone_mae = "5511980715234"
        
        # LISTA VERTICAL (Melhor para Celular)
        # Removi as colunas para que cada número ocupe sua própria linha
        for entry in sorted_list:
            num = entry.get('Número', '?')
            fralda = get_fralda_size(int(num))
            
            # Mensagem personalizada
            mensagem = f"Olá! Gostaria de reservar o número {num} (Fralda {fralda}) para o Chá Rifa da Mariana. 👶🎀"
            link_whatsapp = f"https://wa.me/{telefone_mae}?text={mensagem.replace(' ', '%20')}"
            
            # Botão em largura total (Fácil de clicar com o dedão)
            st.markdown(f"""
            <a href="{link_whatsapp}" target="_blank" style="text-decoration: none;">
                <div style='background: linear-gradient(45deg, #a8e6cf, #dcedc1);
                            padding: 15px; border-radius: 12px; text-align: center;
                            margin-bottom: 10px; border: 2px solid white; 
                            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                            display: flex; justify-content: space-between; align-items: center;'>
                    <div style='text-align: left;'>
                        <strong style='font-size: 1.5em; color: #2d5a3d;'>#{num}</strong>
                        <span style='color: #4a7c59; font-size: 0.9em; margin-left: 10px;'>TAMANHO {fralda}</span>
                    </div>
                    <div style='background: #2d5a3d; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.8em; font-weight: bold;'>
                        RESERVAR NO WHATSAPP ➔
                    </div>
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
