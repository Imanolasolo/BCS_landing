# app.py
import streamlit as st
import sqlite3
from pathlib import Path
from data.content import *
from db_setup import DB_PATH

# ---------- Helpers DB ----------
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def save_lead(nombre, email, telefono, sector, mensaje, source="landing"):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO leads (nombre,email,telefono,sector,mensaje,source) VALUES (?,?,?,?,?,?)
    """, (nombre, email, telefono, sector, mensaje, source))
    conn.commit()
    conn.close()

# ---------- Secciones ----------
def hero_section():
    st.title("🎯 BCS Blackbox — Soluciones IA listas para vender")
    st.markdown("""
    ### Conviértete en Partner y gana vendiendo soluciones de IA a empresas de tu región
    
    **Sin desarrollo, sin inversión inicial, con todo el soporte técnico incluido.**
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("💰 **Comisiones del 40-50%** por cada venta")
        st.info("🚀 **Soluciones listas** — solo vendes, nosotros desarrollamos")
    with col2:
        st.info("📚 **Capacitación incluida** — te enseñamos todo")
        st.info("🎯 **Sectores probados** con casos de éxito reales")

def que_es_bcs():
    st.header("¿Qué es BCS Blackbox?")
    
    st.markdown("""
    **BCS (Business Configuration System) Blackbox** es un ecosistema de **soluciones de IA pre-configuradas** 
    diseñadas específicamente para diferentes industrias.
    
    ### 🎁 Imagínalo como una "caja negra mágica" que:
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ✅ Ya está **programada y probada**  
        ✅ Solo necesita **configurarse** para cada cliente  
        ✅ Funciona **desde el día 1**  
        """)
    with col2:
        st.markdown("""
        ✅ Se **actualiza automáticamente**  
        ✅ Incluye **soporte técnico completo**  
        ✅ Genera **ingresos recurrentes**  
        """)
    
    st.markdown("---")
    
    # Expanders interactivos
    with st.expander("🔍 ¿Qué significa 'Blackbox'?", expanded=False):
        st.markdown("""
        ### El concepto de "caja negra"
        
        En tecnología, una **blackbox** es un sistema que:
        - **Funciona sin que veas el código interno** — como un iPhone, solo lo usas
        - **Resuelve problemas complejos de forma simple** — tú no programas, solo configuras
        - **Es confiable y predecible** — siempre da los mismos resultados de calidad
        
        **Para el partner:** No necesitas ser programador ni entender IA. Solo necesitas:
        1. Entender el negocio de tu cliente
        2. Configurar los parámetros básicos
        3. Activar la solución
        
        **Nosotros nos encargamos de:** programación, servidores, actualizaciones, bugs, seguridad, todo.
        """)
    
    with st.expander("🎯 ¿Qué NO es BCS?", expanded=False):
        st.markdown("""
        ### Para que quede claro:
        
        ❌ **NO es desarrollo a medida** — no hacemos software desde cero para cada cliente  
        ❌ **NO requiere programadores** — tú no necesitas contratar desarrolladores  
        ❌ **NO es una licencia de software** — no vendes acceso a una app genérica  
        ❌ **NO necesitas infraestructura** — nosotros manejamos los servidores  
        
        ✅ **SÍ es una solución vertical lista** — específica para cada industria  
        ✅ **SÍ es personalizable** — se adapta al negocio de cada cliente  
        ✅ **SÍ es escalable** — crece con el cliente sin costos adicionales  
        ✅ **SÍ genera ingresos recurrentes** — tú cobras cada mes mientras el cliente lo use  
        """)
    
    with st.expander("🏗️ ¿Cómo funciona el modelo de negocio?", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### Tu rol como Partner:
            
            1. **Prospección** (5-10 hrs/semana)
               - Identificas empresas objetivo
               - Usas nuestro material de venta
               - Agendas demos
            
            2. **Venta** (2-3 hrs por cliente)
               - Presentas la solución
               - Cierras el contrato
               - Coordinas implementación
            
            3. **Cobro** (automático)
               - Recibe comisiones mensuales
               - Sin trabajo operativo adicional
               - Ingresos recurrentes garantizados
            """)
        
        with col2:
            st.markdown("""
            ### Nuestro rol como Codecodix:
            
            1. **Implementación** (1-2 semanas)
               - Instalamos la solución
               - Configuramos según el cliente
               - Capacitamos al personal
            
            2. **Soporte continuo** (24/7)
               - Atendemos problemas técnicos
               - Actualizamos el sistema
               - Añadimos nuevas funciones
            
            3. **Facturación** (automática)
               - Cobramos al cliente
               - Te transferimos tu comisión
               - Enviamos reportes mensuales
            """)
    
    with st.expander("💡 Ejemplo práctico: Restaurante 'El Buen Sabor'", expanded=False):
        st.markdown("""
        ### Caso real simplificado:
        
        **Cliente:** Restaurante mediano, 80 mesas, $150K facturación mensual
        
        **Problema:** 
        - Pierden 30% de llamadas por línea ocupada en hora pico
        - Personal de recepción sobrecargado
        - Errores en pedidos telefónicos (15% de órdenes incorrectas)
        - No tienen sistema de reservas online
        
        **Solución BCS:** SmartHost - Asistente Virtual para Restaurantes
        
        ---
        
        #### 📋 Proceso paso a paso:
        
        **Día 1-2: Venta (Partner)**
        - Presentas SmartHost con demo en vivo
        - Muestras reducción de errores y aumento de ventas
        - Cierras contrato: $600/mes por 12 meses
        
        **Semana 1: Implementación (Codecodix)**
        - Configuramos asistente de voz con IA
        - Integramos con sistema de mesas y menú digital
        - Conectamos WhatsApp Business para pedidos
        - Configuramos página web con reservas online
        
        **Semana 2: Capacitación (Codecodix)**
        - 1 hora con gerente y hostess
        - Aprenden a usar dashboard de reservas
        - Prueban el asistente y ajustan respuestas
        
        **Mes 1 en adelante: Operación**
        - **Asistente atiende llamadas 24/7:**
          - "Buenas tardes, Restaurante El Buen Sabor, ¿desea hacer una reserva o un pedido?"
          - Toma pedidos completos con confirmación
          - Agenda reservas automáticamente
          - Responde consultas sobre menú y horarios
        - **Resultados medibles:**
          - 0% llamadas perdidas (antes 30%)
          - 95% precisión en pedidos (antes 85%)
          - +40 reservas mensuales extra = +$4,800 en ventas
          - Personal de recepción liberado para atención presencial
        
        **ROI para cliente:**
        - Inversión: $600/mes
        - Nuevas ventas: +$4,800/mes
        - **Retorno: 8x**
        
        **Tu ganancia como Partner:**
        - Comisión 40% = $240/mes
        - x 12 meses = $2,880/año
        - Por UN solo cliente
        - **Sin trabajo adicional después del cierre**
        """)
        
        st.success("💰 Si consigues 10 restaurantes así: $28,800/año en comisiones recurrentes")
        
        with st.container():
            st.markdown("#### 🎙️ Ejemplo de conversación del asistente:")
            st.code("""
Cliente: "Hola, quisiera hacer una reserva"
SmartHost: "¡Por supuesto! ¿Para cuántas personas y qué día?"
Cliente: "Para 4 personas, este sábado a las 8pm"
SmartHost: "Perfecto, tengo disponibilidad el sábado a las 8pm para 4 personas. ¿A nombre de quién hago la reserva?"
Cliente: "Juan Pérez"
SmartHost: "Excelente Juan. ¿Me proporciona un número de contacto?"
Cliente: "0999123456"
SmartHost: "Listo, su reserva está confirmada para el sábado a las 8pm, 4 personas. Le enviaré un recordatorio por WhatsApp. ¿Desea algo más?"
            """, language="text")
    
    with st.expander("🏥 Ejemplo práctico: Dr. Ramírez - Consultorio Odontológico", expanded=False):
        st.markdown("""
        ### Caso real simplificado:
        
        **Cliente:** Consultorio odontológico independiente, 1 doctor + 1 asistente
        
        **Problema:** 
        - 40% de pacientes no contestan llamadas de confirmación
        - Alto índice de inasistencias (25%)
        - Asistente pasa 3 horas/día solo agendando citas
        - No hay sistema para recordatorios automáticos
        - Pierden tiempo valioso en tareas administrativas
        
        **Solución BCS:** MediAssist - Asistente Virtual para Consultorios
        
        ---
        
        #### 📋 Proceso paso a paso:
        
        **Día 1-2: Venta (Partner)**
        - Presentas MediAssist con caso similar
        - Muestras ahorro de tiempo y reducción de inasistencias
        - Cierras contrato: $450/mes por 12 meses
        
        **Semana 1: Implementación (Codecodix)**
        - Configuramos asistente con conocimiento médico básico
        - Integramos agenda electrónica con calendario del doctor
        - Conectamos WhatsApp y teléfono virtual
        - Configuramos sistema de recordatorios automáticos
        
        **Semana 2: Capacitación (Codecodix)**
        - 1 hora con doctor y asistente
        - Aprenden a usar dashboard de citas
        - Configuran horarios y tipos de consulta
        - Prueban respuestas del asistente
        
        **Mes 1 en adelante: Operación**
        - **Asistente gestiona citas 24/7:**
          - Atiende llamadas: "Consultorio Dr. Ramírez, ¿en qué puedo ayudarle?"
          - Agenda citas según disponibilidad real
          - Envía confirmaciones automáticas por WhatsApp
          - Recordatorios 48h y 2h antes de cada cita
          - Responde preguntas frecuentes (horarios, ubicación, costos)
          - Permite a pacientes reprogramar online
        
        - **Resultados medibles:**
          - Inasistencias reducidas de 25% a 8%
          - Asistente ahorra 15 horas/semana en llamadas
          - +12 citas mensuales por mejor gestión = +$1,200 en ingresos
          - Satisfacción de pacientes aumenta (atención 24/7)
          - Doctor puede atender más pacientes
        
        **ROI para cliente:**
        - Inversión: $450/mes
        - Nuevos ingresos: +$1,200/mes
        - Ahorro en tiempo: 60 hrs/mes x $10/hr = $600/mes
        - **Retorno total: 4x**
        
        **Tu ganancia como Partner:**
        - Comisión 50% = $225/mes
        - x 12 meses = $2,700/año
        - Por UN solo cliente
        - **Sin trabajo adicional después del cierre**
        """)
        
        st.success("💰 Si consigues 15 consultorios así: $40,500/año en comisiones recurrentes")
        
        with st.container():
            st.markdown("#### 🎙️ Ejemplo de conversación del asistente:")
            st.code("""
Paciente: "Buenos días, necesito una cita con el doctor"
MediAssist: "Buenos días. ¿Es para limpieza dental o tiene alguna molestia específica?"
Paciente: "Me duele una muela"
MediAssist: "Entiendo, es urgente. Tengo disponibilidad hoy a las 4pm o mañana a las 10am. ¿Cuál prefiere?"
Paciente: "Mañana a las 10 está bien"
MediAssist: "Perfecto. ¿A nombre de quién?"
Paciente: "María González"
MediAssist: "¿Es su primera visita María o ya es paciente del Dr. Ramírez?"
Paciente: "Ya soy paciente"
MediAssist: "Excelente. Su cita está confirmada para mañana jueves a las 10am. Le enviaré un recordatorio por WhatsApp. La ubicación es Av. Principal 123. ¿Algo más en lo que pueda ayudarle?"
            """, language="text")
            
            st.info("📱 El sistema también envía: Recordatorio 48h antes + Recordatorio 2h antes + Opción de confirmar/cancelar con un clic")

def ejemplos_partners():
    st.header("📊 Ejemplos Reales de Partners")
    st.markdown("*Así es como otros partners están ganando con BCS*")
    
    # Ejemplo 1
    with st.expander("🏥 **María - Partner en Salud (Guayaquil)** — Gana $1,500/mes", expanded=False):
        col1, col2 = st.columns([2,1])
        with col1:
            st.markdown("""
            **Perfil:** Consultora de negocios con contactos en clínicas
            
            **Qué vende:**
            - Sistema de gestión de citas con IA
            - Recordatorios automáticos a pacientes
            - Análisis de datos de consultas
            
            **Resultados:**
            - 3 clínicas activas pagando $500/mes c/u
            - Comisión: 50% = $750/mes
            - Bonus por renovación: $750/mes
            - **Total: $1,500/mes recurrente**
            """)
        with col2:
            st.metric("Clientes", "3")
            st.metric("Ingreso mensual", "$1,500")
            st.metric("Tiempo invertido", "5 hrs/semana")
    
    # Ejemplo 2
    with st.expander("🍽️ **Carlos - Partner en Restaurantes (Quito)** — Gana $2,400/mes"):
        col1, col2 = st.columns([2,1])
        with col1:
            st.markdown("""
            **Perfil:** Dueño de agencia de marketing, conoce restauranteros
            
            **Qué vende:**
            - SmartChef: optimización de inventario con IA
            - Predicción de demanda
            - Reducción de desperdicio
            
            **Resultados:**
            - 4 restaurantes medianos ($600/mes c/u)
            - Comisión: 40% = $960/mes
            - 2 cadenas grandes ($1,800/mes c/u, comisión $720)
            - **Total: $2,400/mes recurrente**
            """)
        with col2:
            st.metric("Clientes", "6")
            st.metric("Ingreso mensual", "$2,400")
            st.metric("Tiempo invertido", "8 hrs/semana")
    
    # Ejemplo 3
    with st.expander("🐟 **Roberto - Partner en Pesca (Manta)** — Gana $3,000/mes"):
        col1, col2 = st.columns([2,1])
        with col1:
            st.markdown("""
            **Perfil:** Ingeniero pesquero con red de contactos en el sector
            
            **Qué vende:**
            - Sistema de monitoreo de flota pesquera
            - Predicción de zonas óptimas de pesca
            - Control de calidad con IA
            
            **Resultados:**
            - 2 empresas pesqueras grandes ($3,000/mes c/u)
            - Comisión: 50% = $3,000/mes
            - **Total: $3,000/mes recurrente**
            """)
        with col2:
            st.metric("Clientes", "2")
            st.metric("Ingreso mensual", "$3,000")
            st.metric("Tiempo invertido", "6 hrs/semana")

def sectores_disponibles():
    st.header("🎯 Sectores Disponibles")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🏥 Salud")
        st.write("Clínicas, consultorios, laboratorios")
        st.caption("Ticket promedio: $500/mes")
        
        st.markdown("### 🍽️ Restaurantes")
        st.write("Restaurantes, cafeterías, bares")
        st.caption("Ticket promedio: $600/mes")
    
    with col2:
        st.markdown("### 🐟 Pesca")
        st.write("Empresas pesqueras, procesadoras")
        st.caption("Ticket promedio: $3,000/mes")
        
        st.markdown("### 🛒 Retail")
        st.write("Tiendas, supermercados, boutiques")
        st.caption("Ticket promedio: $800/mes")
    
    with col3:
        st.markdown("### 🏭 Manufactura")
        st.write("Fábricas, talleres, productoras")
        st.caption("Ticket promedio: $2,000/mes")
        
        st.markdown("### 🏨 Turismo")
        st.write("Hoteles, agencias, tours")
        st.caption("Ticket promedio: $1,200/mes")

def beneficios_partner():
    st.header("✅ ¿Por qué ser Partner BCS?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 💰 Ganancias
        - Comisiones del 40-50%
        - Ingresos recurrentes mensuales
        - Sin límite de clientes
        - Bonos por renovación
        """)
        
        st.markdown("""
        ### 🎓 Soporte
        - Capacitación completa gratis
        - Material de ventas incluido
        - Soporte técnico 24/7
        - Demos y presentaciones listas
        """)
    
    with col2:
        st.markdown("""
        ### 🚀 Facilidad
        - No necesitas ser técnico
        - No desarrollas nada
        - No das soporte técnico
        - Solo vendes y cobras
        """)
        
        st.markdown("""
        ### 📈 Crecimiento
        - Territorios exclusivos disponibles
        - Posibilidad de sub-partners
        - Escalable sin límites
        - Casos de éxito comprobados
        """)

