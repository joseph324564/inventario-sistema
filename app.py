import streamlit as st
from database.connection import init_db
from modules.auth import mostrar_login
from modules.registrar import formulario_producto, formulario_categoria, formulario_proveedor, formulario_sede
from modules.inventory import mostrar_inventario, gestionar_eliminacion
from modules.notifications import mostrar_notificaciones # Nueva importación añadida

st.set_page_config(page_title="Sistema Integral A3", page_icon="🛡️", layout="wide")

# Inicialización estructural de tablas
init_db()

if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    mostrar_login()
else:
    st.sidebar.markdown(f"### 👤 Operador Autenticado ID: `{st.session_state.user_id}`")
    st.sidebar.write("---")
    
    # Menú técnico actualizado con el módulo de notificaciones
    opcion = st.sidebar.selectbox("🎯 MENÚ TÉCNICO", [
        "📋 Ver mi Inventario",
        "🔔 Centro de Notificaciones", # Nueva Opción
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

    # Enrutador técnico
    if opcion == "📋 Ver mi Inventario": mostrar_inventario()
    elif opcion == "🔔 Centro de Notificaciones": mostrar_notificaciones() # Ruta de ejecución
    elif opcion == "📝 Registrar Producto": formulario_producto()
    elif opcion == "➕ Crear Categoría": formulario_categoria()
    elif opcion == "➕ Crear Proveedor": formulario_proveedor()
    elif opcion == "➕ Crear Sede": formulario_sede()
    elif opcion == "🗑️ Gestionar / Eliminar": gestionar_eliminacion()