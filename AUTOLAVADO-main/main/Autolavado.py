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


# --- CONEXIÓN CON LA PESTAÑA DE EGRESOS EN GOOGLE SHEETS ---
def conectar_egresos_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciales.json", scope)
    client = gspread.authorize(creds)
    try:
        # Intenta abrir la pestaña "Egresos"
        sheet = client.open(NOMBRE_HOJA_GOOGLE).worksheet("Egresos")
    except Exception:
        # Si no existe, la crea automáticamente con sus encabezados
        spreadsheet = client.open(NOMBRE_HOJA_GOOGLE)
        sheet = spreadsheet.add_worksheet(title="Egresos", rows=100, cols=3)
        sheet.append_row(["Fecha", "Concepto", "Monto ($)"])
    return sheet


# --- CARGAR DATOS DE INGRESOS ---
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
        st.error(f"Error al conectar con Google Sheets (Ingresos): {e}")
        return pd.DataFrame(
            columns=["Fecha", "Cliente", "Vehículo", "Placas", "Tipo de Lavado", "Precio ($)", "Estatus"])


# --- CARGAR DATOS DE EGRESOS ---
def cargar_egresos():
    try:
        sheet = conectar_egresos_sheets()
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        columnas_requeridas = ["Fecha", "Concepto", "Monto ($)"]
        if df.empty:
            return pd.DataFrame(columns=columnas_requeridas)

        for col in columnas_requeridas:
            if col not in df.columns:
                df[col] = ""

        return df
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets (Egresos): {e}")
        return pd.DataFrame(columns=["Fecha", "Concepto", "Monto ($)"])


# --- GUARDAR EGRESO EN SHEETS ---
def agregar_egreso_a_sheets(nuevo_egreso):
    try:
        sheet = conectar_egresos_sheets()
        fila = [
            nuevo_egreso["Fecha"],
            nuevo_egreso["Concepto"],
            nuevo_egreso["Monto ($)"]
        ]
        sheet.append_row(fila)
    except Exception as e:
        st.error(f"Error al guardar el egreso en Google Sheets: {e}")


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


# --- ELIMINAR REGISTRO EN GOOGLE SHEETS ---
def eliminar_fila_en_sheets(indice_real):
    try:
        sheet = conectar_google_sheets()
        fila_excel = indice_real + 2
        sheet.delete_rows(fila_excel)
    except Exception as e:
        st.error(f"Error al eliminar de Google Sheets: {e}")


# --- EDITAR REGISTRO COMPLETO EN GOOGLE SHEETS ---
def actualizar_registro_en_sheets(indice_real, datos_actualizados):
    try:
        sheet = conectar_google_sheets()
        fila_excel = indice_real + 2
        rango = f"A{fila_excel}:G{fila_excel}"
        fila = [
            datos_actualizados["Fecha"],
            datos_actualizados["Cliente"],
            datos_actualizados["Vehículo"],
            datos_actualizados["Placas"],
            datos_actualizados["Tipo de Lavado"],
            datos_actualizados["Precio ($)"],
            datos_actualizados["Estatus"]
        ]
        sheet.update(rango, [fila])
    except Exception as e:
        st.error(f"Error al actualizar el registro en Google Sheets: {e}")


