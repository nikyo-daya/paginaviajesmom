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

# Aquí empieza tu página real
if check_password():
    st.title("Administrador de Viajes")
    
    # --- SECCIÓN 1: DATOS DEL VIAJE ---
    st.subheader("Detalles del Viaje")
    destino = st.text_input("¿A dónde vamos?")
    
    col1, col2 = st.columns(2) # Esto divide la pantalla en dos columnas
    with col1:
        fecha_salida = st.date_input("Fecha de salida")
    with col2:
        fecha_regreso = st.date_input("Fecha de regreso")

    st.divider() # Línea separadora

    # --- SECCIÓN 2: VEHÍCULO Y ASIENTOS (LA MATRIZ) ---
    st.subheader("Transporte y Asientos")
    
    # Menú desplegable para elegir el bus
    vehiculo = st.selectbox(
        "Elige el vehículo:", 
        ["Bus de 11 filas", "Bus de 12 filas", "Bus de 13 filas", "Microbús", "Bus de viaje (Amarillo)"]
    )
    
    st.write("**Mapa de Asientos**")
    
    # Lógica para crear la matriz de asientos dependiendo del bus
    filas = 11
    if "12" in vehiculo: filas = 12
    elif "13" in vehiculo: filas = 13
    elif "Microbús" in vehiculo: filas = 5 # Ejemplo más pequeño
    
    # Creamos una tabla vacía
    tabla_asientos = pd.DataFrame(
        [["" for _ in range(5)] for _ in range(filas)], 
        columns=["Asiento Izq. V", "Asiento Izq. C", "Pasillo Centro", "Asiento Der. C", "Asiento Der. V"]
    )
    st.write("V = Ventana, C = Centro")
    
    # st.data_editor hace que la tabla sea interactiva ¡Tu mamá puede escribir directamente en ella!
    matriz_interactiva = st.data_editor(tabla_asientos, use_container_width=True)

    st.divider()

    # --- SECCIÓN 3: CONTROL DE PAGOS ---
    st.subheader("Finanzas y Pagos")
    st.write("Agrega a los pasajeros.")
    
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
        
        st.write("**Resumen de Cuentas (Actualizado automáticamente):**")
        # st.dataframe muestra una tabla de solo lectura para ver los resultados
        st.dataframe(pagos_ingresados, use_container_width=True)
        st.divider()
    
    # --- SECCIÓN 4: GALERÍA DEL VIAJE ---
    st.subheader("Recuerdos del Viaje ")
    st.write("Estas fotos son el recuerdo de un viaje increíble.")
    
    # Esto crea un botón que abre la galería del celular o el explorador de archivos
    fotos_subidas = st.file_uploader("Selecciona tus fotos", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    
    if fotos_subidas:
        st.success(f"¡Has seleccionado {len(fotos_subidas)} fotos listas para guardar!")
        # Aquí es donde pondremos la magia para enviarlas a la base de datos


 #  ---SECCION 5: GUARDAR DATOS EN SUPABASE ---
 
st.divider()
st.subheader("Guardar Datos en la Base de Datos")   
if st.button("Guardar Viaje"):
        # Aquí es donde escribiríamos la lógica para guardar los datos en Supabase
        st.success("¡Datos guardados exitosamente en la base de datos!")

        if st.button("Guardar Viaje Completo"):
    
    # 1. Empaquetamos los datos principales del viaje
         datos_del_viaje = {
        "destino": destino,
        "fecha_salida": str(fecha_salida), # Convertimos la fecha a texto
        "fecha_regreso": str(fecha_regreso),
        "vehiculo": vehiculo
    }
    
    # 2. Convertimos tu tabla de pagos a un formato que Supabase entienda (Diccionarios)
datos_pagos = pagos_ingresados.to_dict(orient="records")
    
    # 3. Enviamos los datos a Supabase
try:
        # Guardamos el viaje en una tabla llamada 'viajes' (que debes crear en Supabase)
        respuesta_viaje = supabase.table("viajes").insert(datos_del_viaje).execute()
        
        st.success("¡El viaje se guardó correctamente!")
        st.balloons() # ¡Un poco de celebración visual!
        
except Exception as e:
        st.error(f"Hubo un error al guardar: {e}")

        st.subheader("Historial de Viajes Guardados")

# 1. Traemos la lista de todos los viajes desde Supabase
viajes_guardados = supabase.table("viajes").select("*").execute()

if viajes_guardados.data:
    # 2. Creamos una lista con los nombres de los destinos para el menú
    opciones = [viaje["destino"] for viaje in viajes_guardados.data]
    viaje_seleccionado = st.selectbox("Selecciona un viaje para revisar:", opciones)
    
    # 3. Aquí buscarías los asientos y pagos que corresponden a ESE viaje seleccionado
    # y los mostrarías en la pantalla.