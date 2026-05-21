import streamlit as st
from database.connection import get_connection


def _validar_usuario(usuario: str, contrasena: str):
    if not usuario or not contrasena:
        return None

    with get_connection() as conn:
        fila = conn.execute(
            "SELECT id, pw FROM usuarios WHERE user = ?",
            (usuario,),
        ).fetchone()

    if fila and fila[1] == contrasena:
        return fila[0]

    return None


def _crear_usuario(usuario: str, contrasena: str, correo: str, telefono: str):
    if not usuario or not contrasena or not correo or not telefono:
        st.error("Completa todos los campos de registro.")
        return False

    with get_connection() as conn:
        existente = conn.execute(
            "SELECT id FROM usuarios WHERE user = ?",
            (usuario,),
        ).fetchone()
        if existente:
            st.error("El usuario ya existe. Elige otro nombre de usuario.")
            return False

        conn.execute(
            "INSERT INTO usuarios (user, pw, correo, telefono, otp_secret) VALUES (?, ?, ?, ?, ?)",
            (usuario, contrasena, correo, telefono, ""),
        )
        conn.commit()

    st.success("Cuenta creada con éxito. Inicia sesión para continuar.")
    return True


def mostrar_registro(prefill_usuario: str = ""):
    st.subheader("📝 Registro de Operador")
    with st.form("registro_form"):
        usuario = st.text_input("Usuario", value=prefill_usuario)
        contrasena = st.text_input("Contraseña", type="password")
        correo = st.text_input("Correo electrónico")
        telefono = st.text_input("Teléfono")
        guardar = st.form_submit_button("Crear cuenta")

    if guardar:
        if _crear_usuario(usuario, contrasena, correo, telefono):
            st.experimental_rerun()


def mostrar_login():
    st.title("🔐 Acceso al Sistema Integral A3")
    st.write("Introduce tus credenciales para ingresar al inventario.")

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        contrasena = st.text_input("Contraseña", type="password")
        col1, col2 = st.columns([1, 1])
        iniciar = col1.form_submit_button("Iniciar sesión")
        registrar = col2.form_submit_button("Registrar cuenta")

    if iniciar:
        usuario_id = _validar_usuario(usuario, contrasena)
        if usuario_id:
            st.session_state.user_id = usuario_id
            st.session_state.logged_in = True
            st.success("Sesión iniciada correctamente. Redirigiendo...")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos.")

    if registrar:
        mostrar_registro(prefill_usuario=usuario)
