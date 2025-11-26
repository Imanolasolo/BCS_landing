import streamlit as st
import sqlite3
from BCSDBconfig import BCSDatabase
from BCS_dashboards.admin_dashboard import admin_dashboard
from BCS_dashboards.partner_dashboard import partner_dashboard
from BCS_dashboards.user_dashboard import user_dashboard

# Page configuration
st.set_page_config(
    page_title="BCS Blackbox",
    page_icon="🔐",
    layout="wide"
)

# Initialize database
@st.cache_resource
def init_database():
    return BCSDatabase()

db = init_database()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

def login_page():
    """Display login form"""
    col1, col2, col3 = st.columns([1, 2.5, 0.5])
    with col1:
        st.image("assets/BCS_logo.png", width=130)
    with col2:
        st.title("BCS Blackbox")
        st.subheader("Tu plataforma :red[todo-en-uno] para negocios inteligentes.")
    with col3:
        st.image("assets/logo.png", width=300)
    
    st.markdown("---")
        
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        with st.expander("🔐 Sobre BCS Blackbox", expanded=False):
            st.markdown(
                """
                :red[BCS BlackBox] es tu centro de control inteligente.

                Una plataforma unificada que conecta todas tus aplicaciones, automatizaciones y flujos de trabajo en un solo lugar. 
                
                Desde aquí puedes administrar usuarios, roles, datos, procesos y módulos completos sin complejidad ni fricción. 
                
                BlackBox actúa como el núcleo que orquesta tus sistemas, garantiza seguridad de nivel empresarial y te permite escalar tus operaciones con total autonomía. 
                
                Todo en un entorno simple, rápido y diseñado para crecer contigo.
                """
            )
    with col2:
        st.markdown("### Iniciar Sesión")
        
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            submit_button = st.form_submit_button("Ingresar", use_container_width=True)
            
            if submit_button:
                if username and password:
                    user_data = db.authenticate_user(username, password)
                    
                    if user_data:
                        st.session_state.authenticated = True
                        st.session_state.user_role = user_data['role']
                        st.session_state.user_data = user_data
                        st.success(f"¡Bienvenido {user_data['username']}!")
                        st.rerun()
                    else:
                        st.error("Credenciales inválidas")
                else:
                    st.warning("Por favor complete todos los campos")
        
        
    with col3:
        with st.expander("Instrucciones para usar BCS BlackBox", expanded=False):
            st.markdown(
                """
                1. **Registro e Inicio de Sesión**: Usa el formulario para ingresar con tus credenciales. Si no tienes una cuenta, contacta al administrador.
                2. **Navegación del Panel**: Una vez dentro, utiliza la barra lateral para acceder a diferentes módulos según tu rol.
                3. **Gestión de Usuarios**: Los administradores pueden crear, editar y eliminar usuarios desde el panel de administración.
                4. **Monitoreo y Reportes**: Accede a informes detallados y paneles de monitoreo para tomar decisiones informadas.
                """
            )
def logout():
    """Logout function"""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_data = None
    st.rerun()

# Main application logic
if not st.session_state.authenticated:
    login_page()
else:
    # Route to appropriate dashboard based on role
    if st.session_state.user_role == 'admin':
        admin_dashboard()
    elif st.session_state.user_role == 'partner':
        partner_dashboard()
    elif st.session_state.user_role == 'cliente':
        user_dashboard()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>© 2024 BCS Blackbox - Powered by CodeCodix</p>
        <p><em>Sistema de análisis avanzado de datos</em></p>
    </div>
    """, 
    unsafe_allow_html=True
)
