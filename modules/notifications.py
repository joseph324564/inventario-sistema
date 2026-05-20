import streamlit as st
import pandas as pd
from datetime import datetime
from database.connection import get_connection

def mostrar_notificaciones():
    st.header("🔔 Centro de Alertas y Notificaciones")
    st.write("Análisis en tiempo real de ciclos de vida útil por operador.")
    
    with get_connection() as conn:
        df = pd.read_sql(f"""
            SELECT p.nombre, p.fecha_ingreso, p.vida_min, c.nombre as cat, s.nombre as sd
            FROM productos p
            JOIN categorias c ON p.cat_id = c.id
            JOIN sedes s ON p.sede_id = s.id
            WHERE p.user_id = ?""", conn, params=(st.session_state.user_id,))
            
    if df.empty:
        st.info("No posees activos indexados. El centro de alertas está limpio.")
        return
        
    proximos = []
    vencidos = []
    
    # Procesar métricas temporales de desgaste
    for _, r in df.iterrows():
        ing = datetime.strptime(r['fecha_ingreso'], "%Y-%m-%d %H:%M:%S")
        minutos_transcurridos = (datetime.now() - ing).total_seconds() / 60
        pct = (minutos_transcurridos / r['vida_min']) * 100
        
        info_activo = {
            "nombre": r['nombre'],
            "cat": r['cat'],
            "sede": r['sd'],
            "pct": min(int(pct), 100)
        }
        
        if pct >= 100:
            vencidos.append(info_activo)
        elif pct >= 80:
            proximos.append(info_activo)
            
    # --- RENDERIZACIÓN DE ALERTAS AISLADAS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚠️ Próximos a Vencer (>= 80% Uso)")
        if proximos:
            for item in proximos:
                with st.container(border=True):
                    st.markdown(f"**📦 Activo:** {item['nombre']} ({item['cat']})")
                    st.markdown(f"🏢 **Ubicación:** {item['sede']}")
                    st.error(f"Capacidad operativa crítica: {item['pct']}% consumida.")
        else:
            st.success("✅ No tienes productos en rango crítico de desgaste (80%).")
            
    with col2:
        st.subheader("🚨 Activos Vencidos (100% Agotados)")
        if vencidos:
            for item in vencidos:
                with st.container(border=True):
                    st.markdown(f"**🔴 Activo Agotado:** {item['nombre']}")
                    st.markdown(f"🏢 **Ubicación:** {item['sede']}")
                    st.markdown("<span style='color:red; font-weight:bold;'>REEMPLAZO OBLIGATORIO: Vida útil agotada por completo.</span>", unsafe_allow_html=True)
        else:
            st.success("✅ No tienes productos vencidos.")