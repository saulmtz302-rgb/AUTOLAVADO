import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Configuración inicial de la página
st.set_page_config(page_title="RaceWash Control", page_icon="🧼", layout="wide")

# --- CONEXIÓN CON GOOGLE SHEETS ---
NOMBRE_HOJA_GOOGLE = "Control_Autolavado"


def conectar_google_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(NOMBRE_HOJA_GOOGLE).sheet1
    return sheet


# --- CARGAR DATOS DESDE GOOGLE SHEETS ---
def cargar_datos():
    try:
        sheet = conectar_google_sheets()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        columnas_requeridas = ["Fecha", "Cliente", "Vehículo", "Placas", "Tipo de Lavado", "Precio ($)", "Estatus"]
        if df.empty:
            return pd.DataFrame(columns=columnas_requeridas)

        for col in columnas_requeridas:
            if col not in df.columns:
                df[col] = ""

        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame(
            columns=["Fecha", "Cliente", "Vehículo", "Placas", "Tipo de Lavado", "Precio ($)", "Estatus"])


# --- ACTUALIZAR ESTATUS EN GOOGLE SHEETS ---
def guardar_estatus_en_sheets(indice_real, nuevo_estatus):
    try:
        sheet = conectar_google_sheets()
        fila_excel = indice_real + 2
        sheet.update_cell(fila_excel, 7, nuevo_estatus)
    except Exception as e:
        st.error(f"Error al actualizar en Google Sheets: {e}")


def agregar_fila_a_sheets(nuevo_registro):
    try:
        sheet = conectar_google_sheets()
        fila = [
            nuevo_registro["Fecha"],
            nuevo_registro["Cliente"],
            nuevo_registro["Vehículo"],
            nuevo_registro["Placas"],
            nuevo_registro["Tipo de Lavado"],
            nuevo_registro["Precio ($)"],
            nuevo_registro["Estatus"]
        ]
        sheet.append_row(fila)
    except Exception as e:
        st.error(f"Error al guardar el registro en Google Sheets: {e}")


# --- DISEÑO PERSONALIZADO (CSS) ---
st.html("""
    <style>
        button[data-baseweb="tab"] {
            font-size: 20px !important;
            font-weight: bold !important;
            padding: 12px 20px !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #ff4b4b !important;
            border-bottom-color: #ff4b4b !important;
        }
        .car-card {
            background-color: #f0f2f6;
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 10px;
            border-left: 5px solid #ff4b4b;
        }
        @media (prefers-color-scheme: dark) {
            .car-card {
                background-color: #262730;
                border-left: 5px solid #ff4b4b;
            }
        }
    </style>
""")

# --- CABECERA CON LOGOTIPO Y TÍTULO ---
import os

# --- CARGA INTELIGENTE DEL LOGO ---
# Busca el logo tanto si estás en local como si estás en Render
if os.path.exists("main/logo.png"):
    ruta_logo = "main/logo.png"
elif os.path.exists("logo.png"):
    ruta_logo = "logo.png"
else:
    ruta_logo = None

# Muestra el logo si lo encuentra
if ruta_logo:
    st.image(ruta_logo, width=200) # Puedes ajustar el ancho a tu gusto

# Inicializar datos en la sesión desde Google Sheets
if 'servicios' not in st.session_state:
    st.session_state.servicios = cargar_datos()

# Inicializar las variables de los inputs del formulario para poder limpiarlas
if 'input_nombre' not in st.session_state:
    st.session_state.input_nombre = ""
if 'input_vehiculo' not in st.session_state:
    st.session_state.input_vehiculo = ""
if 'input_placas' not in st.session_state:
    st.session_state.input_placas = ""

# CREACIÓN DE PESTAÑAS (Inicia en Registro de Servicio)
tab_registro, tab_inicio, tab_reportes = st.tabs(
    ["📝 Registro de Servicio", "📊 Inicio (Día de Hoy)", "📈 Reporte de Ventas"])

