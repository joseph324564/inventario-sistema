import streamlit as st
import pandas as pd
from datetime import datetime
from database.connection import get_connection

def formulario_categoria():
    st.subheader("📂 Registro de Categorías Propias")
    with st.container(border=True):
        n_cat = st.text_input("Nombre de la Categoría")
        if st.button("Guardar Categoría", type="primary"):
            if n_cat:
                with get_connection() as conn:
                    conn.execute("INSERT INTO categorias (user_id, nombre) VALUES (?, ?)", (st.session_state.user_id, n_cat))
                    conn.commit()
                st.success(f"✅ Categoría '{n_cat}' añadida a tu catálogo.")
            else: st.error("El campo no puede estar vacío.")

def formulario_proveedor():
    st.subheader("🚚 Registro de Proveedores")
    with st.container(border=True):
        n_prov = st.text_input("Razón Social")
        t_prov = st.text_input("Teléfono")
        no_nit = st.checkbox("No maneja NIT")
        nit_prov = "N/A" if no_nit else st.text_input("NIT")
        
        if st.button("Guardar Proveedor", type="primary"):
            if n_prov and t_prov:
                with get_connection() as conn:
                    conn.execute("INSERT INTO proveedores (user_id, nombre, contacto, nit) VALUES (?, ?, ?, ?)", 
                                 (st.session_state.user_id, n_prov, t_prov, nit_prov))
                    conn.commit()
                st.success(f"✅ Proveedor '{n_prov}' indexado.")
            else: st.error("Rellena los campos obligatorios.")

def formulario_sede():
    st.subheader("🏢 Registro de Sedes Locales")
    with st.container(border=True):
        n_sede = st.text_input("Nombre de la Sede")
        d_sede = st.text_input("Dirección")
        loc = st.selectbox("Ubicación Bogotá", ["Suba", "Kennedy", "Engativá", "Usaquén", "Otro"])
        
        if st.button("Guardar Sede", type="primary"):
            if n_sede and d_sede:
                with get_connection() as conn:
                    conn.execute("INSERT INTO sedes (user_id, nombre, direccion) VALUES (?, ?, ?)", 
                                 (st.session_state.user_id, n_sede, f"{d_sede} ({loc})"))
                    conn.commit()
                st.success(f"✅ Sede '{n_sede}' guardada.")

def formulario_producto():
    st.subheader("📝 Ficha Técnica de Registro de Activos")
    
    # CORRECCIÓN EXTRA: Las listas de selección solo muestran lo que este usuario creó
    with get_connection() as conn:
        cats = pd.read_sql(f"SELECT * FROM categorias WHERE user_id={st.session_state.user_id}", conn)
        provs = pd.read_sql(f"SELECT * FROM proveedores WHERE user_id={st.session_state.user_id}", conn)
        sedes = pd.read_sql(f"SELECT * FROM sedes WHERE user_id={st.session_state.user_id}", conn)

    if cats.empty or provs.empty or sedes.empty:
        st.warning("⚠️ Debes registrar primero al menos una Sede, Proveedor y Categoría en tu cuenta.")
        return

    with st.form("prod_form"):
        nom = st.text_input("Nombre del Activo")
        c_s = st.selectbox("Categoría", cats['nombre'])
        p_s = st.selectbox("Proveedor", provs['nombre'])
        s_s = st.selectbox("Sede de Destino", sedes['nombre'])
        vd = st.number_input("Ciclo de Vida Útil (Minutos sugeridos)", min_value=1, value=60)
        sr = st.text_input("Número de Serial Único")
        mr = st.text_input("Marca")
        
        if st.form_submit_button("Asegurar Registro en Servidor"):
            if nom and sr:
                c_id = int(cats[cats['nombre']==c_s]['id'].iloc[0])
                p_id = int(provs[provs['nombre']==p_s]['id'].iloc[0])
                s_id = int(sedes[sedes['nombre']==s_s]['id'].iloc[0])
                
                with get_connection() as conn:
                    cur = conn.cursor()
                    cur.execute("""INSERT INTO productos (user_id, cat_id, prov_id, sede_id, nombre, fecha_ingreso, vida_min) 
                                   VALUES (?,?,?,?,?,?,?)""",
                                (st.session_state.user_id, c_id, p_id, s_id, nom, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), vd))
                    cur.execute("INSERT INTO detalles (prod_id, serial, marca) VALUES (?,?,?)", (cur.lastrowid, sr, mr))
                    conn.commit()
                st.success(f"🚀 Activo '{nom}' vinculado a tu inventario.")