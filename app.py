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
        color: #c9d1d9;
    }
    .styled-table tr:last-of-type td {
        border-bottom: none;
    }
    </style>
""", unsafe_allow_html=True)

def buscar_y_ordenar_empresas(palabra_clave):
    palabra_clave = palabra_clave.strip().upper()
    if not palabra_clave:
        return []
        
    # Diccionario inteligente de mapeo rápido para evitar depender de la búsqueda rota de Yahoo
    mapeo_comun = {
        "TESLA": "TSLA", "APPLE": "AAPL", "MICROSOFT": "MSFT", "AMAZON": "AMZN",
        "GOOGLE": "GOOGL", "ALPHABET": "GOOGL", "META": "META", "FACEBOOK": "META",
        "NETFLIX": "NFLX", "NVIDIA": "NVDA", "AMD": "AMD", "COSTCO": "COST", "BROADCOM": "AVGO"
    }
    
    # Si escribió el nombre común, lo transformamos instantáneamente en su Ticker
    if palabra_clave in mapeo_comun:
        palabra_clave = mapeo_comun[palabra_clave]

    # Intento 1: Comprobar si es un Ticker Directo Válido
    try:
        t_directo = yf.Ticker(palabra_clave)
        info_directa = t_directo.info
        if info_directa and ('marketCap' in info_directa or 'currentPrice' in info_directa):
            nombre = info_directa.get('longName') or info_directa.get('shortName') or palabra_clave
            mcap = info_directa.get('marketCap', 1) or 1
            return [{'ticker': palabra_clave, 'nombre': nombre, 'market_cap': mcap}]
    except Exception:
        pass

    # Intento 2: Búsqueda de respaldo modificada si el usuario metió texto aleatorio
    try:
        busqueda = yf.Search(palabra_clave, max_results=3)
        resultados = busqueda.quotes
        if resultados:
            lista_empresas = []
            for r in resultados:
                ticker_simbolo = r.get('symbol')
                if not ticker_simbolo or "." in ticker_simbolo: 
                    continue
                nombre_oficial = r.get('longname') or r.get('shortname') or "Activo Financiero"
                lista_empresas.append({'ticker': ticker_simbolo, 'nombre': nombre_oficial, 'market_cap': 1})
            if lista_empresas:
                return lista_empresas
    except Exception:
        pass

    # Si todo falla, forzamos la creación con lo que el usuario escribió para no dejarlo varado
    return [{'ticker': palabra_clave, 'nombre': f"Resultado para {palabra_clave}", 'market_cap': 1}]

# =========================================================================
# 🎛️ ESTRUCTURA APP: BARRA LATERAL
# =========================================================================
with st.sidebar:
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 25px;'>
            <div style='background-color: #1f6feb; padding: 8px 12px; border-radius: 8px; color: white; font-weight: bold; font-size: 1.2rem;'>Q</div>
            <div style='font-size: 1.2rem; font-weight: 800; color: white; letter-spacing: -0.5px;'>QUANTUM<span style='color:#1f6feb;'>SaaS</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 Panel de Control")
    entrada = st.text_input("Buscar Activo:", placeholder="Ej: Tesla, Apple, NVDA...")
    
    ticker_elegido = None
    if entrada:
        with st.spinner("Escaneando Wall Street..."):
            empresas_encontradas = buscar_y_ordenar_empresas(entrada)
            
        if empresas_encontradas:
            opciones = []
            for emp in empresas_encontradas:
                opciones.append(f"{emp['ticker']} | {emp['nombre']}")
                
            seleccion = st.selectbox("Seleccionar empresa:", opciones)
            indice_seleccionado = opciones.index(seleccion)
            ticker_elegido = empresas_encontradas[indice_seleccionado]['ticker']
            
            st.markdown("<br>", unsafe_allow_html=True)
            ejecutar_analisis = st.button("⚡ Ejecutar Terminal")
        else:
            st.error("No se encontraron activos.")
            ejecutar_analisis = False
    else:
        ejecutar_analisis = False

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='user-profile'>
            <div style='display: flex; align-items: center; gap: 12px;'>
                <div style='width: 38px; height: 38px; background-color: #8b949e; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #161b22; font-weight: bold; font-size: 1rem;'>VIP</div>
                <div>
                    <div style='color: white; font-weight: bold; font-size: 0.9rem;'>Inversor Premium</div>
                    <div style='color: #58a6ff; font-size: 0.75rem; font-weight: 600;'>Licencia Activa ✅</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# =================================================================
