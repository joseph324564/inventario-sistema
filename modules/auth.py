import streamlit as st
import pandas as pd
from DataBase.connection import init_db, get_connection
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
        "🗑️ Gestionar / Eliminar",
        "🖥️ Consola DB (Profesor)"
    ])
    
    st.sidebar.write("---")
    if st.sidebar.button("🔒 Cerrar Sesión", use_container_width=True):
        st.session_state.clear() 
        st.rerun()

    # Enrutador técnico de módulos
    if opcion == "📋 Ver mi Inventario": 
        mostrar_inventario()
        
    elif opcion == "🔔 Centro de Notificaciones": 
        mostrar_notificaciones()
        
    elif opcion == "📝 Registrar Producto": 
        formulario_producto()
        
    elif opcion == "➕ Crear Categoría": 
        formulario_categoria()
        
    elif opcion == "➕ Crear Proveedor": 
        formulario_proveedor()
        
    elif opcion == "➕ Crear Sede": 
        formulario_sede()
        
    elif opcion == "🗑️ Gestionar / Eliminar": 
        gestionar_eliminacion()
        
    elif opcion == "🖥️ Consola DB (Profesor)":
        st.header("🖥️ Centro de Control y Auditoría de Base de Datos")
        st.write("Herramientas avanzadas de inspección del motor relacional SQLite en el entorno Cloud.")
        
        # Validar credencial maestra solicitada por el usuario
        clave_maestra = st.text_input("🔑 Ingrese la clave de acceso de auditoría:", type="password")
        
        if clave_maestra == "Admin343":
            st.success("🔓 Acceso de auditoría concedido. Modo Administrador Activo.")
            st.write("---")
            
            pestana1, pestana2, pestana3 = st.tabs([
                "📊 Consultas Rápidas (SELECT)", 
                "🔍 Inspección del Sistema (Metadatos)", 
                "📐 Esquema de Relaciones (PRAGMA)"
            ])
            
            # PESTAÑA 1: SELECT FROM DINÁMICO
            with pestana1:
                st.subheader("📋 Consultor Dinámico de Tablas")
                tabla_seleccionada = st.selectbox(
                    "Seleccione la tabla física a consultar en caliente:", 
                    ["usuarios", "categorias", "proveedores", "sedes", "productos", "detalles"]
                )
                
                with get_connection() as conn:
                    try:
                        df_query = pd.read_sql(f"SELECT * FROM {tabla_seleccionada}", conn)
                        st.markdown(f"**Query ejecutado internamente:** `SELECT * FROM {tabla_seleccionada};`")
                        if df_query.empty:
                            st.info(f"La tabla '{tabla_seleccionada}' se encuentra estructurada pero actualmente no contiene registros.")
                        else:
                            st.dataframe(df_query, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error en la consulta: {e}")
            
            # PESTAÑA 2: SQLITE_MASTER
            with pestana2:
                st.subheader("🔍 Estructura Interna del Archivo .db")
                st.write("Este comando demuestra la existencia física y la declaración formal de objetos dentro de SQLite.")
                
                if st.button("Ejecutar Consulta de Tabla Maestra", type="primary"):
                    with get_connection() as conn:
                        try:
                            df_master = pd.read_sql("SELECT type, name, tbl_name, sql FROM sqlite_master WHERE type='table';", conn)
                            st.markdown("**Query ejecutado internamente:** `SELECT name, sql FROM sqlite_master WHERE type='table';`")
                            st.dataframe(df_master, use_container_width=True)
                        except Exception as e:
                            st.error(f"Error al leer metadatos: {e}")
                            
            # PESTAÑA 3: PRAGMA TABLE_INFO Y INTEGR