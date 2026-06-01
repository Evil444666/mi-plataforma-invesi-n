import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. CONFIGURACIÓN DE LA APP (Modo Ancho y Tema Oscuro)
st.set_page_config(page_title="QuantumTerminal Pro", page_icon="📈", layout="wide")

# CSS para forzar la estética de aplicación de escritorio de trading
st.markdown("""
    <style>
    /* Fondo general de la App */
    .stApp {
        background-color: #0b0e14;
        color: #c9d1d9;
    }
    /* Estilo del contenedor de la barra lateral (Sidebar) */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    /* Tarjeta del perfil de cliente VIP */
    .user-profile {
        background-color: #21262d;
        padding: 12px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-top: 20px;
    }
    /* Títulos y fuentes estilo SaaS */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        font-weight: 700 !important;
    }
    /* Ajuste de métricas */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }
    div[data-testid="stMetric"] {
        background-color: #161b22;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    /* Botones de acción */
    .stButton>button {
        background: linear-gradient(135deg, #1f6feb 0%, #0d44a0 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 6px !important;
        border: none !important;
        padding: 0.6rem 1rem !important;
        width: 100% !important;
        transition: 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0px 4px 12px rgba(31, 111, 235, 0.3);
    }
    /* Estilo para tablas mimetizadas */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 0.95rem;
        background-color: #161b22;
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #30363d;
    }
    .styled-table th {
        background-color: #21262d;
        color: #58a6ff;
        text-align: left;
        padding: 12px 15px;
        font-weight: 600;
        border-bottom: 1px solid #30363d;
    }
    .styled-table td {
        padding: 12px 15px;
        border-bottom: 1px solid #21262d;
    }
    .styled-table tr:last-of-type td {
        border-bottom: none;
    }
    </style>
""", unsafe_allow_html=True)

def buscar_y_ordenar_empresas(palabra_clave):
    palabra_clave = palabra_clave.strip().upper()
    try:
        t_directo = yf.Ticker(palabra_clave)
        info_directa = t_directo.info
        if info_directa and 'marketCap' in info_directa and info_directa['marketCap'] is not None:
            nombre = info_directa.get('longName') or info_directa.get('shortName') or palabra_clave
            return [{'ticker': palabra_clave, 'nombre': nombre, 'market_cap': info_directa['marketCap']}]
    except Exception:
        pass

    try:
        busqueda = yf.Search(palabra_clave, max_results=6)
        resultados = busqueda.quotes
        if not resultados:
            return []
        lista_empresas = []
        for r in resultados:
            ticker_simbolo = r.get('symbol')
            if not ticker_simbolo or "." in ticker_simbolo: 
                continue
            nombre_oficial = r.get('longname') or r.get('shortname') or "Desconocido"
            try:
                t = yf.Ticker(ticker_simbolo)
                market_cap = t.info.get('marketCap', 0) or 0
            except Exception:
                market_cap = 0
            lista_empresas.append({'ticker': ticker_simbolo, 'nombre': nombre_oficial, 'market_cap': market_cap})
        return sorted([e for e in lista_empresas if e['market_cap'] > 0], key=lambda x: x['market_cap'])
    except Exception:
        return []

@st.cache_data(ttl=3600)  # Guarda el Top 10 en caché durante 1 hora para una carga veloz
def obtener_top_10_expertos():
    # Lista