# ----------------- CONTENIDO PESTAÑA: REGISTRO -----------------
with tab_registro:
    st.subheader("📝 Registrar Nuevo Servicio (RaceWash)")

    precios_catalogo = {
        ("Auto chico / Sedán", "Básico"): 140.0,
        ("Auto chico / Sedán", "Race"): 200.0,
        ("Auto chico / Sedán", "Premium"): 350.0,
        ("Camionetas / SUV", "Básico"): 190.0,
        ("Camionetas / SUV", "Race"): 250.0,
        ("Camionetas / SUV", "Premium"): 400.0,
        ("Taxi", "Paquete Básico"): 100.0,
    }

    # Controles de selección de tipo y paquete fuera del formulario para el cálculo dinámico del precio
    tipo_vehiculo = st.selectbox("Tipo de Vehículo:", ["Auto chico / Sedán", "Camionetas / SUV", "Taxi"])

    if tipo_vehiculo == "Taxi":
        paquetes_disponibles = ["Paquete Básico"]
    else:
        paquetes_disponibles = ["Básico", "Race", "Premium"]

    paquete_seleccionado = st.selectbox("Selecciona el Paquete:", paquetes_disponibles)

    precio_automatico = precios_catalogo.get((tipo_vehiculo, paquete_seleccionado), 150.0)

    # Campos de texto enlazados a session_state
    nombre = st.text_input("Nombre del Cliente:", key="input_nombre")
    vehiculo = st.text_input("Modelo del Vehículo (Ej. Jetta Negro):", key="input_vehiculo")
    placas = st.text_input("Número de Placas:", key="input_placas")

    precio = st.number_input("Precio del Servicio ($):", min_value=0.0, step=10.0, value=precio_automatico)

    # Botones de acción organizados en dos columnas
    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        registrar = st.button("🚀 Registrar Entrada", type="primary", use_container_width=True)

    with col_btn2:
        limpiar = st.button("🧹 Limpiar Campos", use_container_width=True)

    # Lógica del botón Limpiar
    if limpiar:
        st.session_state.input_nombre = ""
        st.session_state.input_vehiculo = ""
        st.session_state.input_placas = ""
        st.rerun()

    # Lógica del botón Registrar
    if registrar:
        if nombre and vehiculo:
            detalle_lavado = f"{tipo_vehiculo} - {paquete_seleccionado}"

            nuevo_servicio = {
                "Fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Cliente": nombre,
                "Vehículo": vehiculo,
                "Placas": placas.strip().upper() if placas else "",
                "Tipo de Lavado": detalle_lavado,
                "Precio ($)": precio,
                "Estatus": "En Proceso"
            }

            agregar_fila_a_sheets(nuevo_servicio)
            st.session_state.servicios = cargar_datos()

            # Limpiar campos tras un registro exitoso
            st.session_state.input_nombre = ""
            st.session_state.input_vehiculo = ""
            st.session_state.input_placas = ""

            st.success(f"¡Vehículo {vehiculo} registrado con éxito en la nube!")
            st.rerun()
        else:
            st.error("Por favor, llena los campos obligatorios (Nombre y Vehículo).")