def formulario_registro():
    st.header("📝 Regístrate como Partner")
    st.markdown("*Completa el formulario y te contactamos en 24 horas*")
    
    with st.form("registro_partner", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre completo *")
            email = st.text_input("Email *")
            telefono = st.text_input("WhatsApp *")
        
        with col2:
            ciudad = st.text_input("Ciudad / Región")
            sector = st.selectbox("Sector de interés principal", 
                                 ["Salud", "Restaurantes", "Pesca", "Retail", "Manufactura", "Turismo", "Otro"])
            experiencia = st.radio("¿Tienes experiencia en ventas?", 
                                  ["Sí, mucha", "Algo", "No, pero quiero aprender"])
        
        mensaje = st.text_area("¿Por qué quieres ser partner? (opcional)")
        
        submitted = st.form_submit_button("🚀 Quiero ser Partner", use_container_width=True)
        
        if submitted:
            if not nombre or not email or not telefono:
                st.error("⚠️ Por favor completa los campos obligatorios (*)")
            else:
                save_lead(nombre, email, telefono, sector, 
                         f"Experiencia: {experiencia}. Mensaje: {mensaje}", 
                         source="registro_partner")
                st.success("✅ ¡Registro exitoso! Te contactaremos en 24 horas.")
                st.balloons()
                st.info("📧 Revisa tu email — te enviaremos el kit de bienvenida")

# ---------- Layout Principal ----------
st.set_page_config(
    page_title="BCS Blackbox — Programa de Partners", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hero
hero_section()

st.markdown("---")

# Qué es BCS
que_es_bcs()

st.markdown("---")

# Ejemplos de partners (SECCIÓN PRINCIPAL)
ejemplos_partners()

st.markdown("---")

# Sectores
sectores_disponibles()

st.markdown("---")

# Beneficios
beneficios_partner()

st.markdown("---")

# Formulario de registro
formulario_registro()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px;'>
    <h3>¿Preguntas?</h3>
    <p>📧 partners@codecodix.com  •  📱 WhatsApp: +593 XXX XXX XXX</p>
    <p><small>Codecodix AI Lab — Soluciones de IA para empresas</small></p>
</div>
""", unsafe_allow_html=True)

