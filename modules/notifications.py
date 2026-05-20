import streamlit as st
import pandas as pd
from datetime import datetime
from database.connection import get_connection

def mostrar_notificaciones():
    st.header("🔔 Centro de Control de Alertas Próximas a Vencer")
    st.write("Filtro de seguridad en tiempo real por operador logístico.")
    
    with get_connection() as conn:
        df = pd.read_sql("""
            SELECT p.nombre, p.fecha_ingreso, p.vida_min, c.nombre as cat, s.nombre as sd
            FROM productos p
            JOIN categorias c ON p.cat_id = c.id
            JOIN sedes s ON p.sede_id = s.id
            WHERE p.user_id = ?""", conn, params=(st.session_state.user_id,))
            
    if df.empty:
        st.info("No registras activos en tu base de datos. Historial limpio.")
        return
        
    proximos = []
    vencidos = []
    
    for _, r in df.iterrows():
        ing = datetime.strptime(r['fecha_ingreso'], "%Y-%m-%d %H:%M:%S")
        transcurridos = (datetime.now() - ing).total_seconds() / 60
        pct = (transcurridos / r['vida_min']) * 100
        
        datos = {"nombre": r['nombre'], "cat": r['cat'], "sede": r['sd'], "pct": min(int(pct), 100)}
        
        if pct >= 100:
            vencidos.append(datos)
        elif pct >= 80:
            proximos.append(datos)
            
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("⚠️ Alertas de Desgaste Crítico (>= 80%)")
        if proximos:
            for item in proximos:
                with st.container(border=True):
                    st.markdown(f"**📦 Activo:** {item['nombre']} ({item['cat']})")
                    st.markdown(f"🏢 **Ubicación asignada:** {item['sede']}")
                    st.error(f"Alerta: {item['pct']}% de su vida útil consumida.")
        else:
            st.success("✅ Todo bajo control. No tienes activos próximos a expirar.")
            
    with c2:
        st.subheader("🚨 Activos Expirados (100% Consumidos)")
        if vencidos:
            for item in vencidos:
                with st.container(border=True):
                    st.markdown(f"**🔴 NOMBRE:** {item['nombre']}")
                    st.markdown(f"🏢 **Ubicación:** {item['sede']}")
                    st.markdown("<span style='color:red; font-weight:bold;'>OBSOLESCENCIA: Requiere retiro o renovación inmediata.</span>", unsafe_allow_html=True)
        else:
            st.success("✅ Excelente. Cero pérdidas por expiración total.")