import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import webbrowser

# --- STYLES ---
def load_custom_css():
    st.markdown("""
    <style>
        .app-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            box-shadow: 0 8px 16px rgba(0,0,0,0.2);
            margin-bottom: 1rem;
            transition: transform 0.3s ease;
        }
        .app-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 24px rgba(0,0,0,0.3);
        }
        .app-title {
            font-size: 1.8rem;
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .app-description {
            font-size: 1rem;
            opacity: 0.9;
            margin-bottom: 1rem;
        }
        .app-meta {
            font-size: 0.85rem;
            opacity: 0.8;
        }
        .welcome-banner {
            background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            margin-bottom: 2rem;
            text-align: center;
        }
        .stats-card {
            background: #f8fafc;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #3b82f6;
            margin-bottom: 1rem;
        }
        .empty-state {
            text-align: center;
            padding: 3rem;
            color: #64748b;
        }
        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE FUNCTIONS ---
def get_db_connection():
    return sqlite3.connect('bcs_system.db')

def get_user_apps(user_id):
    """Get all Sub-BCS apps for a specific user"""
    conn = get_db_connection()
    apps = pd.read_sql_query('''
        SELECT 
            ubs.*,
            p.username as partner_name
        FROM user_sub_bcs ubs
        LEFT JOIN users p ON ubs.partner_id = p.id
        WHERE ubs.user_id = ? AND ubs.status = 'active'
        ORDER BY ubs.app_name
    ''', conn, params=(user_id,))
    conn.close()
    return apps

def update_app_access(app_id):
    """Update access count and last accessed timestamp"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE user_sub_bcs 
        SET access_count = access_count + 1,
            last_accessed = ?
        WHERE id = ?
    ''', (datetime.now(), app_id))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    """Get statistics for user dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total apps
    cursor.execute('SELECT COUNT(*) FROM user_sub_bcs WHERE user_id = ? AND status = "active"', (user_id,))
    total_apps = cursor.fetchone()[0]
    
    # Total accesses
    cursor.execute('SELECT COALESCE(SUM(access_count), 0) FROM user_sub_bcs WHERE user_id = ?', (user_id,))
    total_accesses = cursor.fetchone()[0]
    
    # Most used app
    cursor.execute('''
        SELECT app_name, access_count 
        FROM user_sub_bcs 
        WHERE user_id = ? AND access_count > 0
        ORDER BY access_count DESC 
        LIMIT 1
    ''', (user_id,))
    most_used = cursor.fetchone()
    most_used_app = most_used[0] if most_used else "N/A"
    
    # Last accessed
    cursor.execute('''
        SELECT app_name, last_accessed 
        FROM user_sub_bcs 
        WHERE user_id = ? AND last_accessed IS NOT NULL
        ORDER BY last_accessed DESC 
        LIMIT 1
    ''', (user_id,))
    last_accessed = cursor.fetchone()
    last_app = last_accessed[0] if last_accessed else "N/A"
    
    conn.close()
    
    return {
        'total_apps': total_apps,
        'total_accesses': total_accesses,
        'most_used_app': most_used_app,
        'last_app': last_app
    }

# --- MAIN DASHBOARD ---
def user_dashboard():
    """User dashboard - Client portal for accessing Sub-BCS apps"""
    load_custom_css()
    
    user_data = st.session_state.user_data
    user_id = user_data['id']
    username = user_data['username']
    
    # Welcome Banner
    st.markdown(f"""
    <div class="welcome-banner">
        <h1>👤 Bienvenido, {username}!</h1>
        <p style="font-size: 1.2rem; margin-top: 1rem;">
            Accede a todas tus aplicaciones y plataformas BCS desde un solo lugar
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Logout button in sidebar
    with st.sidebar:
        st.markdown("### 🔐 Mi Cuenta")
        st.write(f"**Usuario:** {username}")
        st.write(f"**Email:** {user_data.get('email', 'N/A')}")
        st.divider()
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
        
        st.divider()
        st.markdown("### 📊 Mis Estadísticas")
        stats = get_user_stats(user_id)
        st.metric("Apps Activas", stats['total_apps'])
        st.metric("Total Accesos", stats['total_accesses'])
        if stats['most_used_app'] != "N/A":
            st.write(f"**Más Usada:** {stats['most_used_app']}")
        if stats['last_app'] != "N/A":
            st.write(f"**Última Usada:** {stats['last_app']}")
    
    # Navigation Tabs
    tab1, tab2, tab3 = st.tabs([
        "🚀 Mis Aplicaciones",
        "📊 Panel de Control",
        "📖 Ayuda"
    ])
    
    with tab1:
        show_my_applications(user_id)
    
    with tab2:
        show_control_panel(user_id)
    
    with tab3:
        show_help_section()

# --- MY APPLICATIONS ---
def show_my_applications(user_id):
    st.subheader("🚀 Mis Aplicaciones BCS")
    st.markdown("Haz clic en cualquier aplicación para acceder directamente")
    
    # Get user apps
    apps = get_user_apps(user_id)
    
    if not apps.empty:
        # Group by app type
        app_types = apps['app_type'].unique()
        
        # Filter options
        col1, col2 = st.columns([2, 1])
        with col1:
            search = st.text_input("🔍 Buscar aplicación", placeholder="Nombre de la app...")
        with col2:
            type_filter = st.selectbox("Tipo", ["Todas"] + list(app_types))
        
        # Apply filters
        filtered_apps = apps.copy()
        if search:
            filtered_apps = filtered_apps[
                filtered_apps['app_name'].str.contains(search, case=False, na=False)
            ]
        if type_filter != "Todas":
            filtered_apps = filtered_apps[filtered_apps['app_type'] == type_filter]
        
        st.markdown(f"**Mostrando {len(filtered_apps)} de {len(apps)} aplicaciones**")
        st.divider()
        
        # Display apps in grid
        cols_per_row = 2
        for idx in range(0, len(filtered_apps), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for col_idx, col in enumerate(cols):
                app_idx = idx + col_idx
                if app_idx < len(filtered_apps):
                    app = filtered_apps.iloc[app_idx]
                    
                    with col:
                        # App Card
                        with st.container():
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                padding: 1.5rem;
                                border-radius: 12px;
                                color: white;
                                margin-bottom: 1rem;
                                min-height: 200px;
                            ">
                                <div style="font-size: 3rem; margin-bottom: 0.5rem;">{app['app_icon']}</div>
                                <div style="font-size: 1.3rem; font-weight: bold; margin-bottom: 0.5rem;">
                                    {app['app_name']}
                                </div>
                                <div style="font-size: 0.9rem; opacity: 0.9; margin-bottom: 1rem;">
                                    {app['app_description'] or 'Sin descripción'}
                                </div>
                                <div style="font-size: 0.8rem; opacity: 0.7;">
                                    📂 {app['app_type'] or 'General'}<br>
                                    🔢 Accesos: {app['access_count']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Access button
                            col_btn1, col_btn2 = st.columns(2)
                            with col_btn1:
                                if st.button(f"🚀 Abrir", key=f"open_{app['id']}", use_container_width=True):
                                    update_app_access(app['id'])
                                    st.success(f"Abriendo {app['app_name']}...")
                                    st.markdown(f"""
                                    <script>
                                        window.open("{app['app_url']}", "_blank");
                                    </script>
                                    """, unsafe_allow_html=True)
                                    # Alternative: show link
                                    st.link_button("🔗 Click aquí si no se abrió", app['app_url'])
                            
                            with col_btn2:
                                if st.button("ℹ️ Info", key=f"info_{app['id']}", use_container_width=True):
                                    st.session_state[f'show_info_{app["id"]}'] = True
                            
                            # Show info modal
                            if st.session_state.get(f'show_info_{app["id"]}', False):
                                with st.expander(f"📋 Detalles de {app['app_name']}", expanded=True):
                                    st.write(f"**Descripción:** {app['app_description'] or 'N/A'}")
                                    st.write(f"**Tipo:** {app['app_type'] or 'General'}")
                                    st.write(f"**URL:** {app['app_url']}")
                                    st.write(f"**Partner:** {app['partner_name'] or 'BCS Admin'}")
                                    st.write(f"**Total accesos:** {app['access_count']}")
                                    if app['last_accessed']:
                                        st.write(f"**Último acceso:** {app['last_accessed'][:16]}")
                                    st.write(f"**Creado:** {app['created_at'][:10]}")
                                    
                                    if st.button("Cerrar", key=f"close_info_{app['id']}"):
                                        st.session_state[f'show_info_{app["id"]}'] = False
                                        st.rerun()
    else:
        # Empty state
        st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">📦</div>
            <h2>No tienes aplicaciones asignadas</h2>
            <p>Contacta a tu administrador o partner para que te asigne aplicaciones BCS</p>
        </div>
        """, unsafe_allow_html=True)

# --- CONTROL PANEL ---
def show_control_panel(user_id):
    st.subheader("📊 Panel de Control")
    
    # Get stats
    stats = get_user_stats(user_id)
    apps = get_user_apps(user_id)
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🚀 Apps Activas", stats['total_apps'])
    with col2:
        st.metric("🔢 Total Accesos", stats['total_accesses'])
    with col3:
        if stats['most_used_app'] != "N/A":
            st.metric("⭐ Más Usada", "")
            st.caption(stats['most_used_app'])
        else:
            st.metric("⭐ Más Usada", "N/A")
    with col4:
        if stats['last_app'] != "N/A":
            st.metric("🕐 Última Usada", "")
            st.caption(stats['last_app'])
        else:
            st.metric("🕐 Última Usada", "N/A")
    
    st.divider()
    
    # Recent activity
    if not apps.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Aplicaciones por Tipo")
            type_counts = apps['app_type'].value_counts()
            if not type_counts.empty:
                for app_type, count in type_counts.items():
                    st.write(f"**{app_type or 'Sin tipo'}:** {count} apps")
            else:
                st.info("No hay datos de tipos")
        
        with col2:
            st.markdown("### 🔝 Top 5 Apps Más Usadas")
            top_apps = apps.nlargest(5, 'access_count')[['app_name', 'access_count']]
            if not top_apps.empty and top_apps['access_count'].sum() > 0:
                for _, app in top_apps.iterrows():
                    if app['access_count'] > 0:
                        st.write(f"**{app['app_name']}:** {app['access_count']} accesos")
            else:
                st.info("Aún no has usado ninguna aplicación")
        
        st.divider()
        
        # All apps table
        st.markdown("### 📋 Todas Mis Aplicaciones")
        display_apps = apps[['app_icon', 'app_name', 'app_type', 'access_count', 'status']].copy()
        display_apps.columns = ['🎯', 'Aplicación', 'Tipo', 'Accesos', 'Estado']
        st.dataframe(display_apps, use_container_width=True, hide_index=True)

# --- HELP SECTION ---
def show_help_section():
    st.subheader("📖 Ayuda y Soporte")
    
    with st.expander("❓ ¿Cómo usar mis aplicaciones?", expanded=True):
        st.markdown("""
        ### Acceder a tus aplicaciones BCS
        
        1. **Navega a "Mis Aplicaciones"**: En la primera pestaña encontrarás todas tus apps
        2. **Busca tu app**: Usa el buscador o filtro por tipo
        3. **Haz clic en "🚀 Abrir"**: La aplicación se abrirá en una nueva pestaña
        4. **Accede con tus credenciales**: Si la app requiere login, usa tus credenciales BCS
        
        ### Características
        - ✅ Acceso directo a todas tus plataformas
        - ✅ Búsqueda y filtros inteligentes
        - ✅ Estadísticas de uso
        - ✅ Información detallada de cada app
        """)
    
    with st.expander("🔐 Seguridad y Privacidad"):
        st.markdown("""
        ### Tus datos están protegidos
        
        - 🔒 **Conexión segura**: Todas las apps usan HTTPS
        - 👤 **Acceso personal**: Solo tú puedes ver tus aplicaciones
        - 📊 **Sin seguimiento**: No recopilamos datos personales
        - 🔑 **Autenticación**: Sistema de login seguro
        """)
    
    with st.expander("💡 Consejos y Recomendaciones"):
        st.markdown("""
        ### Aprovecha al máximo tu portal BCS
        
        - 📌 **Marca como favorito**: Guarda este portal en tus marcadores
        - 🔄 **Actualiza regularmente**: Nuevas apps pueden ser agregadas
        - 📧 **Contacta soporte**: Si necesitas ayuda con alguna app
        - 💬 **Reporta problemas**: Ayúdanos a mejorar reportando errores
        """)
    
    with st.expander("📞 Contacto y Soporte"):
        st.markdown("""
        ### ¿Necesitas ayuda?
        
        **Soporte Técnico BCS:**
        - 📧 Email: support@bcstechnologies.com
        - 📱 WhatsApp: +51 XXX XXX XXX
        - 🕐 Horario: Lunes a Viernes, 9:00 AM - 6:00 PM
        
        **Para solicitar nuevas aplicaciones:**
        - Contacta a tu partner o administrador BCS
        - Envía un email describiendo tus necesidades
        
        **Reportar problemas:**
        - Describe el problema detalladamente
        - Incluye capturas de pantalla si es posible
        - Indica qué aplicación presenta el problema
        """)
    
    st.divider()
    
    # Quick actions
    st.markdown("### ⚡ Acciones Rápidas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📧 Enviar Email a Soporte", use_container_width=True):
            st.info("Abriendo cliente de correo...")
            st.markdown("[Enviar email](mailto:support@bcstechnologies.com)")
    
    with col2:
        if st.button("📚 Ver Documentación", use_container_width=True):
            st.info("Documentación en desarrollo")
    
    with col3:
        if st.button("💬 Chat en Vivo", use_container_width=True):
            st.info("Chat en desarrollo")

def logout():
    """Logout function"""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_data = None
    st.rerun()