# --- DISEÑO PERSONALIZADO (CSS) ---
st.html("""
    <style>
        button[data-baseweb="tab"] {
            font-size: 18px !important;
            font-weight: bold !important;
            padding: 10px 15px !important;
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

# --- CARGA INTELIGENTE DEL LOGO ---
if os.path.exists("main/logo.png"):
    ruta_logo = "main/logo.png"
elif os.path.exists("logo.png"):
    ruta_logo = "logo.png"
else:
    ruta_logo = None

if ruta_logo:
    st.image(ruta_logo, width=200)

# Inicializar datos en la sesión desde Google Sheets
if 'servicios' not in st.session_state:
    st.session_state.servicios = cargar_datos()

if 'egresos' not in st.session_state:
    st.session_state.egresos = cargar_egresos()

# Inicializar variables del formulario
if 'input_nombre' not in st.session_state:
    st.session_state.input_nombre = ""
if 'input_vehiculo' not in st.session_state:
    st.session_state.input_vehiculo = ""
if 'input_placas' not in st.session_state:
    st.session_state.input_placas = ""

# CREACIÓN DE 4 PESTAÑAS
tab_registro, tab_inicio, tab_egresos, tab_reportes = st.tabs([
    "📝 Registro",
    "📊 Inicio (Hoy)",
    "💸 Egresos / Gastos",
    "📈 Reportes y Caja"
])

# =========================================================
# 1. CONTENIDO PESTAÑA: REGISTRO
# =========================================================
with tab_registro:
    st.subheader("📝 Registrar Nuevo Servicio (RaceWash)")

    if st.session_state.get('limpiar_pendientes', False):
        st.session_state.input_nombre = ""
        st.session_state.input_vehiculo = ""
        st.session_state.input_placas = ""
        st.session_state.limpiar_pendientes = False

    precios_catalogo = {
        ("Auto chico / Sedán", "Básico"): 140.0,
        ("Auto chico / Sedán", "Race"): 200.0,
        ("Auto chico / Sedán", "Premium"): 350.0,
        ("Camionetas / SUV", "Básico"): 190.0,
        ("Camionetas / SUV", "Race"): 250.0,
        ("Camionetas / SUV", "Premium"): 400.0,
        ("Taxi", "Paquete Básico"): 100.0,
        ("Moto", "Básico Moto"): 80.0,
        ("Moto", "Lavado Especial Moto"): 130.0,
        ("Extra / Servicio Adicional", "Detallado"): 500.0,
        ("Extra / Servicio Adicional", "Lavado de Interiores"): 300.0,
    }

    tipo_vehiculo = st.selectbox("Tipo de Vehículo / Servicio:", [
        "Auto chico / Sedán",
        "Camionetas / SUV",
        "Taxi",
        "Moto",
        "Extra / Servicio Adicional"
    ])

    if tipo_vehiculo == "Taxi":
        paquetes_disponibles = ["Paquete Básico"]
    elif tipo_vehiculo == "Moto":
        paquetes_disponibles = ["Básico Moto", "Lavado Especial Moto"]
    elif tipo_vehiculo == "Extra / Servicio Adicional":
        paquetes_disponibles = ["Detallado", "Lavado de Interiores"]
    else:
        paquetes_disponibles = ["Básico", "Race", "Premium"]

    paquete_seleccionado = st.selectbox("Selecciona el Paquete / Opción:", paquetes_disponibles)
    precio_automatico = precios_catalogo.get((tipo_vehiculo, paquete_seleccionado), 150.0)

    nombre = st.text_input("Nombre del Cliente:", key="input_nombre")
    vehiculo = st.text_input("Modelo del Vehículo / Descripción (Ej. Jetta Negro / Moto Italika):",
                             key="input_vehiculo")
    placas = st.text_input("Número de Placas:", key="input_placas")
    precio = st.number_input("Precio del Servicio ($):", min_value=0.0, step=10.0, value=precio_automatico)

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        registrar = st.button("🚀 Registrar Entrada", type="primary", use_container_width=True)

    with col_btn2:
        limpiar = st.button("🧹 Limpiar Campos", use_container_width=True)

    if limpiar:
        st.session_state.limpiar_pendientes = True
        st.rerun()

    if registrar:
        if nombre and vehiculo:
            horario_mex = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
            detalle_lavado = f"{tipo_vehiculo} - {paquete_seleccionado}"

            nuevo_registro = {
                "Fecha": horario_mex.strftime("%Y-%m-%d %H:%M"),
                "Cliente": nombre,
                "Vehículo": vehiculo,
                "Placas": placas.strip().upper() if placas else "",
                "Tipo de Lavado": detalle_lavado,
                "Precio ($)": precio,
                "Estatus": "En Proceso"
            }

            agregar_fila_a_sheets(nuevo_registro)
            st.session_state.servicios = cargar_datos()
            st.session_state.limpiar_pendientes = True

            st.success(f"¡Servicio para {vehiculo} registrado con éxito en la nube!")
            st.rerun()
        else:
            st.error("Por favor, llena los campos obligatorios (Nombre y Vehículo).")

# =========================================================
# 2. CONTENIDO PESTAÑA: INICIO (FILTRADO HOY)
# =========================================================
with tab_inicio:
    horario_mexico = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
    hoy_str = horario_mexico.strftime("%Y-%m-%d")

    st.subheader(f"📊 Resumen del Día: {horario_mexico.strftime('%d/%m/%Y')}")

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
        st.metric(label="Servicios Pendientes Hoy", value=pendientes_hoy)

    st.subheader("🚗 Servicios en Proceso Hoy")

    if not df_hoy.empty and "Estatus" in df_hoy.columns:
        autos_en_proceso_hoy = df_hoy[df_hoy["Estatus"] == "En Proceso"]
    else:
        autos_en_proceso_hoy = pd.DataFrame()

    if not autos_en_proceso_hoy.empty:
        for indice_real, fila in autos_en_proceso_hoy.iterrows():
            placa_val = str(fila["Placas"]).strip() if pd.notna(fila["Placas"]) else ""
            txt_placas = placa_val.upper() if placa_val != "" else "SIN PLACAS"

            st.html(f"""
                        <div class="car-card">
                            <h3 style='margin:0px;'>🚗 {fila['Vehículo']}</h3>
                            <p style='margin:5px 0px;'><b>Placas:</b> {txt_placas} | <b>Cliente:</b> {fila['Cliente']}</p>
                            <p style='margin:5px 0px;'><b>Servicio:</b> {fila['Tipo de Lavado']} — <span style='color:#25D366; font-weight:bold;'>${fila['Precio ($)']}</span></p>
                        </div>
                    """)

            with st.expander(f"➕ Agregar Servicio Extra a {txt_placas}"):
                extra_personalizado = st.text_input(
                    "Nombre del Extra (Ej. Polish, Faros, etc.):",
                    value="",
                    key=f"input_extra_texto_{indice_real}"
                )

                costo_extra = st.number_input(
                    "Costo del Extra ($):",
                    min_value=0.0,
                    value=100.0,
                    step=50.0,
                    key=f"input_extra_precio_{indice_real}"
                )

                if st.button(f"Confirmar y Sumar Extra", key=f"btn_confirmar_extra_{indice_real}",
                             use_container_width=True):
                    if extra_personalizado.strip() != "":
                        nuevo_tipo_lavado = f"{fila['Tipo de Lavado']} + {extra_personalizado.strip()}"
                        nuevo_precio = float(fila["Precio ($)"]) + costo_extra

                        st.session_state.servicios.at[indice_real, "Tipo de Lavado"] = nuevo_tipo_lavado
                        st.session_state.servicios.at[indice_real, "Precio ($)"] = nuevo_precio

                        sheet = conectar_google_sheets()
                        fila_excel = indice_real + 2
                        sheet.update_cell(fila_excel, 5, nuevo_tipo_lavado)
                        sheet.update_cell(fila_excel, 6, nuevo_precio)

                        st.toast(f"¡Extra '{extra_personalizado}' agregado con éxito!")
                        st.rerun()
                    else:
                        st.error("Por favor, escribe el nombre del servicio extra.")

            with st.expander(f"⚙️ Editar o Eliminar ({txt_placas})"):
                nuevo_cliente = st.text_input("Editar Cliente:", value=str(fila['Cliente']),
                                              key=f"edit_cli_{indice_real}")
                nuevo_vehiculo = st.text_input("Editar Vehículo:", value=str(fila['Vehículo']),
                                               key=f"edit_veh_{indice_real}")
                nuevas_placas = st.text_input("Editar Placas:", value=txt_placas, key=f"edit_pla_{indice_real}")
                nuevo_precio = st.number_input("Editar Precio ($):", value=float(fila['Precio ($)']), step=10.0,
                                               key=f"edit_precio_{indice_real}")

                col_ed1, col_ed2 = st.columns(2)

                with col_ed1:
                    if st.button("💾 Guardar Cambios", key=f"btn_guardar_{indice_real}", use_container_width=True):
                        st.session_state.servicios.at[indice_real, "Cliente"] = nuevo_cliente
                        st.session_state.servicios.at[indice_real, "Vehículo"] = nuevo_vehiculo
                        st.session_state.servicios.at[indice_real, "Placas"] = nuevas_placas.upper()
                        st.session_state.servicios.at[indice_real, "Precio ($)"] = nuevo_precio

                        datos_act = st.session_state.servicios.loc[indice_real].to_dict()
                        actualizar_registro_en_sheets(indice_real, datos_act)

                        st.toast("¡Registro actualizado con éxito!")
                        st.rerun()

                with col_ed2:
                    if st.button("🗑️ Eliminar Registro", key=f"btn_del_{indice_real}", use_container_width=True):
                        st.session_state.servicios = st.session_state.servicios.drop(indice_real).reset_index(drop=True)
                        eliminar_fila_en_sheets(indice_real)

                        st.toast("¡Registro eliminado correctamente!")
                        st.rerun()

            if st.button(f"✅ Marcar Terminado ({txt_placas})", key=f"btn_tab_{indice_real}", type="primary",
                         use_container_width=True):
                st.session_state.servicios.at[indice_real, "Estatus"] = "Terminado"
                guardar_estatus_en_sheets(indice_real, "Terminado")
                st.toast(f"¡{fila['Vehículo']} terminado y sincronizado!")
                st.rerun()

            st.write("---")
    else:
        st.success("¡No hay servicios pendientes para el día de hoy!")

    st.subheader("📋 Historial del Día (Editable)")
    if not df_hoy.empty:
        tabla_mostrar = df_hoy.drop(columns=["Fecha_Solo"])
        df_editado = st.data_editor(
            tabla_mostrar,
            key="editor_historial_hoy",
            use_container_width=True,
            hide_index=True
        )

        if st.button("💾 Guardar Cambios de la Tabla en la Nube", use_container_width=True):
            try:
                sheet = conectar_google_sheets()
                for idx in df_editado.index:
                    st.session_state.servicios.loc[idx, "Cliente"] = df_editado.loc[idx, "Cliente"]
                    st.session_state.servicios.loc[idx, "Vehículo"] = df_editado.loc[idx, "Vehículo"]
                    st.session_state.servicios.loc[idx, "Placas"] = str(df_editado.loc[idx, "Placas"]).upper()
                    st.session_state.servicios.loc[idx, "Tipo de Lavado"] = df_editado.loc[idx, "Tipo de Lavado"]
                    st.session_state.servicios.loc[idx, "Precio ($)"] = float(df_editado.loc[idx, "Precio ($)"])
                    st.session_state.servicios.loc[idx, "Estatus"] = df_editado.loc[idx, "Estatus"]

                    fila_excel = idx + 2
                    rango = f"A{fila_excel}:G{fila_excel}"
                    fila_valores = [
                        str(st.session_state.servicios.loc[idx, "Fecha"]),
                        str(st.session_state.servicios.loc[idx, "Cliente"]),
                        str(st.session_state.servicios.loc[idx, "Vehículo"]),
                        str(st.session_state.servicios.loc[idx, "Placas"]),
                        str(st.session_state.servicios.loc[idx, "Tipo de Lavado"]),
                        float(st.session_state.servicios.loc[idx, "Precio ($)"]),
                        str(st.session_state.servicios.loc[idx, "Estatus"])
                    ]
                    sheet.update(rango, [fila_valores])

                st.toast("¡Historial actualizado y sincronizado en la nube con éxito!")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar los cambios de la tabla: {e}")
    else:
        st.info("Aún no hay registros para el día de hoy.")

# =========================================================
# 3. CONTENIDO PESTAÑA: EGRESOS / GASTOS
# =========================================================
with tab_egresos:
    st.subheader("💸 Registro de Egresos y Gastos del Negocio")

    with st.form("form_egreso"):
        # 📅 Selector de fecha (Por defecto trae el día actual de México)
        horario_mex_actual = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
        fecha_egreso = st.date_input("Fecha del Gasto:", value=horario_mex_actual.date())

        concepto_egreso = st.text_input("Concepto del Gasto (Ej. Compra de Shampoo, Luz, Sueldo, Agua):")
        monto_egreso = st.number_input("Monto del Gasto ($):", min_value=0.0, step=10.0, value=50.0)

        btn_guardar_egreso = st.form_submit_button("📉 Registrar Gasto", use_container_width=True)

        if btn_guardar_egreso:
            if concepto_egreso.strip() != "":
                # Combinamos la fecha seleccionada con la hora actual exacta
                hora_actual = horario_mex_actual.strftime("%H:%M")
                fecha_formateada = f"{fecha_egreso.strftime('%Y-%m-%d')} {hora_actual}"

                nuevo_egreso = {
                    "Fecha": fecha_formateada,
                    "Concepto": concepto_egreso.strip(),
                    "Monto ($)": monto_egreso
                }
                agregar_egreso_a_sheets(nuevo_egreso)
                st.session_state.egresos = cargar_egresos()
                st.success(
                    f"¡Gasto de ${monto_egreso:,.2f} registrado para el día {fecha_egreso.strftime('%d/%m/%Y')} con éxito!")
                st.rerun()
            else:
                st.error("Por favor, escribe el concepto del gasto.")

    st.subheader("📋 Historial de Egresos Registrados")
    if not st.session_state.egresos.empty:
        st.dataframe(st.session_state.egresos, use_container_width=True, hide_index=True)
    else:
        st.info("No hay egresos registrados todavía.")

# =========================================================
# 4. CONTENIDO PESTAÑA: REPORTES Y CAJA
# =========================================================
# =========================================================
# 4. CONTENIDO PESTAÑA: REPORTES Y CAJA
# =========================================================
with tab_reportes:
    st.subheader("📈 Reportes, Ingresos, Egresos y Corte por Fecha")

    if not st.session_state.servicios.empty or not st.session_state.egresos.empty:

        # Opciones de visualización
        modo_filtro = st.radio(
            "Selecciona el modo de vista:",
            ["📅 Ver un día específico", "📊 Historial acumulado (Todo)"],
            horizontal=True
        )

        df_reporte_ingresos = st.session_state.servicios.copy()
        df_reporte_egresos = st.session_state.egresos.copy()

        # Preparar columna de solo fecha para los filtros
        if not df_reporte_ingresos.empty:
            df_reporte_ingresos["Fecha_Solo"] = df_reporte_ingresos["Fecha"].astype(str).str.slice(0, 10)
        if not df_reporte_egresos.empty:
            df_reporte_egresos["Fecha_Solo"] = df_reporte_egresos["Fecha"].astype(str).str.slice(0, 10)

        # Filtrar según la opción elegida
        if modo_filtro == "📅 Ver un día específico":
            horario_mex_actual = datetime.datetime.utcnow() - datetime.timedelta(hours=6)
            fecha_seleccionada = st.date_input("Selecciona la fecha a consultar:", value=horario_mex_actual.date())
            fecha_sel_str = fecha_seleccionada.strftime("%Y-%m-%d")

            if not df_reporte_ingresos.empty:
                df_reporte_ingresos = df_reporte_ingresos[df_reporte_ingresos["Fecha_Solo"] == fecha_sel_str]
            if not df_reporte_egresos.empty:
                df_reporte_egresos = df_reporte_egresos[df_reporte_egresos["Fecha_Solo"] == fecha_sel_str]

        # Limpiar columnas temporales auxiliares antes de mostrar
        if not df_reporte_ingresos.empty and "Fecha_Solo" in df_reporte_ingresos.columns:
            df_reporte_ingresos = df_reporte_ingresos.drop(columns=["Fecha_Solo"])
        if not df_reporte_egresos.empty and "Fecha_Solo" in df_reporte_egresos.columns:
            df_reporte_egresos = df_reporte_egresos.drop(columns=["Fecha_Solo"])

        # Cálculos de Totales asegurando formato numérico
        total_ingresos = pd.to_numeric(df_reporte_ingresos["Precio ($)"],
                                       errors='coerce').sum() if not df_reporte_ingresos.empty else 0.0
        total_egresos = pd.to_numeric(df_reporte_egresos["Monto ($)"],
                                      errors='coerce').sum() if not df_reporte_egresos.empty else 0.0
        utilidad_neta = total_ingresos - total_egresos

        # Métricas de Balance
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            st.metric(label="💰 Ingresos del Periodo", value=f"${total_ingresos:,.2f}")
        with col_r2:
            st.metric(label="📉 Egresos del Periodo", value=f"${total_egresos:,.2f}")
        with col_r3:
            st.metric(label="⭐ Utilidad Neta (Ganancia)", value=f"${utilidad_neta:,.2f}",
                      delta=f"${utilidad_neta:,.2f}")

        st.write("---")

        st.subheader("Desglose de Ingresos por Tipo de Servicio")
        if not df_reporte_ingresos.empty:
            df_temp = df_reporte_ingresos.copy()
            df_temp["Precio ($)"] = pd.to_numeric(df_temp["Precio ($)"], errors='coerce')
            resumen = df_temp.groupby("Tipo de Lavado")["Precio ($)"].sum().reset_index()
            st.bar_chart(data=resumen, x="Tipo de Lavado", y="Precio ($)", use_container_width=True)
        else:
            st.info("No hay ingresos para mostrar en gráfica en este periodo.")

        st.subheader("📋 Detalle de Ingresos (Tickets)")
        if not df_reporte_ingresos.empty:
            st.dataframe(df_reporte_ingresos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay ingresos registrados en este periodo.")

        st.subheader("📉 Detalle de Egresos (Gastos)")
        if not df_reporte_egresos.empty:
            df_reporte_egresos["Monto ($)"] = pd.to_numeric(df_reporte_egresos["Monto ($)"], errors='coerce')
            st.dataframe(df_reporte_egresos, use_container_width=True, hide_index=True)
        else:
            st.info("No hay egresos registrados en este periodo.")

        # Botón de Descarga CSV del reporte actual
        csv_data = df_reporte_ingresos.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Reporte de Ingresos en CSV",
            data=csv_data,
            file_name=f"reporte_ingresos_racewash_{datetime.date.today()}.csv",
            mime="text/csv",
            use_container_width=True,
        )
    else:
        st.warning("No hay datos de ventas ni de gastos registrados todavía.")