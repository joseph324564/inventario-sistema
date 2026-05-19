import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd
import re

# --- CONFIGURACIÓN DE BASE DE DATOS ---
def init_db():
    conn = sqlite3.connect("sistema_integral.db")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    cur.execute("CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, user TEXT UNIQUE, pw TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS categorias (id INTEGER PRIMARY KEY, nombre TEXT)")
    # TABLA CORREGIDA CON NIT
    cur.execute("CREATE TABLE IF NOT EXISTS proveedores (id INTEGER PRIMARY KEY, nombre TEXT, contacto TEXT, nit TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS sedes (id INTEGER PRIMARY KEY, nombre TEXT, direccion TEXT)")
    
    cur.execute('''CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY, 
                    user_id INTEGER, cat_id INTEGER, prov_id INTEGER, sede_id INTEGER,
                    nombre TEXT, fecha_ingreso TEXT, vida_min INTEGER,
                    FOREIGN KEY(user_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    FOREIGN KEY(cat_id) REFERENCES categorias(id) ON DELETE CASCADE,
                    FOREIGN KEY(prov_id) REFERENCES proveedores(id) ON DELETE CASCADE,
                    FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE)''')
    
    cur.execute("CREATE TABLE IF NOT EXISTS detalles (id INTEGER PRIMARY KEY, prod_id INTEGER UNIQUE, serial TEXT, marca TEXT, FOREIGN KEY(prod_id) REFERENCES productos(id) ON DELETE CASCADE)")
    
    conn.commit()
    conn.close()

def validar_password(password):
    if len(password) < 6: return False, "❌ Mínimo 6 caracteres."
    if not re.search(r"[A-Z]", password): return False, "❌ Falta una MAYÚSCULA."
    if not re.search(r"[0-9]", password): return False, "❌ Falta un NÚMERO."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False, "❌ Falta un CARÁCTER ESPECIAL."
    return True, ""

init_db()

# --- SESIÓN ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- INTERFAZ ACCESO ---
if not st.session_state.logged_in:
    st.title("🔐 Acceso Sistema A3")
    user = st.text_input("Usuario").strip()
    pw = st.text_input("Contraseña", type="password")
    c1, c2 = st.columns(2)
    
    if c1.button("Iniciar Sesión"):
        with sqlite3.connect("sistema_integral.db") as conn:
            res = conn.execute("SELECT id FROM usuarios WHERE user=? AND pw=?", (user, pw)).fetchone()
            if res:
                st.session_state.logged_in = True
                st.session_state.user_id = res[0]
                st.rerun()
            else: st.error("Error de acceso.")

    if c2.button("Registrar Usuario"):
        st.info("Políticas: 6+ caracteres, Mayúscula, Número y Símbolo (@#$).")
        valido, msg = validar_password(pw)
        if not valido: st.error(msg)
        else:
            with sqlite3.connect("sistema_integral.db") as conn:
                try:
                    conn.execute("INSERT INTO usuarios (user, pw) VALUES (?,?)", (user, pw))
                    conn.commit()
                    st.success("✅ ¡Creado!")
                except: st.warning("Ya existe.")

