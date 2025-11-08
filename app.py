# app.py — Landing Page Interactiva de BCS Technologies
import streamlit as st
import base64
from pathlib import Path

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="BCS Technologies — Business Core Software",
    page_icon="🧩",
    layout="wide"
)

# --- ENCABEZADO PRINCIPAL ---
col1, col2 = st.columns([1,4])
with col1:
    st.image("assets/BCS_logo.png", width=120)
with col2:
    
    st.markdown("""
    <h1 style='color: #00BFFF;'>🧩 BCS Technologies</h1>
    <h3>El sistema que crea sistemas.</h3>
    <p style='font-size: 18px;'>Una plataforma SaaS modular que co-crea soluciones empresariales a partir de los dolores y necesidades reales de cada cliente.</p>
    """, unsafe_allow_html=True)

st.divider()

# --- SECCIÓN: QUÉ ES BCS ---
with st.expander("🔹 ¿Qué es BCS?"):
    st.write("""
    **BCS (Business Core Software)** es una plataforma madre que permite crear, administrar y automatizar sub–sistemas empresariales
    completamente personalizados según la industria y los procesos del cliente.
    
    A diferencia del software tradicional, **BCS no se vende: se co-crea**.  
    Cada cliente participa en el diseño de su propio sistema, asegurando que la tecnología se adapte a su operación real.
    """)

# --- SECCIÓN: CÓMO FUNCIONA ---
st.subheader("⚙️ ¿Cómo funciona BCS?")
tab1, tab2 = st.tabs(["BCS Principal", "Sub–BCS"])

with tab1:
    col1, col2, col3= st.columns(3)
    with col1:
        st.write("""
        El **BCS Principal** es el núcleo de la plataforma.  
        Desde aquí se gestionan:
        - Usuarios, roles y autenticación.  
        - Licencias y monitoreo de sub–BCS.  
        - Bases de datos y módulos centrales.
        """)
    with col2:    
        st.image("assets/image1.jpg", caption="Estructura del BCS Principal", width=300)
    with col3:
        st.image("assets/image4.jpg", caption="Base de datos cloud", width=260)
with tab2:
    col1, col2,col3 = st.columns(3)
    with col1:
        st.write("""
        Cada **Sub–BCS** es una solución hija creada según el dolor del cliente.  
        Tiene su propio dashboard, base de datos y módulos personalizados.
        """)
    with col2:
        st.image("assets/image3.jpg", caption="Ejemplo de Sub–BCS", width=300)
    with col3:
        st.image("assets/image5.jpg", caption="Sistema modular", width=300)
st.divider()

# --- SECCIÓN: CASOS DE USO ---
st.subheader("🏭 Casos de uso")
industria = st.selectbox(
    "Selecciona una industria para ver cómo BCS puede ayudar:",
    ["Hospitalaria", "Pesquera", "Industrial", "Comercial"]
)

if industria == "Hospitalaria":
    st.info("🏥 **BCS Hospitalario:** gestiona pacientes, quirófanos, admisiones y personal médico.")
    col1,col2 = st.columns(2)
    with col1:
        st.image("assets/doctor_dashboard.jpg", caption="Dashboard de BCS Hospitalario", width=300)
    with col2:
        st.image("assets/historial_paciente.jpg", caption="Historial de pacientes inteligente", width=300)
elif industria == "Pesquera":
    st.info("⚓ **BCS Pesquero:** controla la flota, GPS marino, producción y mantenimiento de embarcaciones.")
    col1, col2 = st.columns(2)
    with col1:
        st.image("assets/image2.jpg", caption="Dashboard de BCS Pesquero", width=300)
    with col2:
        st.image("assets/descarga_atun.jpg", caption="Control de descargas", width=350)
elif industria == "Industrial":
    st.info("🏭 **BCS Industrial:** optimiza stock, lotes, mantenimiento y calidad de producción.")
else:
    st.info("🛍️ **BCS Comercial:** administra ventas, clientes, facturación y logística.")

st.divider()

