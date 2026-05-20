import streamlit as st
import re
import pyotp
import qrcode
import io
from database.connection import get_connection

def validar_password(password):
    if len(password) < 6: return False, "❌ Mínimo 6 caracteres."
    if not re.search(r"[A-Z]", password): return False, "❌ Falta una MAYÚSCULA."
    if not re.search(r"[0-9]", password): return False, "❌ Falta un NÚMERO."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False, "❌ Falta un CARÁCTER ESPECIAL."
    return True, ""

def mostrar_login():
    st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>🔐 Sistema de Gestión A3</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #6B7280;'>Módulo de Autenticación de Doble Factor (2FA)</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
    
    with tab1:
        with st.container(border=True):
            user = st.text_input("👤 Usuario", key="login_user").strip()
            pw = st.text_input("🔑 Contraseña", type="password", key="login_pw")
            
            if st.button("Verificar Identidad", type="primary", use_container_width=True):
                if user and pw:
                    with get_connection() as conn:
                        res = conn.execute("SELECT id, otp_secret FROM usuarios WHERE user=? AND pw=?", (user, pw)).fetchone()
                        if res:
                            st.session_state.temp_user_id = res[0]
                            st.session_state.temp_otp_secret = res[1]
                            st.session_state.paso_2fa = True
                            st.toast("🔑 Credenciales válidas. Ingrese su código 2FA.")
                        else:
                            st.error("Credenciales incorrectas.")
            
            if st.session_state.get('paso_2fa', False):
                st.write("---")
                st.warning("🔒 Verificación de Doble Factor Requerida.")
                token = st.text_input("🔢 Código de 6 dígitos de tu App Google Authenticator", key="input_token")
                
                if st.button("Confirmar Código 2FA", use_container_width=True):
                    totp = pyotp.TOTP(st.session_state.temp_otp_secret)
                    if totp.verify(token):
                        st.session_state.logged_in = True
                        st.session_state.user_id = st.session_state.temp_user_id
                        del st.session_state['paso_2fa']
                        st.success("Acceso Concedido.")
                        st.rerun()
                    else:
                        st.error("Código incorrecto o expirado.")

    with tab2:
        with st.container(border=True):
            new_user = st.text_input("👤 Nombre de Usuario", key="reg_user").strip()
            new_pw = st.text_input("🔑 Contraseña", type="password", key="reg_pw")
            correo = st.text_input("📧 Correo Electrónico (Obligatorio)", key="reg_mail").strip()
            telefono = st.text_input("📱 Número Telefónico (Obligatorio)", key="reg_phone").strip()
            
            if st.button("Registrar Cuenta y Generar QR Security", use_container_width=True, type="primary"):
                valido, msg = validar_password(new_pw)
                if not (new_user and new_pw and correo and telefono):
                    st.error("❌ Todos los campos son obligatorios para la auditoría de seguridad.")
                elif not valido:
                    st.error(msg)
                else:
                    secret_key = pyotp.random_base32()
                    with get_connection() as conn:
                        try:
                            conn.execute("""INSERT INTO usuarios (user, pw, correo, telefono, otp_secret) 
                                            VALUES (?, ?, ?, ?, ?)""", (new_user, new_pw, correo, telefono, secret_key))
                            conn.commit()
                            st.session_state.reg_exito = True
                            st.session_state.reg_secret = secret_key
                            st.session_state.reg_name = new_user
                        except:
                            st.warning("El usuario ya existe.")
            
            if st.session_state.get('reg_exito', False):
                st.write("---")
                st.success("🎉 ¡Fase 1 completada! Vincula tu cuenta:")
                totp_url = pyotp.totp.TOTP(st.session_state.reg_secret).provisioning_uri(
                    name=st.session_state.reg_name, issuer_name="Sistema_A3"
                )
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(totp_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buf = io.BytesIO()
                img.save(buf)
                st.image(buf.getvalue(), caption="Escanea este código QR en tu app Google Authenticator", width=220)
                st.info(f"Código manual en caso de fallas: `{st.session_state.reg_secret}`")