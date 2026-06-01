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
    entrada = st.text_input("Buscar Activo:", placeholder="Ej: Apple, Tesla, NVDA...")
    
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

    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
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

# =========================================================================
# 💻 PANEL CENTRAL
# =========================================================================
if ejecutar_analisis and ticker_elegido:
    with st.spinner("Sincronizando flujos de datos..."):
        try:
            empresa = yf.Ticker(ticker_elegido)
            info = empresa.info
            nombre_real = info.get('longName') or ticker_elegido
            
            st.markdown(f"<h1 style='margin-bottom: 0;'>📈 Monitor Operativo: {nombre_real}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='color: #8b949e; margin-top: 0;'>Código oficial de mercado: <b>{ticker_elegido}</b></p>", unsafe_allow_html=True)
            st.markdown("---")
            
            # --- BLOQUE 1: TARJETAS DE INDICADORES ---
            precio_actual = info.get('currentPrice') or info.get('navPrice') or info.get('previousClose') or 0
            pe_ratio = info.get('trailingPE', float('inf')) or float('inf')
            debt_to_equity = info.get('debtToEquity', 0) or 0
            margin_neto = (info.get('profitMargins', 0) or 0) * 100
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("VALOR EN TIEMPO REAL", f"${precio_actual:,.2f}")
            c2.metric("MÚLTIPLO P/E", f"{pe_ratio:.2f}" if pe_ratio != float('inf') else "N/A")
            c3.metric("MARGEN DE UTILIDAD", f"{margin_neto:.2f}%")
            c4.metric("RATIO APALANCAMIENTO", f"{debt_to_equity:.1f}%")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # --- BLOQUE 2: GRÁFICA DE VELAS CONTINVA Y ULTRA LIMPIA ---
            historial = empresa.history(period="5d", interval="15m")
            
            if not historial.empty:
                st.markdown("### 📡 Velas de Alta Frecuencia (Intervalo: 15 Minutos)")
                
                # Formateamos las fechas de fondo para que aparezcan bonitas en los pop-ups flotantes al pasar el cursor
                fechas_limpias = historial.index.strftime('%b %d, %H:%M')
                
                fig = go.Figure(data=