# --- SECCIÓN: MODELO DE NEGOCIO ---
st.subheader("💼 Modelo de negocio")
with st.expander("Plan Básico"):
    st.write("Incluye módulos esenciales de gestión, usuarios y reportes, ideal para pequeñas empresas.")

with st.expander("Plan Profesional"):
    st.write("Agrega automatización avanzada, personalización modular y soporte técnico prioritario.")

with st.expander("Plan Enterprise"):
    st.write("Solución a medida con integración de IA, mantenimiento evolutivo y soporte 24/7.")

st.divider()

# --- SECCIÓN: POR QUÉ BCS ES DIFERENTE ---
st.subheader("💫 Ejemplos BCS")

def img_to_data_uri(img_path: str) -> str:
    p = Path(img_path)
    if not p.exists():
        return ""
    ext = p.suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    data = p.read_bytes()
    return f"data:image/{mime};base64," + base64.b64encode(data).decode()

img1 = img_to_data_uri("assets/image1.jpg")
img2 = img_to_data_uri("assets/image2.jpg")
img3 = img_to_data_uri("assets/image3.jpg")

# Carrusel con menor altura y margen inferior reducido para acercar la siguiente sección
html_code = f"""
<style>
.carousel {{
  position: relative;
  width: 500px;
  height: 180px; /* menor altura */
  overflow: hidden;
  margin: 8px auto 6px auto; /* reduce espacio inferior */
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}}

.slides {{
  display: flex;
  transition: transform 0.5s ease;
  width: calc(500px * 3);
}}

.slide {{
  min-width: 500px;
  height: 180px; /* coincide con la altura del carrusel */
}}

.slide img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 16px;
}}

.arrow {{
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.8rem;
  color: white;
  background: rgba(0,0,0,0.28);
  border: none;
  padding: 0.25em 0.5em;
  cursor: pointer;
  border-radius: 50%;
  z-index: 10;
}}

.left {{ left: 12px; }}
.right {{ right: 12px; }}

</style>

<div class="carousel">
  <div class="slides" id="slides">
    <div class="slide"><img src="{img1}"></div>
    <div class="slide"><img src="{img2}"></div>
    <div class="slide"><img src="{img3}"></div>
  </div>
  <button class="arrow left" onclick="moveSlide(-1)">❮</button>
  <button class="arrow right" onclick="moveSlide(1)">❯</button>
</div>

<script>
let currentIndex = 0;
const totalSlides = 3;
function moveSlide(direction) {{
  currentIndex = (currentIndex + direction + totalSlides) % totalSlides;
  const slides = document.getElementById("slides");
  slides.style.transform = `translateX(${{-500 * currentIndex}}px)`;
}}
</script>
"""

st.components.v1.html(html_code, height=240)

# --- SECCIÓN: EQUIPO ---
st.subheader("👥 Nuestro equipo")
col1, col2 = st.columns(2)
with col1:
    st.image("assets/foto imanol.jpg", width=180)
    st.markdown("### **Imanol Asolo**")
    st.caption("Presidente & CTO — Desarrollador de ecosistemas SaaS y AI Tools Developer")
with col2:
    st.image("https://i.imgur.com/yFxjzqG.png", width=180)
    st.markdown("### **[Nombre del Gerente]**")
    st.caption("CEO Comercial — Estrategia, relaciones y expansión de BCS Technologies")

st.divider()

# --- SECCIÓN: CONTACTO ---
st.subheader("📩 Agenda una reunión con BCS Technologies")
nombre = st.text_input("Nombre completo")
correo = st.text_input("Correo electrónico")
mensaje = st.text_area("Cuéntanos brevemente sobre tu negocio o proyecto")

if st.button("Enviar solicitud"):
    if nombre and correo and mensaje:
        st.success(f"✅ Gracias {nombre}, te contactaremos pronto a {correo} para coordinar una demo personalizada.")
    else:
        st.warning("⚠️ Por favor completa todos los campos antes de enviar.")

st.divider()

# --- PIE DE PÁGINA ---
st.markdown("""
<p style='text-align: center; color: gray;'>
© 2025 BCS Technologies SAS — Co-creamos el futuro digital de tu empresa.
</p>
""", unsafe_allow_html=True)
