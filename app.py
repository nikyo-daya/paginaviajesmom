import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Conectar a Supabase usando las llaves secretas
url = st.secrets["https://zeabysvgtvvxpjvcijpy.supabase.co/rest/v1/"]
key = st.secrets["sb_publishable_eL95IB4Fjkq1Q-2A0jc2kg_zrn_rbGh"]
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

# Aquí empieza tu página real
if check_password():
    st.title("🚐 Administrador de Viajes")
    
    # --- SECCIÓN 1: DATOS DEL VIAJE ---
    st.subheader("1. Detalles del Destino")
    destino = st.text_input("¿A dónde vamos?")
    
    col1, col2 = st.columns(2) # Esto divide la pantalla en dos columnas
    with col1:
        fecha_salida = st.date_input("Fecha de salida")
    with col2:
        fecha_regreso = st.date_input("Fecha de regreso")

    st.divider() # Línea separadora

    # --- SECCIÓN 2: VEHÍCULO Y ASIENTOS (LA MATRIZ) ---
    st.subheader("2. Transporte y Asientos")
    
    # Menú desplegable para elegir el bus
    vehiculo = st.selectbox(
        "Elige el vehículo:", 
        ["Bus de 11 filas", "Bus de 12 filas", "Bus de 13 filas", "Microbús", "Bus de viaje (Amarillo)"]
    )
    
    st.write("**Mapa de Asientos:** Escribe el nombre para ocupar el asiento, o déjalo vacío si está libre.")
    
    # Lógica para crear la matriz de asientos dependiendo del bus
    filas = 11
    if "12" in vehiculo: filas = 12
    elif "13" in vehiculo: filas = 13
    elif "Microbús" in vehiculo: filas = 5 # Ejemplo más pequeño
    
    # Creamos una tabla vacía
    tabla_asientos = pd.DataFrame(
        [["" for _ in range(4)] for _ in range(filas)], 
        columns=["Ventana Izq.", "Pasillo Izq.", "Pasillo Der.", "Ventana Der."]
    )
    
    # st.data_editor hace que la tabla sea interactiva ¡Tu mamá puede escribir directamente en ella!
    matriz_interactiva = st.data_editor(tabla_asientos, use_container_width=True)

    st.divider()

    # --- SECCIÓN 3: CONTROL DE PAGOS ---
    st.subheader("3. Finanzas y Pagos")
    st.write("Agrega a los pasajeros. Llena el Total, Pago 1 y Pago 2. ¡El sistema calcula el resto solo!")
    
    # Creamos una tabla base para los cobros
    tabla_pagos = pd.DataFrame(
        columns=["Pasajero", "Total a Pagar (Q)", "1er Pago", "2do Pago"]
    )
    
    # num_rows="dynamic" le pone un botón con un "+" para que tu mamá agregue cuantas filas quiera
    pagos_ingresados = st.data_editor(tabla_pagos, num_rows="dynamic", use_container_width=True)
    
    # --- CÁLCULOS MATEMÁTICOS AUTOMÁTICOS ---
    if not pagos_ingresados.empty:
        # Convertimos los espacios vacíos en ceros para poder sumar
        pagos_ingresados = pagos_ingresados.fillna(0) 
        
        # Le decimos a Python cómo calcular las sumas y las restas
        pagos_ingresados["Total Pagado"] = pagos_ingresados["1er Pago"] + pagos_ingresados["2do Pago"]
        pagos_ingresados["Falta por Pagar"] = pagos_ingresados["Total a Pagar (Q)"] - pagos_ingresados["Total Pagado"]
        
        st.write("**💰 Resumen de Cuentas (Actualizado automáticamente):**")
        # st.dataframe muestra una tabla de solo lectura para ver los resultados
        st.dataframe(pagos_ingresados, use_container_width=True)
        st.divider()
    
    # --- SECCIÓN 4: GALERÍA DEL VIAJE ---
    st.subheader("4. Recuerdos del Viaje 📸")
    st.write("Sube las fotos de este destino para guardarlas en el historial.")
    
    # Esto crea un botón que abre la galería del celular o el explorador de archivos
    fotos_subidas = st.file_uploader("Selecciona tus fotos", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if fotos_subidas:
        st.success(f"¡Has seleccionado {len(fotos_subidas)} fotos listas para guardar!")
        # Aquí es donde pondremos la magia para enviarlas a la base de datos