import streamlit as st
import yfinance as yf
import pandas as pd

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILO COMPLETO (Tema Oscuro Premium)
st.set_page_config(page_title="Terminal Quant Pro", page_icon="⚡", layout="wide")

# Forzamos un look "Dark Mode" de aplicación de trading con CSS inyectado
st.markdown("""
    <style>
    /* Fondo general y fuentes */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    /* Estilo de los títulos */
    h1 {
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
        font-weight: 800 !important;
        letter-spacing: -1px;
    }
    h2, h3 {
        color: #58a6ff !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600 !important;
    }
    /* Estilo para las tarjetas de métricas */
    div[data-testid="stMetricValue"] {
        font-size: 32px !important;
        font-weight: bold !important;
        color: #ffffff !important;
    }
    /* Bordes redondeados y fondos de los bloques */
    .stSelectbox, .stTextInput, .stButton>button {
        border-radius: 8px !important;
    }
    .stButton>button {
        background-color: #238636 !important;
        color: white !important;
        font-weight: bold !important;
        width: 100% !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #2ea043 !important;
        transform: scale(1.02);
    }
    /* Separadores decorativos */
    hr {
        border-top: 1px solid #21262d !important;
    }
    </style>
""", unsafe_allow_html=True)

# ENCABEZADO DE LA PLATAFORMA
st.markdown("# ⚡ TERMINAL QUANT PRO")
st.markdown("<p style='color: #8b949e; font-size: 1.1rem;'>Plataforma Inteligente de Análisis de Activos en Tiempo Real conectado con Wall Street.</p>", unsafe_allow_html=True)
st.markdown("---")

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
        busqueda = yf.Search(palabra_clave, max_results=8)
        resultados = busqueda.quotes
        if not resultados:
            return []
            
        lista_empresas = []
        for r in resultados:
            ticker_simbolo = r.get('symbol')
            if not ticker_simbolo or "." in ticker_simbolo: 
                continue
            nombre_oficial = r.get('longname') or r.get('shortname') or r.get('name') or "Desconocido"
            try:
                t = yf.Ticker(ticker_simbolo)
                market_cap = t.info.get('marketCap', 0) or 0
            except Exception:
                market_cap = 0
            lista_empresas.append({'ticker': ticker_simbolo, 'nombre': nombre_oficial, 'market_cap': market_cap})
            
        lista_filtrada = [e for e in lista_empresas if e['market_cap'] > 0]
        if not lista_filtrada and lista_empresas:
            return lista_empresas
        return sorted(lista_filtrada, key=lambda x: x['market_cap'])
    except Exception:
        return []

# INTERFAZ DE BÚSQUEDA ELEGANTE
col_izq, col_der = st.columns([2, 1])

with col_izq:
    entrada = st.text_input("🔍 Sistema de Radar (Introduce Nombre o Código Ticker):", placeholder="Ej: Apple, Tesla, NVDA...")

