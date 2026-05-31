import streamlit as st

# Configuración básica de la página
st.set_page_config(page_title="Para mi Mom", page_icon="✈️")

# Sistema de contraseña simple
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets["password_secreta"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Por seguridad
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Ingresa la contraseña para entrar:", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Ingresa la contraseña para entrar:", type="password", on_change=password_entered, key="password")
        st.error("Contraseña incorrecta. Intenta de nuevo.")
        return False
    else:
        return True

# Aquí empieza tu página real
if check_password():
    st.title("Pagina de viajes")
    st.write("Bienvenida a tu página exclusiva. Aquí pondremos todas las funcionalidades que necesites.")
