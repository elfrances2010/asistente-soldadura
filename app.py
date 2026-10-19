import streamlit as st
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="Asistente de Soldadura e IA", page_icon="🛠️", layout="wide")

st.title("🛠️ Asistente de Soldadura, Cerrajería e IA")

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
    p.drawString(50, y, f"• Tipo de Perfil: {tipo_perfil}")
    y -= 20
    p.drawString(50, y, f"• Metros requeridos: {metros} m")
    y -= 20
    p.drawString(50, y, f"• Barras de 6m a comprar: {barras} und")
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

tab1, tab2, tab3 = st.tabs(["🧮 Cotizador y PDF", "📖 Guía Técnica", "🤖 Chat Asistente IA"])

# --- PESTAÑA 1: COTIZADOR ---
with tab1:
    st.subheader("Calculadora de Presupuesto y Generación de PDF")
    
    col_a, col_b = st.columns(2)
    with col_a:
        nombre_cliente = st.text_input("Nombre del Cliente / Proyecto:", value="Obra Casa Campestre")
        metros = st.number_input("Metros totales requeridos:", min_value=1.0, value=25.0, step=0.5)
        precio_barra = st.number_input("Precio por barra de 6m (COP):", value=35000, step=1000)
    
    with col_b:
        tipo_perfil = st.selectbox("Perfil a utilizar:", ["Tubo Cuadrado 2x1 Cal 18", "Tubo Cuadrado 1x1 Cal 18", "Ángulo 1\"x1/8\"", "Platina 1\"x1/8\""])
        costo_mano_obra = st.number_input("Costo Mano de Obra (COP):", value=150000, step=10000)

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
            nombre_cliente, metros, tipo_perfil, barras, desperdicio, 
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

# --- PESTAÑA 2: GUÍA TÉCNICA ---
with tab2:
    st.subheader("Fichas de Soldadura y Amperajes")
    calibre = st.selectbox("Selecciona el grosor del material:", ["Calibre 18 (1.2 mm)", "Calibre 16 (1.5 mm)", "Estructura Pesada (> 3.0 mm)"])
    if "18" in calibre or "16" in calibre:
        st.info("👉 **Electrodo Recomendado:** E6013 de 3/32\"")
        st.write("**Amperaje recomendado:** 60A - 75A")
    else:
        st.info("👉 **Electrodo Recomendado:** E7018 de 1/8\"")
        st.write("**Amperaje recomendado:** 100A - 130A")

# --- PESTAÑA 3: CHAT INTELIGENTE (OPENAI / DEEPSEEK INTEGRADO) ---
with tab3:
    st.subheader("🤖 Consultas Técnicas en Vivo con IA")
    st.write("Escribe preguntas sobre cualquier proceso de soldadura (SMAW, MIG/MAG, TIG) o cálculo de estructuras.")
    
    api_key = st.sidebar.text_input("Llave de API (OpenAI / DeepSeek / Groq):", type="password", help="Ingresa tu API Key para habilitar el modelo de lenguaje real.")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "¡Hola! Soy tu experto en soldadura y metalmecánica. ¿En qué te puedo asesorar hoy?"}
        ]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Ej: ¿Cómo evito la socavación en soldadura vertical ascendente?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        if api_key:
            try:
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Eres un ingeniero experto en soldadura, cerrajería y estructuras metálicas. Responde de forma clara, técnica y práctica para taller."},
                        *st.session_state.messages
                    ]
                )
                respuesta_ia = response.choices[0].message.content
            except Exception as e:
                respuesta_ia = f"Error al conectar con la API: {e}"
        else:
            respuesta_ia = f"**(Modo offline sin API Key)** Para abordar '{prompt}':\n1. Revisa que el amperaje esté dentro del rango del electrodo.\n2. Mantén un ángulo de ataque adecuado (45° a 70°).\n3. Limpia la escoria y óxido de la junta antes de realizar el pase."

        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
        st.chat_message("assistant").write(respuesta_ia)