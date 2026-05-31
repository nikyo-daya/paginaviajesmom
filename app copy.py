import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Conectar a Supabase usando las llaves secretas
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# Configuración básica de la página
st.set_page_config(page_title="Administración de Viajes", page_icon="✈️")

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

if check_password():
    st.title("Administrador de Viajes")

    # --- SECCIÓN 1: DATOS DEL VIAJE ---
    st.subheader("Detalles del Viaje")
    destino = st.text_input("¿A dónde vamos?")

    col1, col2 = st.columns(2)
    with col1:
        fecha_salida = st.date_input("Fecha de salida")
    with col2:
        fecha_regreso = st.date_input("Fecha de regreso")

    st.divider()

    # --- SECCIÓN 2: VEHÍCULO Y ASIENTOS (LA MATRIZ) ---
    st.subheader("Transporte y Asientos")

    vehiculo = st.selectbox(
        "Elige el vehículo:",
        ["Bus de 11 filas", "Bus de 12 filas", "Bus de 13 filas", "Microbús", "Bus de viaje (Amarillo)"]
    )

    filas = 11
    if "12" in vehiculo:
        filas = 12
    elif "13" in vehiculo:
        filas = 13
    elif "Microbús" in vehiculo:
        filas = 5

    st.write("**Selecciona los asientos para los pasajeros:**")

    for i in range(filas):
        col1, col2, pasillo, col3, col4 = st.columns([1, 1, 0.5, 1, 1])
        with col1:
            st.checkbox(f"💺 {i+1}A", key=f"{i}_A")
        with col2:
            st.checkbox(f"💺 {i+1}B", key=f"{i}_B")
        with pasillo:
            st.write(" ")
        with col3:
            st.checkbox(f"💺 {i+1}C", key=f"{i}_C")
        with col4:
            st.checkbox(f"💺 {i+1}D", key=f"{i}_D")

    st.divider()

    asientos_seleccionados = []
    for key, value in st.session_state.items():
        if value is True and key.endswith(('_A', '_B', '_C', '_D')):
            asientos_seleccionados.append(key.replace("_", ""))

    st.info(f"Asientos seleccionados actualmente: {', '.join(asientos_seleccionados)}")

    st.divider()

    # --- SECCIÓN 3: CONTROL DE PAGOS ---
    st.subheader("Finanzas y Pagos")
    st.write("Agrega a los pasajeros.")

    tabla_pagos = pd.DataFrame(
        columns=["Pasajero", "Total a Pagar (Q)", "1er Pago", "2do Pago"]
    )

    pagos_ingresados = st.data_editor(tabla_pagos, num_rows="dynamic", use_container_width=True)

    if not pagos_ingresados.empty:
        pagos_ingresados = pagos_ingresados.fillna(0)
        pagos_ingresados["Total Pagado"] = pagos_ingresados["1er Pago"] + pagos_ingresados["2do Pago"]
        pagos_ingresados["Falta por Pagar"] = pagos_ingresados["Total a Pagar (Q)"] - pagos_ingresados["Total Pagado"]

        st.write("**Resumen de Cuentas (Actualizado automáticamente):**")
        st.dataframe(pagos_ingresados, use_container_width=True)
        st.divider()

    # --- SECCIÓN 4: GALERÍA DEL VIAJE ---
    st.subheader("Recuerdos del Viaje")
    st.write("Estas fotos son el recuerdo de un viaje increíble.")

    fotos_subidas = st.file_uploader("Selecciona tus fotos", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    if fotos_subidas:
        st.success(f"¡Has seleccionado {len(fotos_subidas)} fotos listas para guardar!")
        # Aquí es donde pondremos la magia para enviarlas a la base de datos
