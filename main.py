import streamlit as st
from utils.database import get_connection, init_leads_table
import base64

# Configuración de la página
st.set_page_config(
    page_title="BCS - Business Core Software",
    layout="wide"
)

# Function to encode image as base64 to set as background
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception as e:
        st.error(f"Error al leer el archivo '{bin_file}': {e}")
        return None

# Encode the background image
img_base64 = get_base64_of_bin_file('assets/background.jpg')

if img_base64:
    # Set the background image using the encoded base64 string
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url('data:image/jpeg;base64,{img_base64}') no-repeat center center fixed;
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Inicializa la tabla de leads
init_leads_table()


# Background image (base64) if background.jpg exists in the same folder
import os
import base64

bg_path = os.path.join(os.path.dirname(__file__), "background.jpg")
if os.path.exists(bg_path):
        with open(bg_path, "rb") as f:
                data = f.read()
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url('data:image/jpg;base64,{b64}');
            background-size: cover;
            background-position: center;
        }}
        </style>
        """, unsafe_allow_html=True)

# Título principal
col1,col2 = st.columns([1,6])
with col1:
    st.image("assets/BCS_logo.png", width=100)
with col2:
    st.header(":red[BCS] - Business Core Software")
st.write("Tu núcleo digital empresarial con asistentes inteligentes IA")

# Expander introductivo sobre qué puede hacer BCS
with st.expander(":blue[¿Qué puede hacer BCS por tu empresa?]"):
    st.write("""
    BCS transforma tu empresa digitalmente y te ayuda a:
    - Implementar soluciones digitales a medida para tu negocio.
    - Integrar asistentes inteligentes IA para optimizar procesos internos.
    - Gestionar proyectos y procesos como Product Owner externo si lo deseas.
    - Monitorear KPIs y tomar decisiones basadas en datos en tiempo real.
    - Mejorar la eficiencia operativa y reducir costos internos.
    """)

# Expanders por sector
col1, col2, col3 = st.columns(3)
with col1:
    with st.expander(":blue[Salud]"):
        st.write("Gestión de pacientes, hospitalización y asistencia IA personalizada para hospitales.")

with col2:
    with st.expander(":blue[Educación]"):
        st.write("Gestión de estudiantes, cursos y asistentes de tutoría IA para colegios y universidades.")

with col3:
    with st.expander(":blue[Retail]"):
        st.write("Gestión de clientes, inventario y ventas con asistentes inteligentes para retail.")

# Expander Product Ownership
with st.expander(":blue[Product Ownership - BCS como tu PO externo]"):
    st.write("""
    BCS puede actuar como tu **Product Owner externo**, asegurando que tus proyectos digitales y procesos internos se ejecuten de manera eficiente y alineada con los objetivos de tu empresa. Con BCS como PO externo, tu negocio recibe:

    - **Gestión de proyectos digitales:** visión, roadmap y priorización de funcionalidades.
    - **Optimización de procesos internos:** mejora de eficiencia y KPIs claros.
    - **Comunicación con stakeholders:** reportes y métricas para la toma de decisiones.
    - **Asesoría y soporte continuo:** recomendaciones estratégicas y tecnológicas.
    """)

# Beneficios
with st.expander(":blue[Beneficios de BCS]"):
    st.write("""
    - Soluciones digitales a medida para cada empresa.
    - Asistentes IA entrenados con datos propios.
    - Rápida implementación sin equipos técnicos internos.
    """)

# Formulario de captación de leads (botón normal)
st.markdown("## Solicita tu demo o piloto")
with st.expander(":red-badge[Formulario de contacto]"):
    nombre = st.text_input("Nombre", key="lead_nombre")
    empresa = st.text_input("Empresa", key="lead_empresa")
    email = st.text_input("Correo electrónico", key="lead_email")
    sector = st.selectbox("Sector de interés", ["Salud", "Educación", "Retail"], key="lead_sector")
    mensaje = st.text_area("Mensaje (opcional)", key="lead_mensaje")

    if st.button("Enviar", type="primary"):
        if not nombre or not email:
            st.error("Por favor, completa al menos el nombre y el correo electrónico.")
        else:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO leads (nombre, empresa, email, sector, mensaje) 
                VALUES (?, ?, ?, ?, ?)
            """, (nombre, empresa, email, sector, mensaje))
            conn.commit()
            conn.close()
            st.success("¡Gracias! Nos pondremos en contacto contigo pronto.")

# Footer
st.markdown("---")
st.write("© 2025 Imanol Asolo | BCS - Business Core Software")
