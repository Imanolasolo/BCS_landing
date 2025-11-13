# CRM_partnerBCS.py - Sistema CRM para Partners BCS Blackbox
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CRM Partner BCS", 
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATABASE SETUP ---
def init_database():
    conn = sqlite3.connect('crm_partner_bcs.db')
    cursor = conn.cursor()
    
    # Tabla de Partners
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            region TEXT,
            specialization TEXT,
            created_date DATE,
            status TEXT DEFAULT 'active',
            created_by TEXT DEFAULT 'admin'
        )
    ''')
    
    # Migración: Agregar columna password_hash si no existe
    try:
        cursor.execute("ALTER TABLE partners ADD COLUMN password_hash TEXT")
    except sqlite3.OperationalError:
        # La columna ya existe, continuar
        pass
    
    # Migración: Agregar columna created_by si no existe
    try:
        cursor.execute("ALTER TABLE partners ADD COLUMN created_by TEXT DEFAULT 'admin'")
    except sqlite3.OperationalError:
        # La columna ya existe, continuar
        pass
    
    # Tabla de Leads
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER,
            company_name TEXT NOT NULL,
            contact_name TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            industry TEXT,
            company_size INTEGER,
            pain_points TEXT,
            lead_source TEXT,
            status TEXT DEFAULT 'new',
            created_date DATE,
            last_contact DATE,
            notes TEXT,
            FOREIGN KEY (partner_id) REFERENCES partners (id)
        )
    ''')
    
    # Tabla de Oportunidades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            partner_id INTEGER,
            opportunity_name TEXT NOT NULL,
            bcs_solution TEXT,
            estimated_users INTEGER,
            price_per_user REAL,
            total_value REAL,
            probability INTEGER,
            stage TEXT DEFAULT 'discovery',
            expected_close_date DATE,
            actual_close_date DATE,
            status TEXT DEFAULT 'open',
            notes TEXT,
            created_date DATE,
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (partner_id) REFERENCES partners (id)
        )
    ''')
    
    # Tabla de Actividades
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            opportunity_id INTEGER,
            partner_id INTEGER,
            activity_type TEXT,
            description TEXT,
            activity_date DATE,
            follow_up_date DATE,
            completed BOOLEAN DEFAULT FALSE,
            created_date DATETIME,
            FOREIGN KEY (lead_id) REFERENCES leads (id),
            FOREIGN KEY (opportunity_id) REFERENCES opportunities (id),
            FOREIGN KEY (partner_id) REFERENCES partners (id)
        )
    ''')
    
    # Tabla de Comisiones
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS commissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partner_id INTEGER,
            opportunity_id INTEGER,
            client_name TEXT,
            monthly_value REAL,
            commission_rate REAL DEFAULT 0.5,
            commission_amount REAL,
            start_date DATE,
            status TEXT DEFAULT 'active',
            payment_date DATE,
            notes TEXT,
            FOREIGN KEY (partner_id) REFERENCES partners (id),
            FOREIGN KEY (opportunity_id) REFERENCES opportunities (id)
        )
    ''')
    
    # Verificar y actualizar partners existentes sin password_hash
    cursor.execute("SELECT id, email FROM partners WHERE password_hash IS NULL OR password_hash = ''")
    partners_without_password = cursor.fetchall()
    
    for partner_id, email in partners_without_password:
        # Asignar contraseña por defecto
        default_password = "123456"
        password_hash = hash_password(default_password)
        cursor.execute("UPDATE partners SET password_hash = ? WHERE id = ?", (password_hash, partner_id))
    
    # Actualizar created_by para partners existentes si es NULL
    cursor.execute("UPDATE partners SET created_by = 'admin' WHERE created_by IS NULL OR created_by = ''")
    
    # Crear usuario admin por defecto si no existe
    cursor.execute("SELECT * FROM partners WHERE email = 'admin@bcsblackbox.com'")
    if not cursor.fetchone():
        admin_password_hash = hash_password("admin123")
        created_date_str = datetime.now().date().strftime('%Y-%m-%d')
        cursor.execute("""
            INSERT INTO partners (name, email, password_hash, phone, region, specialization, created_date, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Admin BCS", "admin@bcsblackbox.com", admin_password_hash, "+1-555-BCS-ADMIN", "Global", "Administrador", created_date_str, "admin", "system"))
    
    conn.commit()
    conn.close()

# --- AUTHENTICATION FUNCTIONS ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    return hash_password(password) == password_hash

def authenticate_user(email, password):
    conn = get_db_connection()
    user = pd.read_sql_query(
        "SELECT * FROM partners WHERE email = ?", 
        conn, params=[email]
    )
    conn.close()
    
    if not user.empty:
        user_data = user.iloc[0]
        if verify_password(password, user_data['password_hash']):
            return {
                'id': user_data['id'],
                'name': user_data['name'],
                'email': user_data['email'],
                'status': user_data['status'],
                'region': user_data['region'],
                'specialization': user_data['specialization']
            }
    return None

def show_login():
    col1, col2,col3 = st.columns([1, 1.7, 0.6])
    with col1:
        st.image("assets/BCS_logo.png", width=250)
    with col2:
        st.markdown("""
        <div style="display: flex; justify-content: left; align-items: center; height: 60vh;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 1rem; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                        text-align: center; color: white; min-width: 450px;">
                <h1 style="margin-bottom: 2rem; font-size: 2.5rem;">🚀 BCS CRM</h1>
                <p style="font-size: 1.2rem; margin-bottom: 2rem;">Sistema de Gestión para Partners</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:    
            
        st.image("assets/logo.png", width=250)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.image("assets/image1.jpg", width=300)
        with st.expander("🏢 ¿Qué es BCS BlackBox?"):
            st.markdown("""
            **BCS BlackBox** es una consultora tecnológica especializada en soluciones avanzadas de datos e inteligencia artificial para empresas.
            
            ### 🎯 **Nuestros Servicios:**
            - **📊 Procesamiento de Datos** - Automatización y optimización de flujos de información
            - **🤖 Análisis Predictivo** - Modelos de machine learning para toma de decisiones
            - **⚡ Automatización de Procesos** - Reducción de tareas manuales y errores
            - **🧠 Inteligencia Artificial** - Implementación de soluciones AI personalizadas
            - **💼 Consultoría Estratégica** - Asesoramiento en transformación digital
            
            ### 🏭 **Industrias que Atendemos:**
            - 🐟 **Pesca** - Optimización de capturas y trazabilidad
            - 🏥 **Salud** - Análisis de datos médicos y eficiencia hospitalaria  
            - 🍽️ **Restauración** - Gestión de inventarios y predicción de demanda
            - 🛒 **Retail** - Análisis de comportamiento del consumidor
            - ⚖️ **Legal** - Automatización de documentos y análisis de casos
            - 📈 **Marketing** - Segmentación y personalización de campañas
            
            ### 💰 **Beneficios Típicos:**
            - **70-90%** reducción en tiempo de procesamiento manual
            - **15-25%** incremento en eficiencia operativa
            - **40-60%** mejora en precisión de datos
            - **ROI** típico del **300-500%** en el primer año
            """)

    with col2:
        st.markdown("### 🔐 Iniciar Sesión")
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="usuario@email.com")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Tu contraseña")
            
            col1, col2 = st.columns(2)
            with col1:
                login_button = st.form_submit_button("🚀 Entrar", type="primary", use_container_width=True)
            with col2:
                demo_button = st.form_submit_button("👀 Demo Partner", use_container_width=True)
            
            if login_button:
                if email and password:
                    user = authenticate_user(email, password)
                    if user:
                        st.session_state['authenticated'] = True
                        st.session_state['user'] = user
                        st.session_state['user_type'] = 'admin' if user['status'] == 'admin' else 'partner'
                        st.success(f"✅ Bienvenido, {user['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas")
                else:
                    st.warning("⚠️ Por favor ingresa email y contraseña")
            
            if demo_button:
                # Usuario demo para testing
                st.session_state['authenticated'] = True
                st.session_state['user'] = {
                    'id': 999,
                    'name': 'Demo Partner',
                    'email': 'demo@partner.com',
                    'status': 'active',
                    'region': 'Demo Region',
                    'specialization': 'Todas las industrias'
                }
                st.session_state['user_type'] = 'partner'
                st.info("🎯 Entrando en modo Demo...")
                st.rerun()
    with col3:    
            
        st.image("assets/image3.jpg", width=300)
        with st.expander("📋 Instrucciones de Uso del CRM"):
            st.markdown("""
            ### 🔐 **Acceso al Sistema**
            
            **Para Administradores:**
            1. Usuario: `admin@bcsblackbox.com`
            2. Contraseña: `admin123`
            3. Acceso completo a gestión de partners y reportes
            
            **Para Partners:**
            1. Utiliza las credenciales proporcionadas por BCS
            2. Si es tu primer acceso, cambia tu contraseña
            3. Usa el botón **"👀 Demo Partner"** para probar el sistema
            
            ### 🎯 **Funcionalidades Principales**
            
            **📊 Dashboard** - Vista general de tu actividad y métricas  
            **👥 Leads** - Gestión de clientes potenciales:
            - Crear nuevos leads con información completa
            - Registrar pain points y necesidades del cliente
            - Actualizar estados (new → contacted → qualified)
            
            **🎯 Oportunidades** - Pipeline de ventas:
            - Crear oportunidades de leads calificados
            - Gestionar etapas del proceso de venta
            - Actualizar probabilidades y valores
            
            **📋 Actividades** - Registro de interacciones:
            - Llamadas, emails, reuniones, propuestas
            - Seguimiento cronológico de contactos
            - Notas detalladas de conversaciones
            
            **💰 Comisiones** - Seguimiento de ganancias:
            - Cálculo automático de comisiones
            - Reportes por período
            - Objetivos y metas
            
            ### ✅ **Proceso de Trabajo Recomendado**
            1. **Crear Lead** → Registrar cliente potencial
            2. **Primera Llamada** → Confirmar interés y necesidades
            3. **Registrar Actividad** → Documentar conversación
            4. **Calificar Lead** → Evaluar fit con BCS
            5. **Crear Oportunidad** → Si hay potencial real
            6. **Seguimiento Regular** → Mantener contacto activo
            7. **Actualizar Pipeline** → Mover etapas según progreso
            8. **Cerrar Oportunidad** → Ganar o perder, documentar resultado
            
            ### 🆘 **¿Necesitas Ayuda?**
            - 📧 Email: `soporte@bcsblackbox.com`
            - 📚 Manual completo disponible en el sistema
            - 💬 Chat de soporte durante horario laboral
            """)
        
        

def logout():
    for key in ['authenticated', 'user', 'user_type']:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

# --- STYLES ---
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    .metric-card {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
    }
    .status-new { color: #059669; }
    .status-contacted { color: #0891b2; }
    .status-qualified { color: #7c3aed; }
    .status-proposal { color: #dc2626; }
    .status-closed-won { color: #16a34a; font-weight: bold; }
    .status-closed-lost { color: #dc2626; }
    .sidebar .sidebar-content {
        background-color: #1e293b;
    }
</style>
""", unsafe_allow_html=True)

# --- UTILITY FUNCTIONS ---
def get_db_connection():
    return sqlite3.connect('crm_partner_bcs.db')

def get_current_partner():
    if 'user' in st.session_state:
        return st.session_state['user']
    else:
        # Fallback for demo purposes
        return {"id": 999, "name": "Demo Partner", "email": "demo@partner.com"}

def format_currency(amount):
    return f"${amount:,.2f}"

def get_stage_color(stage):
    colors = {
        'discovery': '#059669',
        'demo': '#0891b2', 
        'proposal': '#7c3aed',
        'negotiation': '#dc2626',
        'closed-won': '#16a34a',
        'closed-lost': '#dc2626'
    }
    return colors.get(stage, '#6b7280')

# --- MAIN APP ---
def main():
    init_database()
    
    # Check authentication
    if 'authenticated' not in st.session_state or not st.session_state['authenticated']:
        show_login()
        return
    
    user = st.session_state['user']
    user_type = st.session_state['user_type']
    
    # Header
    if user_type == 'admin':
        show_admin_interface()
    else:
        show_partner_interface()

def show_admin_interface():
    st.markdown("""
    <div class="main-header" style="background: linear-gradient(90deg, #dc2626 0%, #ef4444 100%);">
        <h1>⚙️ Panel de Administración BCS</h1>
        <p>Gestión completa del sistema y partners</p>
    </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state['user']
    
    # Admin Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/dc2626/white?text=ADMIN+BCS", width=200)
        st.markdown(f"**👤 Admin:** {user['name']}")
        st.markdown(f"**📧 Email:** {user['email']}")
        st.markdown("---")
        
        admin_page = st.selectbox(
            "🔧 Panel Admin",
            ["📊 Dashboard General", "👥 Gestión Partners", "📈 Analytics Globales", 
             "💰 Comisiones Globales", "🗄️ Gestión Datos", "⚙️ Configuración Sistema"]
        )
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            logout()
    
    # Admin Page Router
    if admin_page == "📊 Dashboard General":
        show_admin_dashboard()
    elif admin_page == "👥 Gestión Partners":
        show_partners_management()
    elif admin_page == "📈 Analytics Globales":
        show_global_analytics()
    elif admin_page == "💰 Comisiones Globales":
        show_global_commissions()
    elif admin_page == "🗄️ Gestión Datos":
        show_data_management()
    elif admin_page == "⚙️ Configuración Sistema":
        show_system_settings()

def show_partner_interface():
    st.markdown("""
    <div class="main-header">
        <h1>🚀 CRM Partner BCS Blackbox</h1>
        <p>Gestiona tus leads, oportunidades y comisiones de manera profesional</p>
    </div>
    """, unsafe_allow_html=True)
    
    user = st.session_state['user']
    
    # Partner Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1e3a8a/white?text=BCS+CRM", width=200)
        st.markdown(f"**👤 Partner:** {user['name']}")
        st.markdown(f"**📧 Email:** {user['email']}")
        st.markdown(f"**🌍 Región:** {user['region']}")
        st.markdown("---")
        
        page = st.selectbox(
            "📋 Navegación",
            ["📊 Dashboard", "👥 Leads", "💼 Oportunidades", "📝 Actividades", "💰 Comisiones", "⚙️ Configuración"]
        )
        
        st.markdown("---")
        if st.button("🚪 Cerrar Sesión", type="secondary", use_container_width=True):
            logout()
    
    # Partner Page Router
    if page == "📊 Dashboard":
        show_dashboard()
    elif page == "👥 Leads":
        show_leads()
    elif page == "💼 Oportunidades":
        show_opportunities()
    elif page == "📝 Actividades":
        show_activities()
    elif page == "💰 Comisiones":
        show_commissions()
    elif page == "⚙️ Configuración":
        show_settings()

# --- ADMIN FUNCTIONS ---
def show_admin_dashboard():
    st.header("📊 Dashboard General del Sistema")
    
    conn = get_db_connection()
    
    # Métricas globales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_partners = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM partners WHERE status != 'admin'", conn
        )['count'].iloc[0]
        st.metric("👥 Total Partners", total_partners, delta="+2 este mes")
    
    with col2:
        total_leads = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM leads", conn
        )['count'].iloc[0]
        st.metric("📋 Total Leads", total_leads, delta="+15 esta semana")
    
    with col3:
        total_opportunities = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM opportunities WHERE status = 'open'", conn
        )['count'].iloc[0]
        st.metric("💼 Oportunidades Activas", total_opportunities, delta="+8")
    
    with col4:
        total_revenue = pd.read_sql_query(
            "SELECT COALESCE(SUM(monthly_value), 0) as total FROM commissions WHERE status = 'active'", conn
        )['total'].iloc[0]
        st.metric("💰 Revenue Mensual", format_currency(total_revenue), delta="+25%")
    
    st.markdown("---")
    
    # Gráficos de performance
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Partners más Activos")
        top_partners = pd.read_sql_query("""
            SELECT p.name, COUNT(l.id) as leads_count, COUNT(o.id) as opportunities_count
            FROM partners p
            LEFT JOIN leads l ON p.id = l.partner_id
            LEFT JOIN opportunities o ON p.id = o.partner_id
            WHERE p.status != 'admin'
            GROUP BY p.id, p.name
            ORDER BY leads_count DESC
            LIMIT 10
        """, conn)
        
        if not top_partners.empty:
            fig = px.bar(top_partners, x='name', y='leads_count', title="Leads por Partner")
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de partners disponibles")
    
    with col2:
        st.subheader("🏭 Distribución por Industria")
        industry_distribution = pd.read_sql_query("""
            SELECT industry, COUNT(*) as count
            FROM leads
            GROUP BY industry
            ORDER BY count DESC
        """, conn)
        
        if not industry_distribution.empty:
            fig = px.pie(industry_distribution, values='count', names='industry', title="Leads por Industria")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de industrias disponibles")
    
    # Actividad reciente del sistema
    st.subheader("📝 Actividad Reciente del Sistema")
    recent_activities = pd.read_sql_query("""
        SELECT a.*, p.name as partner_name, l.company_name
        FROM activities a
        LEFT JOIN partners p ON a.partner_id = p.id
        LEFT JOIN leads l ON a.lead_id = l.id
        ORDER BY a.created_date DESC
        LIMIT 10
    """, conn)
    
    if not recent_activities.empty:
        st.dataframe(recent_activities[['partner_name', 'activity_type', 'company_name', 'activity_date']], use_container_width=True)
    else:
        st.info("No hay actividades recientes")
    
    conn.close()

def show_partners_management():
    st.header("👥 Gestión de Partners")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista Partners", "➕ Nuevo Partner", "📊 Performance"])
    
    with tab1:
        show_partners_list()
    
    with tab2:
        show_add_partner()
    
    with tab3:
        show_partners_performance()

def show_partners_list():
    st.subheader("📋 Lista de Partners")
    
    conn = get_db_connection()
    partners = pd.read_sql_query("""
        SELECT p.*, 
               COUNT(DISTINCT l.id) as leads_count,
               COUNT(DISTINCT o.id) as opportunities_count,
               COALESCE(SUM(c.commission_amount), 0) as total_commissions
        FROM partners p
        LEFT JOIN leads l ON p.id = l.partner_id
        LEFT JOIN opportunities o ON p.id = o.partner_id
        LEFT JOIN commissions c ON p.id = c.partner_id AND c.status = 'active'
        WHERE p.status != 'admin'
        GROUP BY p.id
        ORDER BY p.created_date DESC
    """, conn)
    
    if not partners.empty:
        for _, partner in partners.iterrows():
            status_color = "🟢" if partner['status'] == 'active' else "🔴"
            
            with st.expander(f"{status_color} {partner['name']} - {partner['email']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**📧 Email:** {partner['email']}")
                    st.write(f"**📱 Teléfono:** {partner['phone']}")
                    st.write(f"**🌍 Región:** {partner['region']}")
                    st.write(f"**🏭 Especialización:** {partner['specialization']}")
                
                with col2:
                    st.write(f"**📊 Estado:** {partner['status']}")
                    st.write(f"**📅 Creado:** {partner['created_date']}")
                    st.write(f"**👥 Leads:** {partner['leads_count']}")
                    st.write(f"**💼 Oportunidades:** {partner['opportunities_count']}")
                
                with col3:
                    st.write(f"**💰 Comisiones Mensuales:** {format_currency(partner['total_commissions'])}")
                    
                    if st.button(f"✏️ Editar", key=f"edit_partner_{partner['id']}"):
                        st.session_state['editing_partner_id'] = partner['id']
                        st.rerun()
                    
                    if partner['status'] == 'active':
                        if st.button(f"⏸️ Suspender", key=f"suspend_{partner['id']}"):
                            update_partner_status(partner['id'], 'suspended')
                            st.success("Partner suspendido")
                            st.rerun()
                    else:
                        if st.button(f"▶️ Activar", key=f"activate_{partner['id']}"):
                            update_partner_status(partner['id'], 'active')
                            st.success("Partner activado")
                            st.rerun()
    else:
        st.info("No hay partners registrados")
    
    # Mostrar formulario de edición si hay un partner seleccionado
    if 'editing_partner_id' in st.session_state:
        show_edit_partner_form(st.session_state['editing_partner_id'])
    
    conn.close()

def show_add_partner():
    st.subheader("➕ Crear Nuevo Partner")
    
    with st.form("add_partner_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nombre Completo *", placeholder="Juan Pérez")
            email = st.text_input("Email *", placeholder="juan@email.com")
            password = st.text_input("Contraseña Temporal *", type="password", placeholder="Contraseña inicial")
            phone = st.text_input("Teléfono", placeholder="+56 9 1234 5678")
        
        with col2:
            region = st.text_input("Región/País", placeholder="Chile, Colombia, México")
            specialization = st.selectbox("Especialización", 
                                        ["Todas las industrias", "Pesca", "Salud", "Restauración", "Retail", "Legal"])
            status = st.selectbox("Estado Inicial", ["active", "pending"])
        
        submitted = st.form_submit_button("💾 Crear Partner", type="primary")
        
        if submitted:
            if name and email and password:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Verificar si el email ya existe
                existing = cursor.execute("SELECT id FROM partners WHERE email = ?", (email,)).fetchone()
                
                if existing:
                    st.error("❌ Este email ya está registrado")
                else:
                    password_hash = hash_password(password)
                    created_date_str = datetime.now().date().strftime('%Y-%m-%d')
                    
                    cursor.execute("""
                        INSERT INTO partners (name, email, password_hash, phone, region, specialization, created_date, status, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, email, password_hash, phone, region, specialization, created_date_str, status, "admin"))
                    
                    conn.commit()
                    st.success(f"✅ Partner '{name}' creado exitosamente!")
                    st.info(f"📧 Credenciales: {email} / {password}")
                
                conn.close()
            else:
                st.error("⚠️ Por favor completa los campos obligatorios")

def show_edit_partner_form(partner_id):
    """Muestra el formulario de edición de partner"""
    st.markdown("---")
    st.subheader("✏️ Editar Partner")
    
    conn = get_db_connection()
    
    # Obtener datos actuales del partner
    partner_data = pd.read_sql_query("SELECT * FROM partners WHERE id = ?", conn, params=[partner_id])
    
    if partner_data.empty:
        st.error("Partner no encontrado")
        del st.session_state['editing_partner_id']
        st.rerun()
        return
    
    partner = partner_data.iloc[0]
    
    with st.form("edit_partner_form"):
        st.info(f"Editando: **{partner['name']}** - {partner['email']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nombre Completo *", value=partner['name'])
            email = st.text_input("Email *", value=partner['email'])
            phone = st.text_input("Teléfono", value=partner['phone'] or "")
            new_password = st.text_input("Nueva Contraseña (dejar vacío para no cambiar)", type="password")
        
        with col2:
            region = st.text_input("Región/País", value=partner['region'] or "")
            specialization = st.selectbox("Especialización", 
                                        ["Todas las industrias", "Pesca", "Salud", "Restauración", "Retail", "Legal"],
                                        index=["Todas las industrias", "Pesca", "Salud", "Restauración", "Retail", "Legal"].index(partner['specialization']) if partner['specialization'] in ["Todas las industrias", "Pesca", "Salud", "Restauración", "Retail", "Legal"] else 0)
            status = st.selectbox("Estado", ["active", "suspended", "pending"],
                                index=["active", "suspended", "pending"].index(partner['status']) if partner['status'] in ["active", "suspended", "pending"] else 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Actualizar Partner", type="primary")
        
        with col2:
            cancelled = st.form_submit_button("❌ Cancelar")
        
        if cancelled:
            del st.session_state['editing_partner_id']
            st.rerun()
        
        if submitted:
            if name and email:
                update_partner(partner_id, name, email, phone, region, specialization, status, new_password)
                st.success(f"✅ Partner '{name}' actualizado exitosamente!")
                del st.session_state['editing_partner_id']
                st.rerun()
            else:
                st.error("⚠️ Por favor completa los campos obligatorios (marcados con *)")
    
    conn.close()

def update_partner(partner_id, name, email, phone, region, specialization, status, new_password=None):
    """Actualiza un partner en la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si el email ya existe para otro partner
        existing = cursor.execute("SELECT id FROM partners WHERE email = ? AND id != ?", (email, partner_id)).fetchone()
        
        if existing:
            st.error("❌ Este email ya está registrado para otro partner")
            return
        
        # Actualizar partner
        if new_password:
            password_hash = hash_password(new_password)
            cursor.execute("""
                UPDATE partners SET
                    name = ?, email = ?, password_hash = ?, phone = ?, 
                    region = ?, specialization = ?, status = ?
                WHERE id = ?
            """, (name, email, password_hash, phone, region, specialization, status, partner_id))
            st.info(f"📧 Nueva contraseña establecida: {new_password}")
        else:
            cursor.execute("""
                UPDATE partners SET
                    name = ?, email = ?, phone = ?, 
                    region = ?, specialization = ?, status = ?
                WHERE id = ?
            """, (name, email, phone, region, specialization, status, partner_id))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        st.error(f"Error al actualizar el partner: {str(e)}")
    finally:
        conn.close()

def show_partners_performance():
    st.subheader("📊 Performance de Partners")
    
    conn = get_db_connection()
    
    # Métricas de performance
    performance_data = pd.read_sql_query("""
        SELECT 
            p.name,
            p.region,
            COUNT(DISTINCT l.id) as total_leads,
            COUNT(DISTINCT CASE WHEN o.stage = 'closed-won' THEN o.id END) as won_deals,
            COUNT(DISTINCT CASE WHEN o.stage = 'closed-lost' THEN o.id END) as lost_deals,
            COALESCE(SUM(CASE WHEN o.stage = 'closed-won' THEN o.total_value END), 0) as total_revenue,
            COALESCE(SUM(c.commission_amount), 0) as monthly_commissions
        FROM partners p
        LEFT JOIN leads l ON p.id = l.partner_id
        LEFT JOIN opportunities o ON p.id = o.partner_id
        LEFT JOIN commissions c ON p.id = c.partner_id AND c.status = 'active'
        WHERE p.status != 'admin'
        GROUP BY p.id
        ORDER BY total_revenue DESC
    """, conn)
    
    if not performance_data.empty:
        # Tabla de performance
        st.dataframe(performance_data, use_container_width=True)
        
        # Gráfico de revenue por partner
        fig = px.bar(performance_data, x='name', y='total_revenue', 
                     title="Revenue Total por Partner", color='region')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de performance disponibles")
    
    conn.close()

def show_global_analytics():
    st.header("📈 Analytics Globales")
    # Implementar analytics globales del sistema
    st.info("Sección de analytics globales en desarrollo")

def show_global_commissions():
    st.header("💰 Gestión Global de Comisiones")
    # Implementar gestión de comisiones globales
    st.info("Sección de comisiones globales en desarrollo")

def show_system_settings():
    st.header("⚙️ Configuración del Sistema")
    # Implementar configuraciones del sistema
    st.info("Configuraciones del sistema en desarrollo")

def update_partner_status(partner_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE partners SET status = ? WHERE id = ?", (new_status, partner_id))
    conn.commit()
    conn.close()

# --- DASHBOARD ---
def show_dashboard():
    st.header("📊 Dashboard de Performance")
    
    partner = get_current_partner()
    conn = get_db_connection()
    
    # KPIs Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        leads_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM leads WHERE partner_id = ?", 
            conn, params=[partner['id']]
        )['count'].iloc[0]
        
        st.metric("👥 Total Leads", leads_count, delta="+5 este mes")
    
    with col2:
        opportunities_count = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM opportunities WHERE partner_id = ? AND status = 'open'", 
            conn, params=[partner['id']]
        )['count'].iloc[0]
        
        st.metric("💼 Oportunidades Abiertas", opportunities_count, delta="+2 esta semana")
    
    with col3:
        pipeline_value = pd.read_sql_query(
            "SELECT COALESCE(SUM(total_value * probability / 100), 0) as value FROM opportunities WHERE partner_id = ? AND status = 'open'", 
            conn, params=[partner['id']]
        )['value'].iloc[0]
        
        st.metric("💵 Pipeline Value", format_currency(pipeline_value), delta="+15%")
    
    with col4:
        monthly_commissions = pd.read_sql_query(
            "SELECT COALESCE(SUM(commission_amount), 0) as total FROM commissions WHERE partner_id = ? AND status = 'active'", 
            conn, params=[partner['id']]
        )['total'].iloc[0]
        
        st.metric("💰 Comisiones Mensuales", format_currency(monthly_commissions), delta="+$1,250")
    
    st.markdown("---")
    
    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Pipeline por Etapa")
        
        pipeline_data = pd.read_sql_query("""
            SELECT stage, COUNT(*) as count, SUM(total_value) as value
            FROM opportunities 
            WHERE partner_id = ? AND status = 'open'
            GROUP BY stage
        """, conn, params=[partner['id']])
        
        if not pipeline_data.empty:
            fig = px.funnel(
                pipeline_data, 
                x='count', 
                y='stage',
                title="Oportunidades por Etapa"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de pipeline disponibles")
    
    with col2:
        st.subheader("📊 Leads por Fuente")
        
        leads_source = pd.read_sql_query("""
            SELECT lead_source, COUNT(*) as count
            FROM leads 
            WHERE partner_id = ?
            GROUP BY lead_source
        """, conn, params=[partner['id']])
        
        if not leads_source.empty:
            fig = px.pie(
                leads_source, 
                values='count', 
                names='lead_source',
                title="Distribución de Fuentes"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay datos de fuentes disponibles")
    
    # Activities Summary
    st.subheader("📝 Actividades Recientes")
    
    recent_activities = pd.read_sql_query("""
        SELECT a.*, l.company_name, o.opportunity_name
        FROM activities a
        LEFT JOIN leads l ON a.lead_id = l.id
        LEFT JOIN opportunities o ON a.opportunity_id = o.id
        WHERE a.partner_id = ?
        ORDER BY a.created_date DESC
        LIMIT 5
    """, conn, params=[partner['id']])
    
    if not recent_activities.empty:
        for _, activity in recent_activities.iterrows():
            with st.expander(f"{activity['activity_type']} - {activity['activity_date']}"):
                st.write(f"**Descripción:** {activity['description']}")
                if activity['company_name']:
                    st.write(f"**Lead:** {activity['company_name']}")
                if activity['opportunity_name']:
                    st.write(f"**Oportunidad:** {activity['opportunity_name']}")
    else:
        st.info("No hay actividades recientes")
    
    conn.close()

# --- LEADS MANAGEMENT ---
def show_leads():
    st.header("👥 Gestión de Leads")
    
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Leads", "➕ Nuevo Lead", "📊 Analytics"])
    
    with tab1:
        show_leads_list()
    
    with tab2:
        show_add_lead()
    
    with tab3:
        show_leads_analytics()

def show_leads_list():
    partner = get_current_partner()
    conn = get_db_connection()
    
    # Filtros
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status_filter = st.selectbox("Estado", ["Todos", "new", "contacted", "qualified", "unqualified"])
    
    with col2:
        industry_filter = st.selectbox("Industria", ["Todas", "Pesca", "Salud", "Restauración", "Retail", "Marketing", "Legal"])
    
    with col3:
        source_filter = st.selectbox("Fuente", ["Todas", "Referido", "Cold Call", "LinkedIn", "Website", "Email", "Otros"])
    
    with col4:
        date_filter = st.date_input("Desde fecha", datetime.now() - timedelta(days=30))
    
    # Query con filtros
    query = """
        SELECT l.*, 
               COUNT(o.id) as opportunities_count,
               COALESCE(SUM(o.total_value), 0) as total_value
        FROM leads l
        LEFT JOIN opportunities o ON l.id = o.lead_id
        WHERE l.partner_id = ?
    """
    params = [partner['id']]
    
    if status_filter != "Todos":
        query += " AND l.status = ?"
        params.append(status_filter)
    
    if industry_filter != "Todas":
        query += " AND l.industry = ?"
        params.append(industry_filter)
    
    if source_filter != "Todas":
        query += " AND l.lead_source = ?"
        params.append(source_filter)
    
    query += " AND l.created_date >= ?"
    params.append(date_filter)
    
    query += " GROUP BY l.id ORDER BY l.created_date DESC"
    
    leads_df = pd.read_sql_query(query, conn, params=params)
    
    if not leads_df.empty:
        # Display leads
        for _, lead in leads_df.iterrows():
            with st.expander(f"🏢 {lead['company_name']} - {lead['contact_name']} ({lead['status']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**📧 Email:** {lead['contact_email']}")
                    st.write(f"**📱 Teléfono:** {lead['contact_phone']}")
                    st.write(f"**🏭 Industria:** {lead['industry']}")
                    st.write(f"**👥 Tamaño:** {lead['company_size']} empleados")
                    st.write(f"**📅 Creado:** {lead['created_date']}")
                
                with col2:
                    st.write(f"**📊 Estado:** {lead['status']}")
                    st.write(f"**📍 Fuente:** {lead['lead_source']}")
                    st.write(f"**💼 Oportunidades:** {lead['opportunities_count']}")
                    st.write(f"**💵 Valor Total:** {format_currency(lead['total_value'])}")
                    st.write(f"**🗒️ Pain Points:** {lead['pain_points'][:100]}...")
                
                # Action buttons
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    if st.button(f"📞 Contactar", key=f"contact_{lead['id']}"):
                        log_activity(partner['id'], lead['id'], None, "call", f"Llamada a {lead['contact_name']}")
                        st.success("Actividad registrada")
                        st.rerun()
                
                with col2:
                    if st.button(f"💼 Crear Oportunidad", key=f"opp_{lead['id']}"):
                        st.session_state['create_opp_lead'] = lead['id']
                        st.rerun()
                
                with col3:
                    new_status = st.selectbox(
                        "Cambiar Estado", 
                        ["new", "contacted", "qualified", "unqualified"],
                        index=["new", "contacted", "qualified", "unqualified"].index(lead['status']),
                        key=f"status_{lead['id']}"
                    )
                    if new_status != lead['status']:
                        update_lead_status(lead['id'], new_status)
                        st.success("Estado actualizado")
                        st.rerun()
                
                with col4:
                    if st.button(f"✏️ Editar", key=f"edit_{lead['id']}"):
                        st.session_state['edit_lead'] = lead['id']
                        st.rerun()
                
                with col5:
                    # Verificar si el lead tiene oportunidades asociadas
                    has_opportunities = lead['opportunities_count'] > 0
                    
                    # Mostrar información sobre oportunidades pero permitir eliminación
                    button_text = f"🗑️ Eliminar" if not has_opportunities else f"🗑️ Eliminar (+{lead['opportunities_count']} opp.)"
                    button_help = None if not has_opportunities else f"También eliminará {lead['opportunities_count']} oportunidad(es) asociada(s)"
                    
                    if st.button(button_text, key=f"delete_{lead['id']}", type="secondary", help=button_help):
                        # Confirmar eliminación con mensaje apropiado
                        if f"confirm_delete_{lead['id']}" not in st.session_state:
                            st.session_state[f"confirm_delete_{lead['id']}"] = True
                            warning_msg = f"⚠️ ¿Estás seguro de eliminar el lead '{lead['company_name']}'?"
                            if has_opportunities:
                                warning_msg += f" Esto también eliminará {lead['opportunities_count']} oportunidad(es) asociada(s)."
                            warning_msg += " Haz clic nuevamente para confirmar."
                            st.warning(warning_msg)
                            st.rerun()
                        else:
                            delete_lead(lead['id'])
                            st.success(f"✅ Lead '{lead['company_name']}' eliminado exitosamente")
                            del st.session_state[f"confirm_delete_{lead['id']}"]
                            st.rerun()
    else:
        st.info("No se encontraron leads con los filtros aplicados")
    
    # Mostrar formulario de edición si hay un lead seleccionado para editar
    if 'edit_lead' in st.session_state:
        show_edit_lead_form(st.session_state['edit_lead'], partner['id'])
    
    conn.close()

def show_add_lead():
    st.subheader("➕ Agregar Nuevo Lead")
    
    with st.form("add_lead_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Nombre de la Empresa *", placeholder="Ej: Pescados del Pacífico SA")
            contact_name = st.text_input("Nombre del Contacto *", placeholder="Ej: Juan Pérez")
            contact_email = st.text_input("Email del Contacto", placeholder="juan.perez@empresa.com")
            contact_phone = st.text_input("Teléfono", placeholder="+56 9 1234 5678")
        
        with col2:
            industry = st.selectbox("Industria *", ["Pesca", "Salud", "Restauración", "Retail", "Marketing", "Legal", "Otros"])
            company_size = st.number_input("Número de Empleados", min_value=1, max_value=10000, value=10)
            lead_source = st.selectbox("Fuente del Lead", ["Referido", "Cold Call", "LinkedIn", "Website", "Email", "Otros"])
            status = st.selectbox("Estado Inicial", ["new", "contacted"], index=0)
        
        pain_points = st.text_area("Pain Points / Problemas Identificados", 
                                  placeholder="Describe los principales problemas o necesidades del cliente...")
        
        notes = st.text_area("Notas Adicionales", 
                            placeholder="Información adicional sobre el lead...")
        
        submitted = st.form_submit_button("💾 Guardar Lead", type="primary")
        
        if submitted:
            if company_name and contact_name:
                partner = get_current_partner()
                
                conn = get_db_connection()
                cursor = conn.cursor()
                
                created_date_str = datetime.now().date().strftime('%Y-%m-%d')
                activity_date_str = datetime.now().date().strftime('%Y-%m-%d')
                created_datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                cursor.execute("""
                    INSERT INTO leads (
                        partner_id, company_name, contact_name, contact_email, 
                        contact_phone, industry, company_size, pain_points,
                        lead_source, status, created_date, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    partner['id'], company_name, contact_name, contact_email,
                    contact_phone, industry, company_size, pain_points,
                    lead_source, status, created_date_str, notes
                ))
                
                lead_id = cursor.lastrowid
                
                # Log activity
                cursor.execute("""
                    INSERT INTO activities (
                        lead_id, partner_id, activity_type, description, 
                        activity_date, created_date
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    lead_id, partner['id'], "lead_created", 
                    f"Lead creado para {company_name}", 
                    activity_date_str, created_datetime_str
                ))
                
                conn.commit()
                conn.close()
                
                st.success(f"✅ Lead '{company_name}' creado exitosamente!")
                st.balloons()
            else:
                st.error("⚠️ Por favor completa los campos obligatorios (marcados con *)")

def show_edit_lead_form(lead_id, partner_id):
    """Muestra el formulario de edición de lead en un modal"""
    st.markdown("---")
    st.subheader("✏️ Editar Lead")
    
    # Obtener datos actuales del lead
    conn = get_db_connection()
    lead_data = pd.read_sql_query(
        "SELECT * FROM leads WHERE id = ? AND partner_id = ?", 
        conn, params=[lead_id, partner_id]
    )
    
    if lead_data.empty:
        st.error("Lead no encontrado")
        del st.session_state['edit_lead']
        st.rerun()
        return
    
    lead = lead_data.iloc[0]
    
    with st.form("edit_lead_form"):
        st.info(f"Editando: **{lead['company_name']}** - {lead['contact_name']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Nombre de la Empresa *", value=lead['company_name'])
            contact_name = st.text_input("Nombre del Contacto *", value=lead['contact_name'])
            contact_email = st.text_input("Email del Contacto", value=lead['contact_email'] or "")
            contact_phone = st.text_input("Teléfono", value=lead['contact_phone'] or "")
        
        with col2:
            industry = st.selectbox(
                "Industria *", 
                ["Pesca", "Salud", "Restauración", "Retail", "Marketing", "Legal", "Otros"],
                index=["Pesca", "Salud", "Restauración", "Retail", "Marketing", "Legal", "Otros"].index(lead['industry']) if lead['industry'] in ["Pesca", "Salud", "Restauración", "Retail", "Marketing", "Legal", "Otros"] else 0
            )
            company_size = st.number_input("Número de Empleados", min_value=1, max_value=10000, value=int(lead['company_size']) if lead['company_size'] else 10)
            lead_source = st.selectbox(
                "Fuente del Lead", 
                ["Referido", "Cold Call", "LinkedIn", "Website", "Email", "Otros"],
                index=["Referido", "Cold Call", "LinkedIn", "Website", "Email", "Otros"].index(lead['lead_source']) if lead['lead_source'] in ["Referido", "Cold Call", "LinkedIn", "Website", "Email", "Otros"] else 0
            )
            status = st.selectbox(
                "Estado", 
                ["new", "contacted", "qualified", "unqualified"],
                index=["new", "contacted", "qualified", "unqualified"].index(lead['status'])
            )
        
        pain_points = st.text_area(
            "Pain Points / Problemas Identificados", 
            value=lead['pain_points'] or "",
            placeholder="Describe los principales problemas o necesidades del cliente...",
            height=100
        )
        
        notes = st.text_area(
            "Notas Adicionales", 
            value=lead['notes'] or "",
            placeholder="Información adicional sobre el lead...",
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Actualizar Lead", type="primary")
        
        with col2:
            cancelled = st.form_submit_button("❌ Cancelar")
        
        if cancelled:
            del st.session_state['edit_lead']
            st.rerun()
        
        if submitted:
            if company_name and contact_name:
                update_lead(
                    lead_id, company_name, contact_name, contact_email, contact_phone,
                    industry, company_size, lead_source, status, pain_points, notes, partner_id
                )
                st.success(f"✅ Lead '{company_name}' actualizado exitosamente!")
                del st.session_state['edit_lead']
                st.rerun()
            else:
                st.error("⚠️ Por favor completa los campos obligatorios (marcados con *)")
    
    conn.close()

def update_lead(lead_id, company_name, contact_name, contact_email, contact_phone, 
                industry, company_size, lead_source, status, pain_points, notes, partner_id):
    """Actualiza un lead en la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE leads SET
                company_name = ?, contact_name = ?, contact_email = ?, contact_phone = ?,
                industry = ?, company_size = ?, lead_source = ?, status = ?,
                pain_points = ?, notes = ?
            WHERE id = ?
        """, (
            company_name, contact_name, contact_email, contact_phone,
            industry, company_size, lead_source, status,
            pain_points, notes, lead_id
        ))
        
        # Registrar actividad de edición
        activity_date_str = datetime.now().date().strftime('%Y-%m-%d')
        created_datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            INSERT INTO activities (
                lead_id, partner_id, activity_type, description, 
                activity_date, created_date
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            lead_id, partner_id, "lead_updated", 
            f"Lead actualizado: {company_name}", 
            activity_date_str, created_datetime_str
        ))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        st.error(f"Error al actualizar el lead: {str(e)}")
    finally:
        conn.close()

def show_leads_analytics():
    st.subheader("📊 Analytics de Leads")
    
    partner = get_current_partner()
    conn = get_db_connection()
    
    # Métricas de conversión
    col1, col2, col3 = st.columns(3)
    
    with col1:
        conversion_rate = pd.read_sql_query("""
            SELECT 
                COUNT(CASE WHEN status = 'qualified' THEN 1 END) * 100.0 / COUNT(*) as rate
            FROM leads WHERE partner_id = ?
        """, conn, params=[partner['id']])['rate'].iloc[0] or 0
        
        st.metric("📈 Tasa de Calificación", f"{conversion_rate:.1f}%")
    
    with col2:
        avg_time_to_contact = pd.read_sql_query("""
            SELECT AVG(julianday(last_contact) - julianday(created_date)) as avg_days
            FROM leads 
            WHERE partner_id = ? AND last_contact IS NOT NULL
        """, conn, params=[partner['id']])['avg_days'].iloc[0] or 0
        
        st.metric("⏱️ Tiempo Promedio a Contacto", f"{avg_time_to_contact:.1f} días")
    
    with col3:
        leads_this_month = pd.read_sql_query("""
            SELECT COUNT(*) as count
            FROM leads 
            WHERE partner_id = ? 
            AND created_date >= date('now', 'start of month')
        """, conn, params=[partner['id']])['count'].iloc[0]
        
        st.metric("📅 Leads Este Mes", leads_this_month)
    
    # Gráfico de tendencia
    st.subheader("📈 Tendencia de Leads")
    
    leads_trend = pd.read_sql_query("""
        SELECT 
            date(created_date) as date,
            COUNT(*) as leads_count
        FROM leads 
        WHERE partner_id = ?
        AND created_date >= date('now', '-30 days')
        GROUP BY date(created_date)
        ORDER BY date
    """, conn, params=[partner['id']])
    
    if not leads_trend.empty:
        fig = px.line(leads_trend, x='date', y='leads_count', title="Leads Creados por Día (Últimos 30 días)")
        st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

# --- OPPORTUNITIES MANAGEMENT ---
def show_opportunities():
    st.header("💼 Gestión de Oportunidades")
    
    tab1, tab2, tab3 = st.tabs(["📋 Pipeline", "➕ Nueva Oportunidad", "📊 Analytics"])
    
    with tab1:
        show_opportunities_pipeline()
    
    with tab2:
        show_add_opportunity()
    
    with tab3:
        show_opportunities_analytics()

def show_opportunities_pipeline():
    partner = get_current_partner()
    conn = get_db_connection()
    
    # Stage columns
    stages = ['discovery', 'demo', 'proposal', 'negotiation', 'closed-won', 'closed-lost']
    stage_names = ['🔍 Discovery', '🎯 Demo', '📋 Propuesta', '🤝 Negociación', '✅ Ganada', '❌ Perdida']
    
    opportunities = pd.read_sql_query("""
        SELECT o.*, l.company_name, l.contact_name
        FROM opportunities o
        LEFT JOIN leads l ON o.lead_id = l.id
        WHERE o.partner_id = ?
        ORDER BY o.created_date DESC
    """, conn, params=[partner['id']])
    
    cols = st.columns(len(stages))
    
    for i, (stage, stage_name) in enumerate(zip(stages, stage_names)):
        with cols[i]:
            st.markdown(f"### {stage_name}")
            
            stage_opps = opportunities[opportunities['stage'] == stage]
            stage_value = stage_opps['total_value'].sum()
            
            st.markdown(f"**💵 Valor:** {format_currency(stage_value)}")
            st.markdown(f"**📊 Cantidad:** {len(stage_opps)}")
            st.markdown("---")
            
            for _, opp in stage_opps.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin-bottom: 8px; background-color: white;">
                        <strong>{opp['opportunity_name']}</strong><br>
                        <small>🏢 {opp['company_name']}</small><br>
                        <small>💰 {format_currency(opp['total_value'])}</small><br>
                        <small>📊 {opp['probability']}% prob.</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button(f"📋 Detalles", key=f"view_opp_{opp['id']}"):
                            st.session_state['show_details'] = opp['id']
                            st.rerun()
                    
                    with col2:
                        if st.button(f"✏️ Editar", key=f"edit_opp_{opp['id']}"):
                            st.session_state['edit_opportunity'] = opp['id']
                            st.rerun()
                    
                    with col3:
                        if st.button(f"🗑️ Eliminar", key=f"delete_opp_{opp['id']}", type="secondary"):
                            # Confirmar eliminación
                            if f"confirm_delete_opp_{opp['id']}" not in st.session_state:
                                st.session_state[f"confirm_delete_opp_{opp['id']}"] = True
                                st.warning(f"⚠️ ¿Estás seguro de eliminar la oportunidad '{opp['opportunity_name']}'? Haz clic nuevamente para confirmar.")
                                st.rerun()
                            else:
                                delete_opportunity(opp['id'])
                                st.success(f"✅ Oportunidad '{opp['opportunity_name']}' eliminada exitosamente")
                                del st.session_state[f"confirm_delete_opp_{opp['id']}"]
                                st.rerun()
    
    # Mostrar detalles si hay una oportunidad seleccionada
    if 'show_details' in st.session_state:
        show_opportunity_details(st.session_state['show_details'])
    
    # Mostrar formulario de edición si hay una oportunidad seleccionada para editar
    if 'edit_opportunity' in st.session_state:
        show_edit_opportunity_form(st.session_state['edit_opportunity'])
    
    conn.close()

def show_add_opportunity():
    st.subheader("➕ Nueva Oportunidad")
    
    partner = get_current_partner()
    conn = get_db_connection()
    
    # Get leads for selection
    leads = pd.read_sql_query("""
        SELECT id, company_name, contact_name
        FROM leads 
        WHERE partner_id = ? AND status IN ('qualified', 'contacted')
    """, conn, params=[partner['id']])
    
    if leads.empty:
        st.warning("⚠️ No tienes leads calificados. Primero crea y califica algunos leads.")
        return
    
    with st.form("add_opportunity_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            lead_options = [f"{row['company_name']} - {row['contact_name']}" for _, row in leads.iterrows()]
            selected_lead_idx = st.selectbox("Seleccionar Lead *", range(len(lead_options)), format_func=lambda x: lead_options[x])
            selected_lead = leads.iloc[selected_lead_idx]
            
            opportunity_name = st.text_input("Nombre de la Oportunidad *", 
                                           value=f"{selected_lead['company_name']} - BCS Implementation")
            
            bcs_solutions = [
                "FleetCore - Pesca & Flotas",
                "MedCare Pro - Hospitales & Clínicas", 
                "SmartChef - Restaurantes & Delivery",
                "PetCore - Veterinarias",
                "TravelCore - Hoteles & Turismo",
                "LawFlow - Bufetes Legales",
                "RetailFlow - Comercio & Retail",
                "Consultix - Consultoras"
            ]
            bcs_solution = st.selectbox("Solución BCS *", bcs_solutions)
            
            estimated_users = st.number_input("Usuarios Estimados *", min_value=1, max_value=1000, value=10)
        
        with col2:
            price_per_user = st.number_input("Precio por Usuario (USD/mes) *", min_value=50.0, max_value=200.0, value=100.0, step=10.0)
            
            total_value = estimated_users * price_per_user * 12  # Annual value
            st.metric("💵 Valor Anual Total", format_currency(total_value))
            
            probability = st.slider("Probabilidad de Cierre (%)", 0, 100, 25)
            
            stage = st.selectbox("Etapa Inicial", ['discovery', 'demo', 'proposal', 'negotiation'])
            
            expected_close_date = st.date_input("Fecha Esperada de Cierre", 
                                              value=datetime.now() + timedelta(days=30))
        
        notes = st.text_area("Notas de la Oportunidad", 
                            placeholder="Detalles sobre la oportunidad, próximos pasos, etc.")
        
        submitted = st.form_submit_button("💾 Crear Oportunidad", type="primary")
        
        if submitted:
            cursor = conn.cursor()
            
            # Convertir fechas a strings
            created_date_str = datetime.now().date().strftime('%Y-%m-%d')
            expected_close_str = expected_close_date.strftime('%Y-%m-%d')
            activity_date_str = datetime.now().date().strftime('%Y-%m-%d')
            created_datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("""
                INSERT INTO opportunities (
                    lead_id, partner_id, opportunity_name, bcs_solution,
                    estimated_users, price_per_user, total_value, probability,
                    stage, expected_close_date, status, notes, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                selected_lead['id'], partner['id'], opportunity_name, bcs_solution,
                estimated_users, price_per_user, total_value, probability,
                stage, expected_close_str, 'open', notes, created_date_str
            ))
            
            opp_id = cursor.lastrowid
            
            # Log activity
            cursor.execute("""
                INSERT INTO activities (
                    lead_id, opportunity_id, partner_id, activity_type, description,
                    activity_date, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                selected_lead['id'], opp_id, partner['id'], "opportunity_created",
                f"Oportunidad creada: {opportunity_name}",
                activity_date_str, created_datetime_str
            ))
            
            conn.commit()
            st.success(f"✅ Oportunidad '{opportunity_name}' creada exitosamente!")
            st.balloons()
    
    conn.close()

def show_opportunities_analytics():
    st.subheader("📊 Analytics de Oportunidades")
    
    partner = get_current_partner()
    conn = get_db_connection()
    
    # Métricas clave
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pipeline = pd.read_sql_query("""
            SELECT COALESCE(SUM(total_value), 0) as total
            FROM opportunities 
            WHERE partner_id = ? AND status = 'open'
        """, conn, params=[partner['id']])['total'].iloc[0]
        
        st.metric("💼 Pipeline Total", format_currency(total_pipeline))
    
    with col2:
        weighted_pipeline = pd.read_sql_query("""
            SELECT COALESCE(SUM(total_value * probability / 100), 0) as weighted
            FROM opportunities 
            WHERE partner_id = ? AND status = 'open'
        """, conn, params=[partner['id']])['weighted'].iloc[0]
        
        st.metric("⚖️ Pipeline Ponderado", format_currency(weighted_pipeline))
    
    with col3:
        win_rate = pd.read_sql_query("""
            SELECT 
                COUNT(CASE WHEN stage = 'closed-won' THEN 1 END) * 100.0 / 
                NULLIF(COUNT(CASE WHEN stage IN ('closed-won', 'closed-lost') THEN 1 END), 0) as rate
            FROM opportunities WHERE partner_id = ?
        """, conn, params=[partner['id']])['rate'].iloc[0] or 0
        
        st.metric("🎯 Tasa de Cierre", f"{win_rate:.1f}%")
    
    with col4:
        avg_deal_size = pd.read_sql_query("""
            SELECT COALESCE(AVG(total_value), 0) as avg_size
            FROM opportunities 
            WHERE partner_id = ? AND stage = 'closed-won'
        """, conn, params=[partner['id']])['avg_size'].iloc[0]
        
        st.metric("💰 Deal Promedio", format_currency(avg_deal_size))
    
    # Pipeline por solución
    st.subheader("📊 Pipeline por Solución BCS")
    
    pipeline_by_solution = pd.read_sql_query("""
        SELECT 
            bcs_solution,
            COUNT(*) as count,
            SUM(total_value) as total_value,
            AVG(probability) as avg_probability
        FROM opportunities 
        WHERE partner_id = ? AND status = 'open'
        GROUP BY bcs_solution
        ORDER BY total_value DESC
    """, conn, params=[partner['id']])
    
    if not pipeline_by_solution.empty:
        fig = px.bar(
            pipeline_by_solution, 
            x='bcs_solution', 
            y='total_value',
            title="Valor de Pipeline por Solución BCS"
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    conn.close()

# --- ACTIVITIES MANAGEMENT ---
def show_activities():
    st.header("📝 Gestión de Actividades")
    
    tab1, tab2 = st.tabs(["📋 Lista de Actividades", "➕ Nueva Actividad"])
    
    with tab1:
        show_activities_list()
    
    with tab2:
        show_add_activity()

def show_activities_list():
    partner = get_current_partner()
    conn = get_db_connection()
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    
    with col1:
        activity_filter = st.selectbox("Tipo", ["Todas", "call", "email", "demo", "meeting", "follow_up", "proposal"])
    
    with col2:
        status_filter = st.selectbox("Estado", ["Todas", "Pendientes", "Completadas"])
    
    with col3:
        date_filter = st.date_input("Desde fecha", datetime.now() - timedelta(days=7))
    
    # Query activities
    query = """
        SELECT a.*, l.company_name, o.opportunity_name
        FROM activities a
        LEFT JOIN leads l ON a.lead_id = l.id
        LEFT JOIN opportunities o ON a.opportunity_id = o.id
        WHERE a.partner_id = ?
    """
    params = [partner['id']]
    
    if activity_filter != "Todas":
        query += " AND a.activity_type = ?"
        params.append(activity_filter)
    
    if status_filter == "Pendientes":
        query += " AND a.completed = 0"
    elif status_filter == "Completadas":
        query += " AND a.completed = 1"
    
    query += " AND a.activity_date >= ? ORDER BY a.activity_date DESC"
    params.append(date_filter)
    
    activities = pd.read_sql_query(query, conn, params=params)
    
    if not activities.empty:
        for _, activity in activities.iterrows():
            status_icon = "✅" if activity['completed'] else "⏳"
            
            with st.expander(f"{status_icon} {activity['activity_type']} - {activity['activity_date']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Descripción:** {activity['description']}")
                    if activity['company_name']:
                        st.write(f"**Lead:** {activity['company_name']}")
                    if activity['opportunity_name']:
                        st.write(f"**Oportunidad:** {activity['opportunity_name']}")
                
                with col2:
                    st.write(f"**Fecha:** {activity['activity_date']}")
                    if activity['follow_up_date']:
                        st.write(f"**Seguimiento:** {activity['follow_up_date']}")
                    st.write(f"**Estado:** {'Completada' if activity['completed'] else 'Pendiente'}")
                
                if not activity['completed']:
                    if st.button(f"Marcar como Completada", key=f"complete_{activity['id']}"):
                        update_activity_status(activity['id'], True)
                        st.success("Actividad marcada como completada")
                        st.rerun()
    else:
        st.info("No hay actividades con los filtros aplicados")
    
    conn.close()

def show_add_activity():
    st.subheader("➕ Nueva Actividad")
    
    partner = get_current_partner()
    conn = get_db_connection()
    
    # Get leads and opportunities
    leads = pd.read_sql_query("SELECT id, company_name FROM leads WHERE partner_id = ?", conn, params=[partner['id']])
    opportunities = pd.read_sql_query("SELECT id, opportunity_name FROM opportunities WHERE partner_id = ?", conn, params=[partner['id']])
    
    with st.form("add_activity_form"):
        activity_type = st.selectbox("Tipo de Actividad", ["call", "email", "demo", "meeting", "follow_up", "proposal", "other"])
        
        col1, col2 = st.columns(2)
        
        with col1:
            if not leads.empty:
                lead_options = ["Ninguno"] + [f"{row['company_name']}" for _, row in leads.iterrows()]
                selected_lead_idx = st.selectbox("Lead Relacionado", range(len(lead_options)), format_func=lambda x: lead_options[x])
                selected_lead_id = None if selected_lead_idx == 0 else leads.iloc[selected_lead_idx - 1]['id']
            else:
                st.info("No hay leads disponibles")
                selected_lead_id = None
        
        with col2:
            if not opportunities.empty:
                opp_options = ["Ninguna"] + [f"{row['opportunity_name']}" for _, row in opportunities.iterrows()]
                selected_opp_idx = st.selectbox("Oportunidad Relacionada", range(len(opp_options)), format_func=lambda x: opp_options[x])
                selected_opp_id = None if selected_opp_idx == 0 else opportunities.iloc[selected_opp_idx - 1]['id']
            else:
                st.info("No hay oportunidades disponibles")
                selected_opp_id = None
        
        description = st.text_area("Descripción de la Actividad", placeholder="Describe la actividad realizada o planificada...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            activity_date = st.date_input("Fecha de la Actividad", value=datetime.now().date())
        
        with col2:
            follow_up_date = st.date_input("Fecha de Seguimiento (opcional)", value=None)
        
        submitted = st.form_submit_button("💾 Guardar Actividad", type="primary")
        
        if submitted and description:
            log_activity(
                partner['id'], 
                selected_lead_id, 
                selected_opp_id, 
                activity_type, 
                description,
                activity_date,
                follow_up_date
            )
            st.success("✅ Actividad registrada exitosamente!")
    
    conn.close()

# --- COMMISSIONS MANAGEMENT ---
def show_commissions():
    st.header("💰 Gestión de Comisiones")
    
    tab1, tab2 = st.tabs(["📊 Dashboard de Comisiones", "📋 Historial"])
    
    with tab1:
        show_commissions_dashboard()
    
    with tab2:
        show_commissions_history()

def show_commissions_dashboard():
    partner = get_current_partner()
    conn = get_db_connection()
    
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        monthly_recurring = pd.read_sql_query("""
            SELECT COALESCE(SUM(commission_amount), 0) as total
            FROM commissions 
            WHERE partner_id = ? AND status = 'active'
        """, conn, params=[partner['id']])['total'].iloc[0]
        
        st.metric("💰 MRR (Monthly Recurring Revenue)", format_currency(monthly_recurring))
    
    with col2:
        this_year_total = pd.read_sql_query("""
            SELECT COALESCE(SUM(commission_amount), 0) as total
            FROM commissions 
            WHERE partner_id = ? 
            AND strftime('%Y', start_date) = strftime('%Y', 'now')
            AND status = 'active'
        """, conn, params=[partner['id']])['total'].iloc[0] * 12  # Proyección anual
        
        st.metric("📅 Proyección Anual", format_currency(this_year_total))
    
    with col3:
        active_clients = pd.read_sql_query("""
            SELECT COUNT(DISTINCT client_name) as count
            FROM commissions 
            WHERE partner_id = ? AND status = 'active'
        """, conn, params=[partner['id']])['count'].iloc[0]
        
        st.metric("👥 Clientes Activos", active_clients)
    
    with col4:
        avg_commission = monthly_recurring / active_clients if active_clients > 0 else 0
        st.metric("📊 Comisión Promedio/Cliente", format_currency(avg_commission))
    
    # Gráfico de tendencia
    st.subheader("📈 Evolución de Comisiones")
    
    commissions_trend = pd.read_sql_query("""
        SELECT 
            strftime('%Y-%m', start_date) as month,
            SUM(commission_amount) as total_commission
        FROM commissions 
        WHERE partner_id = ? 
        AND start_date >= date('now', '-12 months')
        GROUP BY strftime('%Y-%m', start_date)
        ORDER BY month
    """, conn, params=[partner['id']])
    
    if not commissions_trend.empty:
        fig = px.line(
            commissions_trend, 
            x='month', 
            y='total_commission',
            title="Evolución Mensual de Comisiones (Últimos 12 meses)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top clientes por comisión
    st.subheader("🏆 Top Clientes por Comisión")
    
    top_clients = pd.read_sql_query("""
        SELECT 
            client_name,
            commission_amount,
            start_date,
            status
        FROM commissions 
        WHERE partner_id = ?
        ORDER BY commission_amount DESC
        LIMIT 10
    """, conn, params=[partner['id']])
    
    if not top_clients.empty:
        st.dataframe(top_clients, use_container_width=True)
    else:
        st.info("Aún no tienes comisiones registradas")
    
    conn.close()

def show_commissions_history():
    partner = get_current_partner()
    conn = get_db_connection()
    
    commissions = pd.read_sql_query("""
        SELECT c.*, o.opportunity_name
        FROM commissions c
        LEFT JOIN opportunities o ON c.opportunity_id = o.id
        WHERE c.partner_id = ?
        ORDER BY c.start_date DESC
    """, conn, params=[partner['id']])
    
    if not commissions.empty:
        for _, comm in commissions.iterrows():
            status_color = "🟢" if comm['status'] == 'active' else "🔴"
            
            with st.expander(f"{status_color} {comm['client_name']} - {format_currency(comm['commission_amount'])}/mes"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Cliente:** {comm['client_name']}")
                    st.write(f"**Oportunidad:** {comm['opportunity_name']}")
                    st.write(f"**Valor Mensual:** {format_currency(comm['monthly_value'])}")
                    st.write(f"**Tasa de Comisión:** {comm['commission_rate'] * 100}%")
                
                with col2:
                    st.write(f"**Comisión Mensual:** {format_currency(comm['commission_amount'])}")
                    st.write(f"**Fecha Inicio:** {comm['start_date']}")
                    st.write(f"**Estado:** {comm['status']}")
                    if comm['payment_date']:
                        st.write(f"**Último Pago:** {comm['payment_date']}")
                
                if comm['notes']:
                    st.write(f"**Notas:** {comm['notes']}")
    else:
        st.info("No hay comisiones registradas")
        st.markdown("""
        ### ¿Cómo generar comisiones?
        1. 🎯 Crear leads calificados
        2. 💼 Convertir leads en oportunidades
        3. 🤝 Cerrar oportunidades como "ganadas"
        4. 💰 Las comisiones se generan automáticamente
        """)
    
    conn.close()

# --- SETTINGS ---
def show_settings():
    st.header("⚙️ Configuración")
    
    tab1, tab2, tab3 = st.tabs(["👤 Perfil", "🔧 Preferencias", "📊 Datos"])
    
    with tab1:
        show_profile_settings()
    
    with tab2:
        show_app_preferences()
    
    with tab3:
        show_data_management()

def show_profile_settings():
    st.subheader("👤 Información del Partner")
    
    partner = get_current_partner()
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nombre Completo", value=partner['name'])
            email = st.text_input("Email", value=partner['email'])
            phone = st.text_input("Teléfono", value="")
        
        with col2:
            region = st.text_input("Región/País", value="")
            specialization = st.selectbox("Especialización", 
                                        ["Todas las industrias", "Pesca", "Salud", "Restauración", "Retail", "Legal"])
            timezone = st.selectbox("Zona Horaria", ["UTC-3 (Chile)", "UTC-5 (Colombia)", "UTC-6 (México)"])
        
        bio = st.text_area("Bio/Experiencia", placeholder="Describe tu experiencia y fortalezas como partner...")
        
        if st.form_submit_button("💾 Actualizar Perfil"):
            st.success("✅ Perfil actualizado exitosamente!")

def show_app_preferences():
    st.subheader("🔧 Preferencias de la Aplicación")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Notificaciones:**")
        email_notifications = st.checkbox("Notificaciones por email", value=True)
        lead_alerts = st.checkbox("Alertas de nuevos leads", value=True)
        follow_up_reminders = st.checkbox("Recordatorios de seguimiento", value=True)
    
    with col2:
        st.write("**Visualización:**")
        currency = st.selectbox("Moneda", ["USD", "CLP", "EUR", "MXN"])
        date_format = st.selectbox("Formato de fecha", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"])
        theme = st.selectbox("Tema", ["Claro", "Oscuro", "Automático"])
    
    if st.button("💾 Guardar Preferencias"):
        st.success("✅ Preferencias guardadas!")

def show_data_management():
    st.subheader("📊 Gestión de Datos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Exportar Datos:**")
        if st.button("📥 Exportar Leads"):
            # Implementation for exporting leads
            st.info("Exportando leads... (funcionalidad en desarrollo)")
        
        if st.button("📥 Exportar Oportunidades"):
            st.info("Exportando oportunidades... (funcionalidad en desarrollo)")
        
        if st.button("📥 Exportar Comisiones"):
            st.info("Exportando comisiones... (funcionalidad en desarrollo)")
    
    with col2:
        st.write("**Importar Datos:**")
        uploaded_file = st.file_uploader("Subir archivo CSV", type=['csv'])
        
        if uploaded_file:
            st.info("Archivo subido. Funcionalidad de importación en desarrollo.")
        
        st.write("**⚠️ Zona de Peligro:**")
        if st.button("🗑️ Limpiar Datos de Prueba", type="secondary"):
            if st.checkbox("Confirmo que quiero eliminar datos de prueba"):
                st.warning("Esta acción eliminará todos los datos de prueba.")

# --- UTILITY FUNCTIONS ---
def log_activity(partner_id, lead_id, opportunity_id, activity_type, description, activity_date=None, follow_up_date=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convertir fechas a strings para evitar el warning de SQLite
    activity_date_str = (activity_date or datetime.now().date()).strftime('%Y-%m-%d')
    follow_up_date_str = follow_up_date.strftime('%Y-%m-%d') if follow_up_date else None
    created_date_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        INSERT INTO activities (
            lead_id, opportunity_id, partner_id, activity_type, description,
            activity_date, follow_up_date, created_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        lead_id, opportunity_id, partner_id, activity_type, description,
        activity_date_str, follow_up_date_str, created_date_str
    ))
    
    conn.commit()
    conn.close()

def update_lead_status(lead_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convertir fecha a string para evitar el warning de SQLite
    last_contact_str = datetime.now().date().strftime('%Y-%m-%d')
    
    cursor.execute("""
        UPDATE leads 
        SET status = ?, last_contact = ?
        WHERE id = ?
    """, (new_status, last_contact_str, lead_id))
    
    conn.commit()
    conn.close()

def update_activity_status(activity_id, completed):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE activities 
        SET completed = ?
        WHERE id = ?
    """, (completed, activity_id))
    
    conn.commit()
    conn.close()

def show_opportunity_details(opp_id):
    conn = get_db_connection()
    
    opp_details = pd.read_sql_query("""
        SELECT o.*, l.company_name, l.contact_name, l.contact_email
        FROM opportunities o
        LEFT JOIN leads l ON o.lead_id = l.id
        WHERE o.id = ?
    """, conn, params=[opp_id])
    
    if not opp_details.empty:
        opp = opp_details.iloc[0]
        
        with st.container():
            st.markdown("---")
            st.subheader("📋 Detalles de la Oportunidad")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Oportunidad:** {opp['opportunity_name']}")
                st.write(f"**Cliente:** {opp['company_name']}")
                st.write(f"**Contacto:** {opp['contact_name']}")
                st.write(f"**Solución:** {opp['bcs_solution']}")
            
            with col2:
                st.write(f"**Valor Total:** {format_currency(opp['total_value'])}")
                st.write(f"**Etapa:** {opp['stage']}")
                st.write(f"**Probabilidad:** {opp['probability']}%")
            
            if opp['notes']:
                st.write(f"**Notas:** {opp['notes']}")
            
            if st.button("❌ Cerrar Detalles", key="close_details"):
                if 'show_details' in st.session_state:
                    del st.session_state['show_details']
                st.rerun()
            
            st.markdown("---")
    
    conn.close()

def delete_opportunity(opp_id):
    """Elimina una oportunidad y todas sus actividades asociadas"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener nombre de la oportunidad para logging
        opp_name = cursor.execute("SELECT opportunity_name FROM opportunities WHERE id = ?", (opp_id,)).fetchone()
        
        # 1. Eliminar actividades asociadas a la oportunidad
        cursor.execute("DELETE FROM activities WHERE opportunity_id = ?", (opp_id,))
        
        # 2. Eliminar la oportunidad
        cursor.execute("DELETE FROM opportunities WHERE id = ?", (opp_id,))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        st.error(f"Error al eliminar la oportunidad: {str(e)}")
    finally:
        conn.close()

def show_edit_opportunity_form(opp_id):
    """Muestra el formulario de edición de oportunidad"""
    st.markdown("---")
    st.subheader("✏️ Editar Oportunidad")
    
    partner = get_current_partner()
    conn = get_db_connection()
    
    # Obtener datos actuales de la oportunidad
    opp_data = pd.read_sql_query("""
        SELECT o.*, l.company_name, l.contact_name 
        FROM opportunities o
        JOIN leads l ON o.lead_id = l.id
        WHERE o.id = ?
    """, conn, params=[opp_id])
    
    if opp_data.empty:
        st.error("Oportunidad no encontrada")
        del st.session_state['edit_opportunity']
        st.rerun()
        return
    
    opp = opp_data.iloc[0]
    
    # Obtener leads disponibles
    leads = pd.read_sql_query("""
        SELECT id, company_name, contact_name
        FROM leads 
        WHERE partner_id = ? AND (status IN ('qualified', 'contacted') OR id = ?)
    """, conn, params=[partner['id'], opp['lead_id']])
    
    with st.form("edit_opportunity_form"):
        st.info(f"Editando: **{opp['opportunity_name']}** - {opp['company_name']}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            opportunity_name = st.text_input("Nombre de la Oportunidad *", value=opp['opportunity_name'])
            
            # Lead selection
            lead_options = {f"{lead['company_name']} - {lead['contact_name']}": lead['id'] for _, lead in leads.iterrows()}
            current_lead_key = f"{opp['company_name']} - {opp['contact_name']}"
            lead_index = list(lead_options.keys()).index(current_lead_key) if current_lead_key in lead_options else 0
            
            selected_lead = st.selectbox("Cliente Asociado *", options=list(lead_options.keys()), index=lead_index)
            lead_id = lead_options[selected_lead]
            
            bcs_solution = st.selectbox(
                "Solución BCS *", 
                ["Procesamiento de Datos", "Análisis Predictivo", "Automatización", "IA/ML", "Consultoría", "Otros"],
                index=["Procesamiento de Datos", "Análisis Predictivo", "Automatización", "IA/ML", "Consultoría", "Otros"].index(opp['bcs_solution']) if opp['bcs_solution'] in ["Procesamiento de Datos", "Análisis Predictivo", "Automatización", "IA/ML", "Consultoría", "Otros"] else 0
            )
            
            total_value = st.number_input("Valor Total (EUR) *", min_value=100.0, max_value=1000000.0, value=float(opp['total_value']), step=100.0)
        
        with col2:
            stage = st.selectbox(
                "Etapa *", 
                ["prospecting", "qualification", "proposal", "negotiation", "closed_won", "closed_lost"],
                index=["prospecting", "qualification", "proposal", "negotiation", "closed_won", "closed_lost"].index(opp['stage'])
            )
            
            probability = st.slider("Probabilidad de Cierre (%)", min_value=0, max_value=100, value=int(opp['probability']), step=5)
            
            expected_close_date = st.date_input("Fecha Esperada de Cierre", value=datetime.strptime(opp['expected_close_date'], '%Y-%m-%d').date())
        
        notes = st.text_area(
            "Notas", 
            value=opp['notes'] or "",
            placeholder="Información adicional sobre la oportunidad...",
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            submitted = st.form_submit_button("💾 Actualizar Oportunidad", type="primary")
        
        with col2:
            cancelled = st.form_submit_button("❌ Cancelar")
        
        if cancelled:
            del st.session_state['edit_opportunity']
            st.rerun()
        
        if submitted:
            if opportunity_name and lead_id and bcs_solution and total_value > 0:
                update_opportunity(
                    opp_id, opportunity_name, lead_id, bcs_solution, 
                    total_value, stage, probability, expected_close_date, notes, partner['id']
                )
                st.success(f"✅ Oportunidad '{opportunity_name}' actualizada exitosamente!")
                del st.session_state['edit_opportunity']
                st.rerun()
            else:
                st.error("⚠️ Por favor completa los campos obligatorios (marcados con *)")
    
    conn.close()

def update_opportunity(opp_id, opportunity_name, lead_id, bcs_solution, total_value, 
                      stage, probability, expected_close_date, notes, partner_id):
    """Actualiza una oportunidad en la base de datos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE opportunities SET
                opportunity_name = ?, lead_id = ?, bcs_solution = ?, total_value = ?,
                stage = ?, probability = ?, expected_close_date = ?, notes = ?
            WHERE id = ?
        """, (
            opportunity_name, lead_id, bcs_solution, total_value,
            stage, probability, expected_close_date.strftime('%Y-%m-%d'), notes, opp_id
        ))
        
        # Registrar actividad de edición
        activity_date_str = datetime.now().date().strftime('%Y-%m-%d')
        created_datetime_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            INSERT INTO activities (
                lead_id, opportunity_id, partner_id, activity_type, description, 
                activity_date, created_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            lead_id, opp_id, partner_id, "opportunity_updated", 
            f"Oportunidad actualizada: {opportunity_name}", 
            activity_date_str, created_datetime_str
        ))
        
        conn.commit()
        
    except Exception as e:
        conn.rollback()
        st.error(f"Error al actualizar la oportunidad: {str(e)}")
    finally:
        conn.close()

def delete_lead(lead_id):
    """Elimina un lead y todas sus oportunidades y actividades asociadas"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información del lead antes de eliminarlo para el log
        lead_info = cursor.execute("SELECT company_name FROM leads WHERE id = ?", (lead_id,)).fetchone()
        company_name = lead_info[0] if lead_info else "Lead desconocido"
        
        # 1. Eliminar oportunidades asociadas al lead
        opportunities = cursor.execute("SELECT id, opportunity_name FROM opportunities WHERE lead_id = ?", (lead_id,)).fetchall()
        
        for opp_id, opp_name in opportunities:
            # Eliminar actividades de las oportunidades
            cursor.execute("DELETE FROM activities WHERE opportunity_id = ?", (opp_id,))
            # Eliminar la oportunidad
            cursor.execute("DELETE FROM opportunities WHERE id = ?", (opp_id,))
        
        # 2. Eliminar actividades asociadas directamente al lead
        cursor.execute("DELETE FROM activities WHERE lead_id = ?", (lead_id,))
        
        # 3. Eliminar el lead
        cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        
        conn.commit()
        
        # Mensaje informativo sobre lo que se eliminó
        opp_count = len(opportunities)
        if opp_count > 0:
            opp_names = [name for _, name in opportunities]
            st.info(f"📋 También se eliminaron {opp_count} oportunidad(es): {', '.join(opp_names)}")
        
    except Exception as e:
        conn.rollback()
        st.error(f"Error al eliminar el lead: {str(e)}")
    finally:
        conn.close()

# --- RUN APP ---
if __name__ == "__main__":
    main()