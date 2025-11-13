# app.py — Landing BCS Blackbox (Partner Program)
import streamlit as st
import pandas as pd
from datetime import datetime
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="BCS Blackbox — Partner Program", page_icon="🧩", layout="wide")

# --- STYLES: BLACK THEME + ACCENTS ---
st.markdown(
    """
    <style>
    /* Page background */
    .stApp { background-color: #000000; color: #FFFFFF; }
    /* Headers */
    h1, h2, h3, h4, h5 { color: #FFFFFF; }
    /* Card-like containers */
    .card { background: linear-gradient(90deg, rgba(10,10,10,0.85), rgba(18,18,18,0.85)); padding: 18px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); }
    /* Buttons */
    .css-1emrehy.edgvbvh3 { background-color: #e60023 !important; color: white !important; } /* Primary red */
    .css-1emrehy.edgvbvh3:hover { background-color: #ff3347 !important; }
    /* Links */
    a { color: #00BFFF; }
    /* Form inputs background */
    .stTextInput>div>div>input { background-color: #0f0f0f; color: white; }
    .stTextArea>div>div>textarea { background-color: #0f0f0f; color: white; }
    /* Columns spacing */
    .big-gap { padding-top: 18px; padding-bottom: 18px; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Helper: save partner registrations locally ---
REG_FILE = "partners_registrations.csv"
def save_partner_submission(data: dict):
    df = pd.DataFrame([data])
    if os.path.exists(REG_FILE):
        df.to_csv(REG_FILE, mode='a', index=False, header=False)
    else:
        df.to_csv(REG_FILE, index=False)

# --- HERO SECTION ---
with st.container():
    col1, col2 = st.columns([2,1])
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size:42px; margin:0; color:#00BFFF;'>BCS Blackbox</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='margin:0; color:#e6e6e6;'>Tu puerta a negocios SaaS recurrentes</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color:#bfbfbf; font-size:16px;'>Conecta empresas con sub-BCS verticales (ERP, CRM, Asistentes Virtuales y más), y conviértete en Partner: trae clientes, recibe el 50% de la ganancia mensual.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.image("https://i.imgur.com/4N8SlKz.png", width=340)  # placeholder image

# CTA row - Full width
st.markdown("") 
c1, c2, c3, c4 = st.columns([1,1,1,1])
with c1:
    if st.button("🚀 Quiero ser Partner BCS", use_container_width=True):
        st.session_state.get("cta_clicked", True)
        st.info("¡Gran decisión! Baja al formulario de registro para completar tu inscripción.")
with c2:
    if st.button("📄 Ver Partner Kit (PDF)", use_container_width=True):
        st.info("Partner Kit enviado por email tras el registro. (Simulado)")
with c3:
    if st.button("📞 Solicitar Demo", use_container_width=True):
        st.info("Un asesor te contactará para coordinar la demo (simulado).")
with c4:
    if st.button("❓ ¿Qué es BCS?", use_container_width=True):
        st.info("""
        **BCS (Business Control System)** es un ecosistema de soluciones SaaS especializadas por sector.
        
        🔹 **Sistema modular**: Cada sub-BCS está diseñado para resolver problemas específicos de una industria
        
        🔹 **Plug & Play**: Los clientes obtienen una solución completa sin necesidad de desarrollo personalizado
        
        🔹 **Asistentes IA integrados**: Cada módulo incluye automatización inteligente y asistentes virtuales
        
        🔹 **Modelo Partner**: Tú conectas clientes, nosotros entregamos la tecnología y el soporte
        
        Como Partner BCS, no necesitas conocimientos técnicos - solo identifica empresas que necesiten digitalización.
        """)

st.write("---")

# --- WHY JOIN (BENEFITS) ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### ¿Por qué ser Partner BCS?", unsafe_allow_html=True)
    st.markdown("<p style='color:#bfbfbf; margin-bottom: 20px;'>Descubre las ventajas de formar parte del ecosistema BCS:</p>", unsafe_allow_html=True)
    
    cols = st.columns(2)
    with cols[0]:
        with st.expander("💵 Ingresos Recurrentes", expanded=False):
            st.markdown("**50% de las ganancias mensuales**")
            st.markdown("- Comisión del 50% sobre cada licencia vendida")
            st.markdown("- Ingresos pasivos mientras el cliente esté activo")
            st.markdown("- Sin límite en el número de clientes que puedes referir")
            st.markdown("- Pagos automáticos mensuales")
        
        with st.expander("🌍 Alcance Global", expanded=False):
            st.markdown("**Vende en tu región**")
            st.markdown("- Aprovecha tu red de contactos local")
            st.markdown("- Conocimiento del mercado regional")
            st.markdown("- Soporte en español y otros idiomas")
            st.markdown("- Adaptación a regulaciones locales")
    
    with cols[1]:
        with st.expander("🧩 Soluciones Listas", expanded=False):
            st.markdown("**ERP, CRM, IA y más**")
            st.markdown("- Más de 15 sub-BCS verticales disponibles")
            st.markdown("- Soluciones probadas en el mercado")
            st.markdown("- Implementación rápida (30 días)")
            st.markdown("- Asistentes IA integrados")
        
        with st.expander("🤝 Soporte Completo", expanded=False):
            st.markdown("**Formación y materiales**")
            st.markdown("- Kit de ventas profesional")
            st.markdown("- Capacitación comercial y técnica")
            st.markdown("- Demos pregrabadas y personalizadas")
            st.markdown("- Soporte técnico directo para tus clientes")
    
    st.markdown("<p style='color:#bfbfbf; margin-top: 20px;'>No necesitas ser desarrollador. Tú conectas, nosotros entregamos la solución y damos soporte técnico.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# --- INDUSTRIES GRID WITH EXPANDERS (MARKETING COPY) ---
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("## Sectores rentables para Partners", unsafe_allow_html=True)
st.markdown("<p style='color:#bfbfbf;'>Ofrece sub-BCS específicos que resuelven problemas reales. Aquí algunos ejemplos probados y listos para vender.</p>", unsafe_allow_html=True)

industry_list = [
    ("Pesca & Flotas", "FleetCore — Control de embarcaciones, bitácoras digitales y mantenimiento predictivo. Ideal para armadoras y patrones."),
    ("Hospitales & Clínicas", "MedCare Pro — Admisión, quirófanos, gestión de camas y asistente médico para preguntas frecuentes y seguimiento."),
    ("Restaurantes & Delivery", "SmartChef — Inventario, puntos de venta, reservas y análisis de demanda."),
    ("Veterinarias", "PetCore — Fichas clínicas, recordatorios de vacunación y CRM para clientes."),
    ("Hoteles & Turismo", "TravelCore — Reservas, check-in/out, asistentes multilingües y upsells."),
    ("Bufetes", "LawFlow — Gestión de casos, deadlines y documentación con recordatorios automáticos."),
    ("Consultoras & Contables", "Consultix — Gestión de proyectos, reportes automáticos y facturación."),
    ("Comercio & Retail", "RetailFlow — Inventario omnicanal, ventas y analítica por tienda."),
    ("Marketing & Agencias", "MarketFlow — Campañas, leads y automatización de informes."),
    ("Diseño & Creativos", "DesignFlow — Gestión de briefs, entregas y control de versiones."),
    ("Fábricas & Industria", "FactoryCore — Órdenes de producción, mantenimiento y trazabilidad."),
    ("Peluquerías & Salones", "SalonFlow — Agenda, caja y promociones automáticas."),
    ("Agro & Ganadería", "AgroCore — Registro de animales, tratamientos y trazabilidad."),
    ("Inmobiliarias", "RealCore — Gestión de propiedades, visitas y contratos."),
    ("Viajes & Agencias", "TripManager — Paquetes, itinerarios y atención al cliente.")
]

for title, desc in industry_list:
    with st.expander(f"🔹 {title}", expanded=False):
        st.markdown(f"**{title}** — {desc}")
        st.markdown("- **¿Por qué lo compran?**: Alta frecuencia de procesos, cumplimiento normativo y necesidad de digitalización.")
        st.markdown("- **Pitch corto para vender:** `Reduce costos, gana trazabilidad y automatiza reportes en 30 días sin inversión TI del cliente.`")
st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# --- ASISTENTES VIRTUALES SECTION ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 🤖 Asistentes Virtuales y Automatizaciones", unsafe_allow_html=True)
    st.markdown("<p style='color:#bfbfbf;'>Cada sub-BCS puede integrar asistentes entrenados con los documentos y datos del cliente: atenciones automáticas, generación de reportes, extracción de información y workflows por voz o chat.</p>", unsafe_allow_html=True)
    colA, colB = st.columns(2)
    colA.markdown("**Ejemplos de asistentes**")
    colA.markdown("- *FirstMate AI* (Pesca): genera bitácoras por voz, alerta cambios de clima y resume viajes.")
    colA.markdown("- *Nurse AI* (Salud): responde protocolos básicos y agenda citas.")
    colA.markdown("- *SmartAgent* (Retail): sugiere reposición y promociones.")
    colB.markdown("**Beneficios comerciales**")
    colB.markdown("- Ventas de módulos IA como add-ons premium.")
    colB.markdown("- Upsell natural para clientes existentes.")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# --- SIMULATOR: PARTNER EARNINGS ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 🧮 Simulador de Ganancias para Partners", unsafe_allow_html=True)
    st.markdown("<p style='color:#bfbfbf;'>Ajusta los parámetros para ver tu potencial de ingresos.</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        n_clients = st.slider("Empresas referidas", 1, 100, 5)
    with col2:
        users_per_client = st.slider("Usuarios promedio por empresa", 1, 50, 8)
    with col3:
        fee_per_user = st.select_slider("Fee promedio por usuario (USD/mes)", options=[25,50,75,100,150,200], value=100)

    monthly_revenue = n_clients * users_per_client * fee_per_user
    partner_commission = monthly_revenue * 0.5
    annual_commission = partner_commission * 12

    st.markdown(f"### Resultado estimado (dinámico)")
    st.markdown(f"- **Ingresos mensuales por licencias (cliente→BCS):** <span style='color:#bfbfbf;'>${monthly_revenue:,.0f}</span>", unsafe_allow_html=True)
    st.markdown(f"- **Tu comisión (50%):** <span style='color:#00BFFF; font-weight:700;'>${partner_commission:,.0f}/mes</span>", unsafe_allow_html=True)
    st.markdown(f"- **Comisión anual estimada:** <span style='color:#00BFFF; font-weight:700;'>${annual_commission:,.0f}/año</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# --- SOCIAL PROOF & STEPS ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## ✅ ¿Cómo funciona el proceso con tus clientes?", unsafe_allow_html=True)
    st.markdown("1. Presentas BCS Blackbox → 2. Coordinamos demo técnica → 3. Cierre comercial y onboarding → 4. Tú recibes 50% de la ganancia mensual mientras el cliente esté activo.")
    st.markdown("**Soporte y materiales:** recibirás kit de ventas, demos pregrabadas y capacitación comercial.")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# --- PARTNER REGISTRATION FORM (CTA) ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 🧾 Regístrate como Partner BCS", unsafe_allow_html=True)
    st.markdown("<p style='color:#bfbfbf;'>Completa el formulario y recibes el Partner Kit + capacitación. No necesitas experiencia técnica.</p>", unsafe_allow_html=True)
    with st.form("partner_form", clear_on_submit=True):
        cols = st.columns(3)
        name = cols[0].text_input("Nombre completo")
        email = cols[1].text_input("Correo electrónico")
        country = cols[2].text_input("País / Región")
        company = st.text_input("Empresa / Marca (opcional)")
        niche = st.selectbox("¿En qué sector te enfocas?", ["Pesca", "Salud", "Restauración", "Retail", "Marketing", "Consultoría", "Otros"])
        phone = st.text_input("Teléfono / WhatsApp (opcional)")
        notes = st.text_area("Cuéntanos tu experiencia y red de contactos (opcional)")
        accept = st.checkbox("Acepto recibir comunicaciones y el Partner Kit (simulado)")
        submitted = st.form_submit_button("Enviar registro y recibir Partner Kit")

        if submitted:
            if not name or not email:
                st.warning("Por favor completa al menos nombre y correo.")
            else:
                data = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "name": name,
                    "email": email,
                    "country": country,
                    "company": company,
                    "niche": niche,
                    "phone": phone,
                    "notes": notes
                }
                save_partner_submission(data)
                st.success("✅ Registro recibido. Te enviaremos el Partner Kit en breve (simulado).")
                st.info("Próximos pasos: capacitación, material comercial y demo para tus primeros clientes.")
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# --- FOOTER / CONTACT ---
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([3,1])
    with c1:
        st.markdown("### ¿Listo para ganar con BCS Blackbox?")
        st.markdown("<p style='color:#bfbfbf;'>Si prefieres, escríbenos a <a href='mailto:partners@codecodix.com'>partners@codecodix.com</a> o solicita una demo personalizada.</p>", unsafe_allow_html=True)
    with c2:
        st.markdown("**CodeCodix**")
        st.markdown("BCS Blackbox")
        st.markdown("© 2025")
    st.markdown("</div>", unsafe_allow_html=True)
