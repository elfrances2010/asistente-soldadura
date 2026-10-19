import streamlit as st
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Asistente de Soldadura e IA", page_icon="🛠️", layout="wide")

st.title("🛠️ Asistente de Soldadura, Cerrajería e IA")

# --- DICCIONARIO BASE DE MATERIALES Y PRECIOS ESTIMADOS (COP) ---
CATALOGO_MATERIALES = {
    "Tubos Cuadrados y Rectangulares (6m)": {
        "Tubo Cuadrado 1/2" x 1/2" Cal 18": 18000,
        "Tubo Cuadrado 3/4" x 3/4" Cal 18": 26000,
        "Tubo Cuadrado 1" x 1" Cal 18": 32000,
        "Tubo Cuadrado 1" x 1" Cal 16": 42000,
        "Tubo Rectangular 2" x 1" Cal 18": 48000,
        "Tubo Rectangular 2" x 1" Cal 16": 62000,
        "Tubo Cuadrado 2" x 2" Cal 14": 95000,
    },
    "Perfiles Estructurales y Perfilería C (6m)": {
        "Perfil C / Envolvente 3" x 1.1/2" Cal 16": 65000,
        "Perfil C / Envolvente 4" x 2" Cal 16": 88000,
        "Perfil C / Envolvente 4" x 2" Cal 14": 115000,
        "Tubo Estructural Chapa 3" x 1.1/2" Cal 14": 98000,
    },
    "Ángulos y Platinas de Hierro (6m)": {
        "Ángulo 3/4" x 1/8"": 28000,
        "Ángulo 1" x 1/8"": 36000,
        "Ángulo 1.1/2" x 1/8"": 54000,
        "Ángulo 2" x 3/16"": 98000,
        "Platina 1" x 1/8"": 32000,
        "Platina 1.1/2" x 3/16"": 68000,
        "Platina 2" x 1/4"": 110000,
    },
    "Varillas de Hierro y Cabilla (6m)": {
        "Varilla Lisa 3/8"": 22000,
        "Varilla Lisa 1/2"": 38000,
        "Varilla Cuadrada 1/2" (Para Rejas)": 42000,
        "Varilla Corrugada 1/2" (Estructural)": 35000,
    },
    "Láminas y Placas": {
        "Lámina Cold Rolled Cal 18 (1.2m x 2.4m)": 125000,
        "Lámina Cold Rolled Cal 16 (1.2m x 2.4m)": 165000,
        "Lámina Alfajor 2.5mm (1.2m x 2.4m - Pisos)": 280000,
        "Lámina HR 1/8" (1.2m x 2.4m)": 290000,
    }
}

# --- FUNCIÓN GENERAR PDF ---
def generar_pdf_cotizacion(cliente, metros, tipo_perfil, barras, desperdicio, kg_soldadura, costo_materiales, mano_obra, total):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    p.setTitle("Cotización de Cerrajería")

    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, 750, "COTIZACIÓN DE TALLER - CERRAJERÍA Y SOLDADURA")
    
    p.setFont("Helvetica", 10)
    p.drawString(50, 735, f"Cliente / Proyecto: {cliente}")
    p.line(50, 725, 550, 725)

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, 700, "Detalle del Presupuesto:")

    p.setFont("Helvetica", 10)
    y = 675
    p.drawString(50, y, f"• Material / Perfil: {tipo_perfil}")
    y -= 20
    p.drawString(50, y, f"• Metros o unidades requeridas: {metros} m/und")
    y -= 20
    p.drawString(50, y, f"• Unidades/Barras a comprar: {barras} und")
    y -= 20
    p.drawString(50, y, f"• Desperdicio estimado: {desperdicio:.2f} m")
    y -= 20
    p.drawString(50, y, f"• Soldadura estimada: {kg_soldadura:.2f} kg")
    y -= 30

    p.line(50, y, 550, y)
    y -= 20
    p.drawString(50, y, f"Costo estimado de materiales: ${costo_materiales:,.0f} COP")
    y -= 20
    p.drawString(50, y, f"Mano de obra estimada: ${mano_obra:,.0f} COP")
    y -= 25
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, f"TOTAL COTIZACIÓN: ${total:,.0f} COP")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

tab1, tab2, tab3 = st.tabs(["🧮 Cotizador y PDF", "📖 Guía de Materiales y Fichas", "🤖 Chat Asistente IA"])