# --- PANEL DE CONTROL ---
else:
    st.sidebar.title(f"Usuario ID: {st.session_state.user_id}")
    opcion = st.sidebar.selectbox("Menú", [
        "Registrar Producto", 
        "Ver mi Inventario", 
        "➕ Crear Categoría", 
        "➕ Crear Proveedor", 
        "➕ Crear Sede",
        "🗑️ Gestionar / Eliminar"
    ])

    with sqlite3.connect("sistema_integral.db") as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        
        # --- SECCIONES DE CREACIÓN (Categoría, Proveedor, Sede) ---
        if opcion == "➕ Crear Categoría":
            st.header("📂 Nueva Categoría")
            n_cat = st.text_input("Nombre")
            if st.button("Guardar"):
                conn.execute("INSERT INTO categorias (nombre) VALUES (?)", (n_cat,))
                conn.commit()
                st.success("Añadida.")

        elif opcion == "➕ Crear Proveedor":
            st.header("🚚 Nuevo Proveedor")
            n_prov = st.text_input("Nombre")
            t_prov = st.text_input("Teléfono")
            no_nit = st.checkbox("No tiene NIT")
            nit_prov = "N/A" if no_nit else st.text_input("NIT")
            if st.button("Guardar"):
                conn.execute("INSERT INTO proveedores (nombre, contacto, nit) VALUES (?,?,?)", (n_prov, t_prov, nit_prov))
                conn.commit()
                st.success("Proveedor guardado.")

        elif opcion == "➕ Crear Sede":
            st.header("🏢 Nueva Sede")
            n_sede = st.text_input("Nombre")
            d_sede = st.text_input("Dirección")
            loc = st.selectbox("Localidad", ["Suba", "Kennedy", "Engativá", "Usaquén", "Otro"])
            if st.button("Guardar"):
                conn.execute("INSERT INTO sedes (nombre, direccion) VALUES (?,?)", (n_sede, f"{d_sede} ({loc})"))
                conn.commit()
                st.success("Sede guardada.")

        # --- REGISTRAR PRODUCTO ---
        elif opcion == "Registrar Producto":
            st.header("📝 Registrar Producto")
            cats = pd.read_sql("SELECT * FROM categorias", conn)
            provs = pd.read_sql("SELECT * FROM proveedores", conn)
            sedes = pd.read_sql("SELECT * FROM sedes", conn)

            if cats.empty or provs.empty or sedes.empty:
                st.warning("Faltan datos base (Sede, Proveedor o Categoría).")
            else:
                with st.form("prod"):
                    nom = st.text_input("Nombre")
                    c_s = st.selectbox("Categoría", cats['nombre'])
                    p_s = st.selectbox("Proveedor", provs['nombre'])
                    s_s = st.selectbox("Sede", sedes['nombre'])
                    vd = st.number_input("Vida (Min)", 1)
                    sr = st.text_input("Serial")
                    mr = st.text_input("Marca")
                    if st.form_submit_button("Guardar"):
                        c_id = int(cats[cats['nombre']==c_s]['id'].iloc[0])
                        p_id = int(provs[provs['nombre']==p_s]['id'].iloc[0])
                        s_id = int(sedes[sedes['nombre']==s_s]['id'].iloc[0])
                        cur = conn.cursor()
                        cur.execute("INSERT INTO productos (user_id, cat_id, prov_id, sede_id, nombre, fecha_ingreso, vida_min) VALUES (?,?,?,?,?,?,?)",
                                    (st.session_state.user_id, c_id, p_id, s_id, nom, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), vd))
                        cur.execute("INSERT INTO detalles (prod_id, serial, marca) VALUES (?,?,?)", (cur.lastrowid, sr, mr))
                        conn.commit()
                        st.success("Producto registrado.")

        # --- VER INVENTARIO ---
        elif opcion == "Ver mi Inventario":
            st.header("🕵️ Inventario")
            df = pd.read_sql(f"SELECT p.*, c.nombre as cat, s.nombre as sd, d.serial FROM productos p JOIN categorias c ON p.cat_id=c.id JOIN sedes s ON p.sede_id=s.id JOIN detalles d ON p.id=d.prod_id WHERE p.user_id={st.session_state.user_id}", conn)
            for _, r in df.iterrows():
                ing = datetime.strptime(r['fecha_ingreso'], "%Y-%m-%d %H:%M:%S")
                pct = ((datetime.now()-ing).total_seconds()/60/r['vida_min'])*100
                with st.expander(f"{r['nombre']} - {r['cat']}"):
                    st.write(f"Sede: {r['sd']} | Serial: {r['serial']}")
                    st.progress(min(pct/100, 1.0))

        # --- NUEVA SECCIÓN: GESTIONAR / ELIMINAR ---
        elif opcion == "🗑️ Gestionar / Eliminar":
            st.header("🗑️ Zona de Borrado")
            tab1, tab2, tab3, tab4 = st.tabs(["Productos", "Categorías", "Proveedores", "Sedes"])
            
            with tab1:
                prods = pd.read_sql(f"SELECT id, nombre FROM productos WHERE user_id={st.session_state.user_id}", conn)
                if not prods.empty:
                    p_del = st.selectbox("Selecciona Producto a eliminar", prods['nombre'], key="del_p")
                    if st.button("Eliminar Producto", color="red"):
                        p_id = int(prods[prods['nombre']==p_del]['id'].iloc[0])
                        conn.execute("DELETE FROM productos WHERE id=?", (p_id,))
                        conn.commit()
                        st.rerun()
                else: st.write("No hay productos.")

            with tab2:
                cats = pd.read_sql("SELECT * FROM categorias", conn)
                c_del = st.selectbox("Selecciona Categoría", cats['nombre'], key="del_c")
                if st.button("Eliminar Categoría"):
                    conn.execute("DELETE FROM categorias WHERE nombre=?", (c_del,))
                    conn.commit()
                    st.rerun()

            with tab3:
                provs = pd.read_sql("SELECT * FROM proveedores", conn)
                pr_del = st.selectbox("Selecciona Proveedor", provs['nombre'], key="del_pr")
                if st.button("Eliminar Proveedor"):
                    conn.execute("DELETE FROM proveedores WHERE nombre=?", (pr_del,))
                    conn.commit()
                    st.rerun()

            with tab4:
                seds = pd.read_sql("SELECT * FROM sedes", conn)
                s_del = st.selectbox("Selecciona Sede", seds['nombre'], key="del_s")
                if st.button("Eliminar Sede"):
                    conn.execute("DELETE FROM sedes WHERE nombre=?", (s_del,))
                    conn.commit()
                    st.rerun()

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.logged_in = False
        st.rerun()