if entrada:
    with st.spinner("Conectando con los servidores de la Bolsa..."):
        empresas_encontradas = buscar_y_ordenar_empresas(entrada)
        
    if empresas_encontradas:
        with col_der:
            opciones = []
            for emp in empresas_encontradas:
                cap_billones = emp['market_cap'] / 1_000_000_000 if emp['market_cap'] else 0
                opciones.append(f"{emp['ticker']} | {emp['nombre']} ({cap_billones:.1f}B USD)")
                
            seleccion = st.selectbox("🎯 Activo exacto a auditar:", opciones)
        
        indice_seleccionado = opciones.index(seleccion)
        ticker_elegido = empresas_encontradas[indice_seleccionado]['ticker']
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 INICIAR ESCANEO CUANTITATIVO"):
            st.markdown("---")
            
            with st.spinner("Procesando histórico de precios y balances contables..."):
                try:
                    empresa = yf.Ticker(ticker_elegido)
                    
                    # --- DISEÑO PANEL DE INFORMACIÓN ---
                    info = empresa.info
                    precio_actual = info.get('currentPrice') or info.get('navPrice') or info.get('previousClose') or 0
                    pe_ratio = info.get('trailingPE', float('inf')) or float('inf')
                    debt_to_equity = info.get('debtToEquity', 0) or 0
                    margin_neto = (info.get('profitMargins', 0) or 0) * 100
                    
                    st.subheader(f"📊 Dashboard Operativo: {ticker_elegido}")
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("💰 PRECIO ACTUAL", f"${precio_actual:,.2f}")
                    m2.metric("📈 RATIO P/E", f"{pe_ratio:.2f}" if pe_ratio != float('inf') else "N/A")
                    m3.metric("💎 MARGEN NETO", f"{margin_neto:.2f}%")
                    m4.metric("⚖️ DEUDA / CAPITAL", f"{debt_to_equity:.1f}%")
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # --- DISEÑO CENTRAL: GRÁFICA ---
                    historial = empresa.history(period="15d")
                    if not historial.empty:
                        st.markdown("### 📡 Tendencia de Mercado (Últimos 15 Días)")
                        
                        historial['Diferencia'] = historial['Close'].diff()
                        historial.iloc[0, historial.columns.get_loc('Diferencia')] = 0
                        historial['Color'] = historial['Diferencia'].apply(lambda x: '#00cc66' if x >= 0 else '#ff3333')
                        
                        datos_grafica = pd.DataFrame({
                            'Fecha': historial.index.strftime('%Y-%m-%d'),
                            'Precio ($)': historial['Close'].round(2),
                            'color': historial['Color']
                        })
                        
                        st.bar_chart(
                            datos_grafica, 
                            x='Fecha', 
                            y='Precio ($)', 
                            color='color', 
                            use_container_width=True
                        )
                    
                    st.markdown("---")
                    
                    # --- ANÁLISIS DE BALANCES ---
                    st.markdown("### 📋 Resultados de la Auditoría Computarizada")
                    
                    puntuacion = 0
                    razones = []
                    
                    if pe_ratio != float('inf') and pe_ratio < 20:
                        puntuacion += 1
                        razones.append("🟢 **Valoración Atractiva:** El precio de la acción está barato en relación a sus ganancias actuales (P/E < 20).")
                    else:
                        razones.append("🟡 **Valoración Elevada:** El precio actual exige altas expectativas de crecimiento futuro (P/E > 20).")
                        
                    if margin_neto > 15:
                        puntuacion += 1
                        razones.append("🟢 **Eficiencia Operativa Extrema:** Margen neto brutal superior al 15%. Conserva gran parte de lo que vende.")
                    else:
                        razones.append("🟡 **Rentabilidad Ajustada:** Los márgenes comerciales son estrechos o negativos (Menor al 15%).")
                        
                    if debt_to_equity < 100:
                        puntuacion += 1
                        razones.append("🟢 **Salud Financiera Sólida:** El nivel de endeudamiento es seguro y está perfectamente respaldado por su capital.")
                    else:
                        razones.append("🔴 **Riesgo de Apalancamiento:** La deuda supera los fondos propios. Alerta de carga financiera.")
                    
                    for razon in razones:
                        st.markdown(razon)
                        
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    if puntuacion == 3:
                        st.success("### 💥 SEÑAL ALGORÍTMICA: COMPRA FUERTE (Oportunidad de Alta Convicción)")
                    elif puntuacion == 2:
                        st.warning("### ⚖️ SEÑAL ALGORÍTMICA: MANTENER / BAJO VIGILANCIA (Precio en Rango Justo)")
                    else:
                        st.error("### ❌ SEÑAL ALGORÍTMICA: EVITAR / RESTRICCIÓN DE COMPRA (Riesgo Estructural)")
                        
                except Exception as e:
                    st.error(f"Error de sincronización con los datos de Wall Street: {e}")
    else:
        st.error("❌ No se encontraron activos con esos parámetros en el radar internacional.")