# --- PESTAÑA 1: COTIZADOR CON CATÁLOGO ---
with tab1:
    st.subheader("Calculadora de Presupuesto con Catálogo Ampliado")
    
    col_a, col_b = st.columns(2)
    with col_a:
        nombre_cliente = st.text_input("Nombre del Cliente / Proyecto:", value="Obra Casa Campestre")
        categoria = st.selectbox("Categoría de Material:", list(CATALOGO_MATERIALES.keys()))
        
        # Selección dinámica de perfil según categoría
        perfil_seleccionado = st.selectbox("Selecciona el Perfil / Material:", list(CATALOGO_MATERIALES[categoria].keys()))
        precio_sugerido = CATALOGO_MATERIALES[categoria][perfil_seleccionado]
        
    with col_b:
        metros = st.number_input("Metros o unidades totales requeridas:", min_value=1.0, value=25.0, step=0.5)
        precio_barra = st.number_input("Precio unitario / barra (COP):", value=precio_sugerido, step=1000)
        costo_mano_obra = st.number_input("Costo Mano de Obra (COP):", value=180000, step=10000)

    # Cálculo si es por metro (barras de 6m) o por lámina unitaria
    if "Lámina" in categoria:
        barras = int(metros)
        desperdicio = 0.0
        costo_perfiles = barras * precio_barra
        kg_soldadura = metros * 0.2
    else:
        barras = int(metros // 6) + (1 if metros % 6 > 0 else 0)
        desperdicio = (barras * 6) - metros
        costo_perfiles = barras * precio_barra
        kg_soldadura = metros * 0.05

    costo_soldadura = kg_soldadura * 18000
    total_materiales = costo_perfiles + costo_soldadura
    total_general = total_materiales + costo_mano_obra

    st.markdown("---")
    st.markdown(f"### **Total Cotización: ${total_general:,.0f} COP**")

    try:
        pdf_bytes = generar_pdf_cotizacion(
            nombre_cliente, metros, perfil_seleccionado, barras, desperdicio, 
            kg_soldadura, total_materiales, costo_mano_obra, total_general
        )
        st.download_button(
            label="📄 Descargar Cotización en PDF",
            data=pdf_bytes,
            file_name=f"Cotizacion_{nombre_cliente.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    except Exception:
        st.warning("Instala reportlab: `pip install reportlab`")

# --- PESTAÑA 2: GUÍA TÉCNICA Y TIPOS DE MATERIALES ---
with tab2:
    st.subheader("Clasificación General de Materiales en Metalmecánica")
    
    st.markdown('''
    ### 1. Aceros al Carbono (Hierro Comercial / Estructural)
    * **Perfiles Muebleros y Malla Suave (Cal. 18 - Cal. 20):** Ideal para ventanas, puertas residenciales, cerramientos ligeros y muebles metálicos.
    * **Perfiles Estructurales Medios (Cal. 14 - Cal. 16):** Usados en correas para tejados, portones vehiculares, estructuras para cubiertas y perfiles tipo C.
    * **Aceros Pesados / Vigas (IPN, IPE, HEA, Ángulos > 1/4"):** Diseñados para mezanines, bodegas, columnas de soporte y cerchas industriales.

    ### 2. Aceros Inoxidables (AISI 304 / AISI 316)
    * **Uso:** Equipos para procesamiento de alimentos, tanques, barandas ornamentales y ambientes marinos o de alta humedad.
    * **Proceso de Soldadura recomendado:** TIG (GTAW) con argón puro o electrodo E308L / E316L (SMAW).

    ### 3. Aluminio y Aleaciones (Serie 6000 - 6063/6061)
    * **Uso:** Ventanería arquitectónica, carrocerías livianas, estructuras marinas y portones automatizados de bajo peso.
    * **Proceso de Soldadura recomendado:** TIG con corriente alterna (AC) o MIG (GMAW) con carrete Spool Gun y gas Argón.
    ''')

# --- PESTAÑA 3: CHAT IA ---
with tab3:
    st.subheader("🤖 Consultas Técnicas en Vivo con IA")
    st.write("Pregunta sobre especificaciones de materiales, calibres, normas AWS o tipos de bisel.")
    api_key = st.sidebar.text_input("Llave de API (OpenAI / DeepSeek / Groq):", type="password")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "¡Hola! Pregúntame sobre cualquier tipo de material o proceso de soldadura."}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Ej: ¿Qué diferencia hay entre acero Cold Rolled y Hot Rolled?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Eres un experto en metalmecánica y ciencia de materiales."},
                        *st.session_state.messages
                    ]
                )
                respuesta_ia = response.choices[0].message.content
            except Exception as e:
                respuesta_ia = f"Error: {e}"
        else:
            respuesta_ia = f"**(Modo offline)** Para '{prompt}':
* **Cold Rolled (Laminado en frío):** Excelente acabado superficial, dimensiones precisas, ideal para cerrajería fina y muebles.
* **Hot Rolled (Laminado en caliente):** Capa de cascarilla de laminación (cáscara negra), mayor grosor, ideal para estructuras pesadas."

        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
        st.chat_message("assistant").write(respuesta_ia)