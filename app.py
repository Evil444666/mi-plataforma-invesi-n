import streamlit as st
import yfinance as yf
import pandas as pd

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
# 🎛️ ESTRUCTURA APP: BARRA LATERAL (MENÚ DE NAVEGACIÓN Y CONFIGURACIÓN)
# =========================================================================
with st.sidebar:
    # LOGO DE LA PÁGINA (Estilo Corporativo Tech)
    st.markdown("""
        <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 25px;'>
            <div style='background-color: #1f6feb; padding: 8px 12px; border-radius: 8px; color: white; font-weight: bold; font-size: 1.2rem;'>Q</div>
            <div style='font-size: 1.2rem; font-weight: 800; color: white; letter-spacing: -0.5px;'>QUANTUM<span style='color:#1f6feb;'>SaaS</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 Panel de Control")
    entrada = st.text_input("Buscar Activo:", placeholder="Ej: Apple, Tesla, NVDA...")
    
    # Menú dinámico si se busca algo
    ticker_elegido = None
    if entrada:
        with st.spinner("Escaneando Wall Street..."):
            empresas_encontradas = buscar_y_ordenar_empresas(entrada)
            
        if empresas_encontradas:
            opciones = []
            for emp in empresas_encontradas:
                cap_billones = emp['market_cap'] / 1_000_000_000 if emp['market_cap'] else 0
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

    # Espaciador para mandar el perfil al fondo de la barra
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    
    # LÓGICA DEL LOGO DE CLIENTE VIP (Sección de Cuenta del Usuario)
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
# 💻 PANEL CENTRAL: MONITOR DE DATOS OPERATIVOS
# =========================================================================
if ejecutar_analisis and ticker_elegido:
    with st.spinner("Sincronizando flujos de datos..."):
        try:
            empresa = yf.Ticker(ticker_elegido)
            info = empresa.info
            nombre_real = info.get('longName') or ticker_elegido
            
            # Encabezado dinámico de la empresa analizada
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
            
            # --- BLOQUE 2: GRÁFICA VECTORIAL DE ALTO IMPACTO ---
            historial = empresa.history(period="15d")
            if not historial.empty:
                st.markdown("### 📡 Flujo de Tendencia (15 Períodos)")
                historial['Diferencia'] = historial['Close'].diff()
                historial.iloc[0, historial.columns.get_loc('Diferencia')] = 0
                historial['Color'] = historial['Diferencia'].apply(lambda x: '#00cc66' if x >= 0 else '#ff3333')
                
                datos_grafica = pd.DataFrame({
                    'Fecha': historial.index.strftime('%Y-%m-%d'),
                    'Precio ($)': historial['Close'].round(2),
                    'color': historial['Color']
                })
                st.bar_chart(datos_grafica, x='Fecha', y='Precio ($)', color='color', use_container_width=True)
            
            st.markdown("---")
            
            # --- BLOQUE 3: AUDITORÍA INTELECTUAL ---
            st.markdown("### 📋 Evaluación de Riesgos Financieros")
            puntuacion = 0
            razones = []
            
            if pe_ratio != float('inf') and pe_ratio < 20:
                puntuacion += 1
                razones.append("🟢 **Precio Atractivo:** Cotización equilibrada respecto a sus ganancias corporativas actuales (P/E < 20).")
            else:
                razones.append("🟡 **Multiplo Exigente:** El mercado está pagando un premium alto por esta acción (P/E > 20).")
                
            if margin_neto > 15:
                puntuacion += 1
                razones.append("🟢 **Ventaja Competitiva:** Margen de ganancia neto excelente superior al 15%. Gran retención de caja.")
            else:
                razones.append("🟡 **Rendimiento Ajustado:** Márgenes de beneficio limitados debido a costes operativos elevados (Menor al 15%).")
                
            if debt_to_equity < 100:
                puntuacion += 1
                razones.append("🟢 **Estructura Balance Lineal:** La deuda se mantiene controlada y por debajo de su patrimonio neto.")
            else:
                razones.append("🔴 **Carga de Deuda Pasiva:** El pasivo financiero supera los recursos propios. Incremento de riesgo crediticio.")
            
            for razon in razones:
                st.markdown(razon)
                
            st.markdown("<br>", unsafe_allow_html=True)
            
            # SEÑAL FINAL EN CAJA ESTILIZADA
            if puntuacion == 3:
                st.success("### 💥 CONCLUSIÓN DEL SISTEMA: ALTA CONVICCIÓN DE COMPRA")
            elif puntuacion == 2:
                st.warning("### ⚖️ CONCLUSIÓN DEL SISTEMA: CONDICIÓN DE MANTENER / ESPERAR")
            else:
                st.error("### ❌ CONCLUSIÓN DEL SISTEMA: ALTA SEÑAL DE RIESGO / EVITAR")
                
        except Exception as e:
            st.error(f"Error técnico de enlace de datos: {e}")
else:
    # Pantalla de bienvenida limpia cuando la app se abre por primera vez
    st.markdown("<h1 style='text-align: center; margin-top: 10%; color: #58a6ff;'>🎛️ Terminal Abierta y Lista</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Usa la barra de herramientas de la izquierda para buscar un activo financiero e iniciar el análisis algorítmico en tiempo real.</p>", unsafe_allow_html=True)
