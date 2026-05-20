import streamlit as st
from database.connection import init_db
from modules.auth import mostrar_login
from modules.registrar import formulario_producto, formulario_categoria, formulario_proveedor, formulario_sede
from modules.inventory import mostrar_inventario, gestionar_eliminacion
from modules.notifications import mostrar_notificaciones

st.set_page_config(page_title="Sistema Integral A3", page_icon="🛡️", layout="wide")

# Inicialización obligatoria de la base de datos
init_db()

if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    mostrar_login()
else:
    st.sidebar.markdown(f"### 👤 Operador Autenticado ID: `{st.session_state.user_id}`")
    st.sidebar.write("---")
    
    opcion = st.sidebar.selectbox("🎯 MENÚ TÉCNICO", [
        "📋 Ver mi Inventario",
        "🔔 Centro de Notificaciones",
        "📝 Registrar Producto", 
        "➕ Crear Categoría", 
        "➕ Crear Proveedor", 
        "➕ Crear Sede",
        "🗑️ Gestionar / Eliminar"
    ])
    
    st.sidebar.write("---")
    if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
        st.session_state.clear() 
        st.rerun()

    # Enrutador técnico de módulos
    if opcion == "📋 Ver mi Inventario": mostrar_inventario()
    elif opcion == "🔔 Centro de Notificaciones": mostrar_notificaciones()
    elif opcion == "📝 Registrar Producto": formulario_producto()
    elif opcion == "➕ Crear Categoría": formulario_categoria()
    elif opcion == "➕ Crear Proveedor": formulario_proveedor()
    elif opcion == "➕ Crear Sede": formulario_sede()
    elif opcion == "🗑️ Gestionar / Eliminar": gestionar_eliminacion()