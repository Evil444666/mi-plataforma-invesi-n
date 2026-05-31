%%writefile app.py
import streamlit as st
import yfinance as yf

st.set_page_config(page_title="Terminal de Inversión", page_icon="📈", layout="wide")
st.title("🤖 Mi Plataforma de Inversión Inteligente")
st.write("Busca cualquier empresa de Wall Street por su nombre. El sistema la ordenará por tamaño y analizará sus balances al instante.")

def buscar_y_ordenar_empresas(palabra_clave):
    try:
        busqueda = yf.Search(palabra_clave, max_results=7)
        resultados = busqueda.quotes
        if not resultados:
            return []
        lista_empresas = []
        for r in resultados:
            ticker_simbolo = r.get('symbol')
            nombre_oficial = r.get('longname') or r.get('shortname') or "Desconocido"
            t = yf.Ticker(ticker_simbolo)
            market_cap = t.info.get('marketCap', 0) or 0 
            lista_empresas.append({'ticker': ticker_simbolo, 'nombre': nombre_oficial, 'market_cap': market_cap})
        return sorted(lista_empresas, key=lambda x: x['market_cap'])
    except Exception:
        return []

entrada = st.text_input("Introduce el nombre de la empresa (ej: 'Apple', 'Tesla'):", "")

if entrada:
    empresas_encontradas = buscar_y_ordenar_empresas(entrada)
    if empresas_encontradas:
        st.subheader("📍 Empresas encontradas (Ordenadas de menor a mayor):")
        opciones = [f"{emp['nombre']} [{emp['ticker']}] - ({emp['market_cap']/1_000_000_000:.2f}B USD)" for emp in empresas_encontradas]
        seleccion = st.selectbox("Selecciona la empresa exacta para auditar:", opciones)
        indice_seleccionado = opciones.index(seleccion)
        ticker_elegido = empresas_encontradas[indice_seleccionado]['ticker']
        
        if st.button("🚀 Ejecutar Auditoría Financiera"):
            st.divider()
            with st.spinner("Conectando con Wall Street..."):
                try:
                    empresa = yf.Ticker(ticker_elegido)
                    info = empresa.info
                    precio_actual = info.get('currentPrice', 0)
                    pe_ratio = info.get('trailingPE', float('inf'))
                    debt_to_equity = info.get('debtToEquity', 100)
                    margin_neto = info.get('profitMargins', 0) * 100
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Precio Actual", f"${precio_actual}")
                    col2.metric("Ratio P/E", f"{pe_ratio if pe_ratio != float('inf') else 'N/A'}")
                    col3.metric("Margen Neto", f"{margin_neto:.2f}%")
                    col4.metric("Deuda / Capital", f"{debt_to_equity}%")
                    
                    puntuacion = 0
                    razones = []
                    if pe_ratio < 20:
                        puntuacion += 1
                        razones.append("La empresa cotiza a una valoración atractiva (P/E < 20).")
                    else:
                        razones.append("La valoración es alta (P/E > 20). Riesgo de sobreprecio.")
                    if margin_neto > 15:
                        puntuacion += 1
                        razones.append("Excelente rentabilidad. Margen neto superior al 15%.")
                    else:
                        razones.append("Márgenes de ganancia ajustados (Menor al 15%).")
                    if debt_to_equity < 100:
                        puntuacion += 1
                        razones.append("Nivel de deuda saludable y bajo control.")
                    else:
                        razones.append("Atención: La deuda supera el capital de la empresa.")
                    
                    st.write("#### 📋 Puntos Clave del Análisis:")
                    for razon in razones:
                        st.write(f"- {razon}")
                        
                    if puntuacion == 3:
                        st.success("💥 RECOMENDACIÓN: COMPRA FUERTE (Oportunidad Value).")
                    elif puntuacion == 2:
                        st.warning("⚖️ RECOMENDACIÓN: MANTENER / VIGILAR (Precio justo).")
                    else:
                        st.error("❌ RECOMENDACIÓN: EVITAR / VENDER (Alto riesgo).")
                except Exception as e:
                    st.error(f"Error al obtener datos: {e}")
    else:
        st.error("No se encontraron empresas.")