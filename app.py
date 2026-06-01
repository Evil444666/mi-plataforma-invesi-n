import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Terminal de Inversión", page_icon="📈", layout="wide")
st.title("🤖 Mi Plataforma de Inversión Inteligente")
st.write("Busca cualquier empresa de Wall Street por su nombre o su código Ticker (ej: 'AAPL', 'Apple', 'Tesla').")

def buscar_y_ordenar_empresas(palabra_clave):
    # Forzamos mayúsculas por si buscan el código directo (ej: 'aapl' -> 'AAPL')
    palabra_clave = palabra_clave.strip().upper()
    try:
        # Intentamos una búsqueda directa por Ticker primero (es lo más rápido y seguro)
        t_directo = yf.Ticker(palabra_clave)
        info_directa = t_directo.info
        if info_directa and 'marketCap' in info_directa and info_directa['marketCap'] is not None:
            nombre = info_directa.get('longName') or info_directa.get('shortName') or palabra_clave
            return [{'ticker': palabra_clave, 'nombre': nombre, 'market_cap': info_directa['marketCap']}]
    except Exception:
        pass

    # Si no es un Ticker exacto, usamos el motor de búsqueda global
    try:
        busqueda = yf.Search(palabra_clave, max_results=10)
        resultados = busqueda.quotes
        if not resultados:
            return []
            
        lista_empresas = []
        for r in resultados:
            ticker_simbolo = r.get('symbol')
            if not ticker_simbolo:
                continue
                
            nombre_oficial = r.get('longname') or r.get('shortname') or r.get('name') or "Desconocido"
            
            # Conectamos para sacar el tamaño real
            try:
                t = yf.Ticker(ticker_simbolo)
                market_cap = t.info.get('marketCap', 0) or 0
            except Exception:
                market_cap = 0
                
            lista_empresas.append({
                'ticker': ticker_simbolo,
                'nombre': nombre_oficial,
                'market_cap': market_cap
            })
            
        # Filtramos las que no tengan datos válidos y ordenamos de menor a mayor
        lista_filtrada = [e for e in lista_empresas if e['market_cap'] > 0]
        if not lista_filtrada and lista_empresas:
            return lista_empresas # Si ninguna tiene market cap, devolvemos lo que haya
            
        return sorted(lista_filtrada, key=lambda x: x['market_cap'])
    except Exception:
        return []

entrada = st.text_input("Introduce el nombre de la empresa o su código (ej: 'Apple', 'TSLA', 'Amazon'):", "")

if entrada:
    with st.spinner("Buscando en los servidores de Wall Street..."):
        empresas_encontradas = buscar_y_ordenar_empresas(entrada)
        
    if empresas_encontradas:
        st.subheader("📍 Empresas encontradas (Ordenadas de menor a mayor):")
        
        # Formateamos las opciones para el menú desplegable
        opciones = []
        for emp in empresas_encontradas:
            cap_billones = emp['market_cap'] / 1_000_000_000 if emp['market_cap'] else 0
            opciones.append(f"{emp['nombre']} [{emp['ticker']}] - ({cap_billones:.2f}B USD)")
            
        seleccion = st.selectbox("Selecciona la empresa exacta para auditar:", opciones)
        indice_seleccionado = opciones.index(seleccion)
        ticker_elegido = empresas_encontradas[indice_seleccionado]['ticker']
        
        if st.button("🚀 Ejecutar Auditoría Financiera y Gráfica"):
            st.divider()
            with st.spinner(f"Analizando balances históricos de {ticker_elegido}..."):
                try:
                    # --- APARTADO 1: GRÁFICA ---
                    empresa = yf.Ticker(ticker_elegido)
                    historial = empresa.history(period="15d")
                    
                    if not historial.empty:
                        st.write("### 📊 Rendimiento Reciente (Tiempo Real)")
                        historial['Diferencia'] = historial['Close'].diff()
                        historial.iloc[0, historial.columns.get_loc('Diferencia')] = 0
                        historial['Color'] = historial['Diferencia'].apply(lambda x: '#2ecc71' if x >= 0 else '#e74c3c')
                        
                        datos_grafica = pd.DataFrame({
                            'Fecha': historial.index.strftime('%Y-%m-%d'),
                            'Precio Cierre ($)': historial['Close'].round(2),
                            'color': historial['Color']
                        })
                        
                        st.bar_chart(datos_grafica, x='Fecha', y='Precio Cierre ($)', color='color', use_container_width=True)
                    
                    st.divider()
                    
                    # --- APARTADO 2: AUDITORÍA ---
                    st.write("### 📋 Diagnóstico de Balances")
                    info = empresa.info
                    precio_actual = info.get('currentPrice') or info.get('navPrice') or info.get('previousClose') or 0
                    pe_ratio = info.get('trailingPE', float('inf')) or float('inf')
                    debt_to_equity = info.get('debtToEquity', 0) or 0
                    margin_neto = (info.get('profitMargins', 0) or 0) * 100
                    
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Precio Actual", f"${precio_actual}")
                    col2.metric("Ratio P/E", f"{pe_ratio if pe_ratio != float('inf') else 'N/A'}")
                    col3.metric("Margen Neto", f"{margin_neto:.2f}%")
                    col4.metric("Deuda / Capital", f"{debt_to_equity}%")
                    
                    puntuacion = 0
                    razones = []
                    
                    if pe_ratio != float('inf') and pe_ratio < 20:
                        puntuacion += 1
                        razones.append("La empresa cotiza a una valoración atractiva (P/E < 20).")
                    else:
                        razones.append("La valoración es alta o no registra ganancias (P/E > 20). Riesgo de sobreprecio.")
                        
                    if margin_neto > 15:
                        puntuacion += 1
                        razones.append("Excelente rentabilidad. Margen neto superior al 15%.")
                    else:
                        razones.append("Márgenes de ganancia ajustados o negativos (Menor al 15%).")
                        
                    if debt_to_equity < 100:
                        puntuacion += 1
                        razones.append("Nivel de deuda saludable y bajo control.")
                    else:
                        razones.append("Atención: La deuda supera el capital de la empresa.")
                    
                    for razon in razones:
                        st.write(f"- {razon}")
                        
                    if puntuacion == 3:
                        st.success("💥 RECOMENDACIÓN FINAL: COMPRA FUERTE (Oportunidad Value).")
                    elif puntuacion == 2:
                        st.warning("⚖️ RECOMENDACIÓN FINAL: MANTENER / VIGILAR (Precio justo).")
                    else:
                        st.error("❌ RECOMENDACIÓN FINAL: EVITAR / VENDER (Alto riesgo).")
                except Exception as e:
                    st.error(f"Error al obtener los datos detallados: {e}")
    else:
        st.error("❌ No se encontraron empresas con ese nombre en Wall Street. Intenta buscando su código Ticker directo (ej: 'AAPL' para Apple, 'TSLA' para Tesla, 'KO' para Coca-Cola).")
