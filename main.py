import streamlit as st
import pandas as pd
import datetime

# Configuración inicial de la página
st.set_page_config(page_title="Car Wash Control", page_icon="🧼", layout="wide")

# --- DISEÑO PERSONALIZADO (CSS) PARA AGRANDAR EL MENÚ LATERAL ---
st.html("""
    <style>
        /* Agranda el título de la barra lateral */
        [data-testid="stSidebarNav"]::before {
            font-size: 24px !important;
        }
        /* Agranda el texto de las opciones de radio en la barra lateral */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            font-size: 20px !important;
            padding-top: 10px !important;
            padding-bottom: 10px !important;
        }
        /* Incrementa el tamaño de los iconos o elementos interactivos adyacentes */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
            gap: 12px !important;
        }
    </style>
""")

# Estructura de navegación en la barra lateral (Se eliminó Inventario)
st.sidebar.title("🧼 Car Wash Manager")
opcion = st.sidebar.radio("Selecciona una pantalla:", ["Inicio", "Registro de Servicio", "Reporte de Ventas"])

# Inicialización de la base de datos simulada en la sesión de Streamlit
if 'servicios' not in st.session_state:
    st.session_state.servicios = pd.DataFrame(
        columns=["Fecha", "Cliente", "Vehículo", "Placas", "Tipo de Lavado", "Precio ($)", "Estatus"])

# ----------------- PANTALLA: INICIO -----------------
if opcion == "Inicio":
    st.title("📊 Panel de Control General")
    st.write("Bienvenido al sistema de gestión de tu centro de lavado de autos.")

    # Métricas clave en tarjetas
    col1, col2, col3 = st.columns(3)
    with col1:
        total_servicios = len(st.session_state.servicios)
        st.metric(label="Servicios Totales Hoy", value=total_servicios)
    with col2:
        ganancias_totales = st.session_state.servicios["Precio ($)"].sum()
        st.metric(label="Ingresos Totales", value=f"${ganancias_totales:,.2f}")
    with col3:
        pendientes = len(st.session_state.servicios[st.session_state.servicios["Estatus"] == "En Proceso"])
        st.metric(label="Autos en Lavado (En Proceso)", value=pendientes)

    st.subheader("🚗 Autos en Lavado Actualmente")

    # Filtrar solo los autos que están "En Proceso"
    autos_en_proceso = st.session_state.servicios[st.session_state.servicios["Estatus"] == "En Proceso"]

    if not autos_en_proceso.empty:
        # Encabezados de la lista
        enc1, enc2, enc3, enc4, enc5, enc6 = st.columns([2, 2, 1.5, 2, 1.5, 1.5])
        enc1.markdown("**Cliente**")
        enc2.markdown("**Vehículo**")
        enc3.markdown("**Placas**")
        enc4.markdown("**Tipo**")
        enc5.markdown("**Precio**")
        enc6.markdown("**Acción**")
        st.divider()

        # Iterar sobre cada auto activo
        for indice, fila in autos_en_proceso.iterrows():
            c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 1.5, 2, 1.5, 1.5])
            c1.write(fila["Cliente"])
            c2.write(fila["Vehículo"])
            c3.write(fila["Placas"].upper() if fila["Placas"] else "S/P")
            c4.write(fila["Tipo de Lavado"])
            c5.write(f"${fila['Precio ($)']}")

            # Botón único por fila
            if c6.button("✅ Terminar", key=f"btn_{indice}", type="primary"):
                st.session_state.servicios.at[indice, "Estatus"] = "Terminado"
                st.toast(f"¡{fila['Vehículo']} marcado como Terminado!")
                st.rerun()
    else:
        st.success("¡No hay autos pendientes en este momento!")

    # Mostrar historial general abajo solo como lectura
    st.subheader("📋 Historial General del Día")
    if not st.session_state.servicios.empty:
        st.dataframe(st.session_state.servicios, use_container_width=True)

# ----------------- PANTALLA: REGISTRO -----------------
elif opcion == "Registro de Servicio":
    st.title("📝 Registrar Nuevo Cliente")

    with st.form("form_servicio", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del Cliente:")
            vehiculo = st.text_input("Modelo del Vehículo (Ej. Honda Civic Blanco):")
            placas = st.text_input("Número de Placas:")
        with col2:
            tipo_lavado = st.selectbox("Tipo de Lavado:",
                                       ["Básico (Exterior)", "Completo (Interior/Exterior)", "Premium (Cera y Motor)"])
            precio = st.number_input("Precio del Servicio ($):", min_value=0.0, step=10.0, value=150.0)

        guardar = st.form_submit_button("Registrar Entrada")

        if guardar:
            if nombre and vehiculo:
                nuevo_servicio = {
                    "Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Cliente": nombre,
                    "Vehículo": vehiculo,
                    "Placas": placas.strip().upper(),
                    "Tipo de Lavado": tipo_lavado,
                    "Precio ($)": precio,
                    "Estatus": "En Proceso"
                }
                st.session_state.servicios = pd.concat([st.session_state.servicios, pd.DataFrame([nuevo_servicio])],
                                                       ignore_index=True)
                st.success(f"¡Vehículo {vehiculo} [{placas.upper()}] registrado con éxito!")
            else:
                st.error("Por favor, llena los campos obligatorios (Nombre y Vehículo).")

# ----------------- PANTALLA: REPORTES -----------------
elif opcion == "Reporte de Ventas":
    st.title("📈 Reportes de Cierre de Caja")

    if not st.session_state.servicios.empty:
        st.subheader("Desglose de Ingresos por Tipo de Lavado")
        resumen = st.session_state.servicios.groupby("Tipo de Lavado")["Precio ($)"].sum().reset_index()
        st.bar_chart(data=resumen, x="Tipo de Lavado", y="Precio ($)", use_container_width=True)

        st.subheader("Historial Completo de Tickets")
        st.dataframe(st.session_state.servicios, use_container_width=True)
    else:
        st.warning("No hay datos de ventas registrados todavía.")
