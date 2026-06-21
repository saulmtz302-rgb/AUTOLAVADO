import streamlit as st
import pandas as pd
import datetime

# Configuración inicial de la página
st.set_page_config(page_title="Car Wash Control", page_icon="🧼", layout="wide")

# --- DISEÑO PERSONALIZADO (CSS) PARA CELULARES Y MENÚ ---
st.html("""
    <style>
        /* Agranda el título de la barra lateral */
        [data-testid="stSidebarNav"]::before {
            font-size: 24px !important;
        }
        /* Agranda el texto de las opciones del menú lateral */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
            font-size: 20px !important;
            padding-top: 10px !important;
            padding-bottom: 10px !important;
        }
        /* Separación del menú */
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
            gap: 12px !important;
        }
        /* Caja o tarjeta responsiva para cada auto en proceso */
        .car-card {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 5px solid #ff4b4b;
        }
        /* Modo oscuro compatible para las tarjetas si cambias el tema */
        @media (prefers-color-scheme: dark) {
            .car-card {
                background-color: #262730;
                border-left: 5px solid #ff4b4b;
            }
        }
    </style>
""")

# Estructura de navegación en la barra lateral
st.sidebar.title("🧼 Car Wash Manager")
opcion = st.sidebar.radio("Selecciona una pantalla:", ["Inicio", "Registro de Servicio", "Reporte de Ventas"])

# Inicialización de la base de datos en sesión
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
        # En lugar de una tabla rota en celular, creamos contenedores móviles individuales
        for indice, fila in autos_en_proceso.iterrows():
            txt_placas = fila["Placas"].upper() if fila["Placas"] else "SIN PLACAS"

            # Renderiza los datos en formato tarjeta responsiva
            st.html(f"""
                <div class="car-card">
                    <h3 style='margin:0px;'>🚗 {fila['Vehículo']}</h3>
                    <p style='margin:5px 0px;'><b>Placas:</b> {txt_placas} | <b>Cliente:</b> {fila['Cliente']}</p>
                    <p style='margin:5px 0px;'><b>Servicio:</b> {fila['Tipo de Lavado']} — <span style='color:#25D366; font-weight:bold;'>${fila['Precio ($)']}</span></p>
                </div>
            """)

            # Botón grande debajo de la tarjeta para presionar fácilmente con el dedo
            if st.button(f"✅ Marcar Terminado ({txt_placas})", key=f"btn_mob_{indice}", type="primary",
                         use_container_width=True):
                st.session_state.servicios.at[indice, "Estatus"] = "Terminado"
                st.toast(f"¡{fila['Vehículo']} terminado!")
                st.rerun()
            st.write("")  # Pequeño espacio de separación
    else:
        st.success("¡No hay autos pendientes en este momento!")

    # Mostrar historial general abajo como tabla de respaldo
    st.subheader("📋 Historial General del Día")
    if not st.session_state.servicios.empty:
        st.dataframe(st.session_state.servicios, use_container_width=True)

# ----------------- PANTALLA: REGISTRO -----------------
elif opcion == "Registro de Servicio":
    st.title("📝 Registrar Nuevo Cliente")

    with st.form("form_servicio", clear_on_submit=True):
        # Campos apilados verticalmente o en dos columnas
        nombre = st.text_input("Nombre del Cliente:")
        vehiculo = st.text_input("Modelo del Vehículo (Ej. Honda Civic Blanco):")
        placas = st.text_input("Número de Placas:")
        tipo_lavado = st.selectbox("Tipo de Lavado:",
                                   ["Básico (Exterior)", "Completo (Interior/Exterior)", "Premium (Cera y Motor)"])
        precio = st.number_input("Precio del Servicio ($):", min_value=0.0, step=10.0, value=150.0)

        guardar = st.form_submit_button("Registrar Entrada", use_container_width=True)

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
                st.success(f"¡Vehículo {vehiculo} registrado con éxito!")
                st.rerun()
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
