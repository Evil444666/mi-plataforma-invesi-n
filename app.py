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
""", unsafe_allow_html=True)  # <-- ESTA ES LA LÍNEA CORREGIDA

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

@st.cache_data(ttl=3600)
def obtener_top_10_expertos():
    tickers_control = [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "LLY", "V", "TSM",
        "AVGO", "NVO", "JPM", "WMT", "UNH", "ASML", "ORCL", "NFLX", "COST", "AMD",
        "HD", "XOM", "MA", "PG", "JNJ", "BRK-B"
    ]
    
    lista_recom = []
    for ticker in tickers_control:
        try:
            t = yf.Ticker(ticker)
            info = t.info
            if not info:
                continue
                
            precio_actual = info.get('currentPrice') or info.get('previousClose') or 1
            precio_objetivo = info.get('targetMeanPrice') or precio_actual
            potencial = ((precio_objetivo - precio_actual) / precio_actual) * 100
            
            rating = info.get('recommendationRating', 3.0) or 3.0
            texto_rating = info.get('recommendationKey', 'HOLD').upper().replace('_', ' ')
            nombre = info.get('shortName') or info.get('longName') or ticker
            
            lista_recom.append({
                "Ticker": ticker,
                "Empresa": nombre,
                "Precio Act.": f"${precio_actual:,.2f}",
                "Obj. Expertos": f"${precio_objetivo:,.2f}",
                "Potencial": potencial,
                "Consenso": texto_rating,
                "RatingNum": rating
            })
        except Exception:
            continue
            
    df = pd.DataFrame(lista_recom)
    if not df.empty:
        df = df.sort_values(by=["RatingNum", "Potencial"], ascending=[True, False])
        return df.head(10)
    return pd.DataFrame()

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
            empresa = yf.Ticker(ticker_elegido