# ----------------- CONTENIDO PESTAÑA: INICIO (FILTRADO HOY) -----------------
with tab_inicio:
    st.subheader(f"📊 Resumen del Día: {datetime.date.today().strftime('%d/%m/%Y')}")

    hoy_str = datetime.datetime.now().strftime("%Y-%m-%d")

    if not st.session_state.servicios.empty:
        df_servicios = st.session_state.servicios.copy()
        df_servicios["Fecha_Solo"] = df_servicios["Fecha"].astype(str).str.slice(0, 10)
        df_hoy = df_servicios[df_servicios["Fecha_Solo"] == hoy_str]
    else:
        df_hoy = pd.DataFrame()

    col1, col2, col3 = st.columns(3)
    with col1:
        total_servicios_hoy = len(df_hoy)
        st.metric(label="Servicios Hoy", value=total_servicios_hoy)
    with col2:
        ganancias_hoy = df_hoy["Precio ($)"].astype(float).sum() if not df_hoy.empty else 0
        st.metric(label="Ingresos Hoy", value=f"${ganancias_hoy:,.2f}")
    with col3:
        if not df_hoy.empty and "Estatus" in df_hoy.columns:
            pendientes_hoy = len(df_hoy[df_hoy["Estatus"] == "En Proceso"])
        else:
            pendientes_hoy = 0
        st.metric(label="Autos Pendientes Hoy", value=pendientes_hoy)

    st.subheader("🚗 Autos en Lavado Hoy (En Proceso)")

    if not df_hoy.empty and "Estatus" in df_hoy.columns:
        autos_en_proceso_hoy = df_hoy[df_hoy["Estatus"] == "En Proceso"]
    else:
        autos_en_proceso_hoy = pd.DataFrame()

    if not autos_en_proceso_hoy.empty:
        for indice_real, fila in autos_en_proceso_hoy.iterrows():
            txt_placas = fila["Placas"].upper() if pd.notna(fila["Placas"]) and fila["Placas"] else "SIN PLACAS"

            st.html(f"""
                <div class="car-card">
                    <h3 style='margin:0px;'>🚗 {fila['Vehículo']}</h3>
                    <p style='margin:5px 0px;'><b>Placas:</b> {txt_placas} | <b>Cliente:</b> {fila['Cliente']}</p>
                    <p style='margin:5px 0px;'><b>Paquete:</b> {fila['Tipo de Lavado']} — <span style='color:#25D366; font-weight:bold;'>${fila['Precio ($)']}</span></p>
                </div>
            """)

            if st.button(f"✅ Marcar Terminado ({txt_placas})", key=f"btn_tab_{indice_real}", type="primary",
                         use_container_width=True):
                st.session_state.servicios.at[indice_real, "Estatus"] = "Terminado"
                guardar_estatus_en_sheets(indice_real, "Terminado")
                st.toast(f"¡{fila['Vehículo']} terminado y sincronizado!")
                st.rerun()
            st.write("")
    else:
        st.success("¡No hay autos pendientes para el día de hoy!")

    st.subheader("📋 Historial del Día")
    if not df_hoy.empty:
        tabla_mostrar = df_hoy.drop(columns=["Fecha_Solo"])
        st.dataframe(tabla_mostrar, use_container_width=True)
    else:
        st.info("Aún no hay registros para el día de hoy.")

# ----------------- CONTENIDO PESTAÑA: REPORTES -----------------
with tab_reportes:
    st.subheader("📈 Reportes Generales y Cierre de Caja")

    if not st.session_state.servicios.empty:
        ver_todo = st.checkbox("Mostrar todo el historial histórico acumulado", value=True)

        if ver_todo:
            df_reporte = st.session_state.servicios.copy()
        else:
            df_reporte = df_hoy.copy()
            if "Fecha_Solo" in df_reporte.columns:
                df_reporte = df_reporte.drop(columns=["Fecha_Solo"])

        st.subheader("Desglose de Ingresos por Paquete")
        df_temp = df_reporte.copy()
        df_temp["Precio ($)"] = pd.to_numeric(df_temp["Precio ($)"])
        resumen = df_temp.groupby("Tipo de Lavado")["Precio ($)"].sum().reset_index()
        st.bar_chart(data=resumen, x="Tipo de Lavado", y="Precio ($)", use_container_width=True)

        st.subheader("Historial de Tickets")
        st.dataframe(df_reporte, use_container_width=True)

        csv_data = df_reporte.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte en CSV",
            data=csv_data,
            file_name=f"reporte_raceva_wash_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.warning("No hay datos de ventas registrados todavía.")