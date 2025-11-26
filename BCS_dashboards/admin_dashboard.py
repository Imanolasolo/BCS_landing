import streamlit as st
import sqlite3
import pandas as pd
from .cruds.partner_crud import render_partner_crud
from .cruds.user_crud import render_user_crud

def admin_dashboard():
    """Admin dashboard with modular sidebar navigation"""
    st.title("🛠️ Panel de Administración")
    st.markdown(f"Bienvenido **{st.session_state.user_data['username']}**")
    
    # Logout button in the main area
    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("Cerrar Sesión"):
            logout()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🎛️ Panel de Control")
        st.markdown("---")
        
        # Main category selector
        categoria = st.selectbox(
            "📋 Categoría Principal",
            ["Actores", "Sub BCS"],
            index=0
        )
        
        st.markdown("---")
        
        # Secondary selector based on main category
        if categoria == "Actores":
            subcategoria = st.selectbox(
                "👥 Gestión de Actores",
                ["Gestión de Usuarios", "Gestión de Partners"],
                index=0
            )
        elif categoria == "Sub BCS":
            subcategoria = st.selectbox(
                "🏢 Gestión Sub BCS",
                ["Configuración Sub BCS", "Monitoreo Sub BCS"],
                index=0
            )
    
    # Main content area based on selection
    st.markdown("---")
    
    if categoria == "Actores":
        if subcategoria == "Gestión de Usuarios":
            render_user_management()
        elif subcategoria == "Gestión de Partners":
            render_partner_management()
    elif categoria == "Sub BCS":
        if subcategoria == "Configuración Sub BCS":
            render_sub_bcs_config()
        elif subcategoria == "Monitoreo Sub BCS":
            render_sub_bcs_monitoring()

def render_user_management():
    """Render user management interface"""
    st.subheader("👤 Gestión de Usuarios")
    
    # Get all users WITHOUT filtering by role_id
    conn = get_db_connection()
    
    # Modified query to show ALL users including those created by partners
    users = pd.read_sql_query('''
        SELECT 
            u.id,
            u.username,
            u.email,
            u.role_id,
            u.role,
            u.status,
            u.is_active,
            u.created_at,
            u.created_by_partner_id,
            p.username as created_by_partner
        FROM users u
        LEFT JOIN users p ON u.created_by_partner_id = p.id
        ORDER BY u.created_at DESC
    ''', conn)
    
    conn.close()
    
    if users.empty:
        st.warning("⚠️ No hay usuarios en el sistema")
        return
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👥 Total Usuarios", len(users))
    
    with col2:
        active_count = len(users[users['is_active'] == 1])
        st.metric("✅ Activos", active_count)
    
    with col3:
        # Count users created by partners
        partner_created = len(users[users['created_by_partner_id'].notna()])
        st.metric("🤝 Creados por Partners", partner_created)
    
    with col4:
        # Count by main roles
        admin_count = len(users[users['role_id'] == 1])
        st.metric("🛠️ Administradores", admin_count)
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        role_filter = st.selectbox(
            "🎭 Filtrar por Rol",
            ["Todos", "Administrador", "Partner", "Cliente", "Creados por Partners"],
            key="user_role_filter"
        )
    
    with col2:
        status_filter = st.selectbox(
            "📊 Estado",
            ["Todos", "Activos", "Inactivos"],
            key="user_status_filter"
        )
    
    with col3:
        search = st.text_input(
            "🔍 Buscar",
            placeholder="Usuario o email...",
            key="user_search"
        )
    
    # Apply filters
    filtered_users = users.copy()
    
    if role_filter == "Administrador":
        filtered_users = filtered_users[filtered_users['role_id'] == 1]
    elif role_filter == "Partner":
        filtered_users = filtered_users[filtered_users['role_id'] == 2]
    elif role_filter == "Cliente":
        filtered_users = filtered_users[(filtered_users['role_id'] == 3) | (filtered_users['role'] == 'client')]
    elif role_filter == "Creados por Partners":
        filtered_users = filtered_users[filtered_users['created_by_partner_id'].notna()]
    
    if status_filter == "Activos":
        filtered_users = filtered_users[filtered_users['is_active'] == 1]
    elif status_filter == "Inactivos":
        filtered_users = filtered_users[filtered_users['is_active'] == 0]
    
    if search:
        filtered_users = filtered_users[
            filtered_users['username'].str.contains(search, case=False, na=False) |
            filtered_users['email'].str.contains(search, case=False, na=False)
        ]
    
    st.markdown(f"**Mostrando {len(filtered_users)} de {len(users)} usuarios**")
    
    # Display users
    if not filtered_users.empty:
        for _, user in filtered_users.iterrows():
            # Determine role display
            if user['role_id'] == 1:
                role_display = "🛠️ Administrador"
                role_color = "blue"
            elif user['role_id'] == 2:
                role_display = "🤝 Partner"
                role_color = "green"
            elif user['role_id'] == 3:
                role_display = "👤 Cliente"
                role_color = "orange"
            else:
                # User created by partner without role_id
                role_display = f"👤 Cliente (Por Partner)"
                role_color = "purple"
            
            status_emoji = "✅" if user['is_active'] else "❌"
            
            # Build title with partner info if applicable
            title = f"{status_emoji} {user['username']} - {role_display}"
            if user['created_by_partner_id']:
                title += f" | 🤝 Creado por: {user['created_by_partner']}"
            
            with st.expander(title):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**🆔 ID:** {user['id']}")
                    st.write(f"**👤 Usuario:** {user['username']}")
                    st.write(f"**📧 Email:** {user['email'] or 'N/A'}")
                
                with col2:
                    st.write(f"**🎭 Rol ID:** {user['role_id'] or 'N/A'}")
                    st.write(f"**🎭 Rol:** {user['role'] or 'N/A'}")
                    st.write(f"**📊 Estado:** {user['status'] or 'N/A'}")
                
                with col3:
                    st.write(f"**✅ Activo:** {'Sí' if user['is_active'] else 'No'}")
                    st.write(f"**📅 Creado:** {user['created_at'][:10]}")
                    if user['created_by_partner_id']:
                        st.write(f"**🤝 Creado por:** {user['created_by_partner']}")
                    else:
                        st.write(f"**🤝 Creado por:** Sistema")
                
                st.divider()
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"📝 Editar", key=f"edit_user_{user['id']}"):
                        st.session_state[f'edit_user_{user["id"]}'] = True
                        st.rerun()
                
                with col2:
                    new_status = 0 if user['is_active'] else 1
                    status_text = "Desactivar" if user['is_active'] else "Activar"
                    if st.button(f"🔄 {status_text}", key=f"toggle_user_{user['id']}"):
                        update_user_status(user['id'], new_status)
                        st.success(f"Usuario {status_text.lower()}do")
                        st.rerun()
                
                with col3:
                    if user['id'] != 1:  # Protect admin user
                        if st.button(f"🗑️ Eliminar", key=f"delete_user_{user['id']}"):
                            if delete_user(user['id']):
                                st.success("Usuario eliminado")
                                st.rerun()
                    else:
                        st.caption("👑 Usuario protegido")
    else:
        st.info("No se encontraron usuarios con los filtros aplicados")
    
    # Add new user button
    st.markdown("---")
    if st.button("➕ Agregar Nuevo Usuario", use_container_width=True):
        st.session_state.show_add_user = True
        st.rerun()
    
    # Show add user form if requested
    if st.session_state.get('show_add_user', False):
        render_add_user_form()

def render_add_user_form():
    """Form to add new user"""
    with st.form("add_user_form"):
        st.markdown("### ➕ Agregar Nuevo Usuario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Usuario *")
            email = st.text_input("Email *")
            password = st.text_input("Contraseña *", type="password")
        
        with col2:
            role_id = st.selectbox("Rol *", [1, 2, 3], format_func=lambda x: {1: "Administrador", 2: "Partner", 3: "Cliente"}[x])
            status = st.selectbox("Estado", ["active", "inactive"])
            is_active = st.checkbox("Activo", value=True)
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Crear Usuario", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submit:
            if username and email and password:
                success, message = create_user(username, email, password, role_id, status, is_active)
                if success:
                    st.success(message)
                    st.session_state.show_add_user = False
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Completa todos los campos obligatorios")
        
        if cancel:
            st.session_state.show_add_user = False
            st.rerun()

def create_user(username, email, password, role_id, status, is_active):
    """Create a new user"""
    import hashlib
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        cursor.execute('''
            INSERT INTO users (username, password_hash, email, role_id, role, status, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (username, hashed_password, email, role_id, {1: 'admin', 2: 'partner', 3: 'client'}[role_id], status, 1 if is_active else 0))
        
        conn.commit()
        conn.close()
        return True, f"Usuario '{username}' creado exitosamente"
    
    except sqlite3.IntegrityError:
        conn.close()
        return False, "El usuario o email ya existe"
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

def update_user_status(user_id, new_status):
    """Update user active status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))
    conn.commit()
    conn.close()

def delete_user(user_id):
    """Delete a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

def render_partner_management():
    """Render partner management interface"""
    st.subheader("🤝 Gestión de Partners")
    
    # Import database from session state or initialize
    if 'db' not in st.session_state:
        from BCSDBconfig import BCSDatabase
        st.session_state.db = BCSDatabase()
    
    render_partner_crud(st.session_state.db)

def render_sub_bcs_config():
    """Render Sub BCS configuration interface"""
    st.subheader("🏢 Configuración de Sub BCS")
    st.markdown("Asigna aplicaciones y plataformas a clientes y partners")
    
    # Tabs for different assignment types
    tab1, tab2 = st.tabs(["📱 Asignar a Clientes", "🔧 Asignar a Partners"])
    
    with tab1:
        render_assign_client_sub_bcs()
    
    with tab2:
        render_assign_partner_sub_bcs()

def render_sub_bcs_monitoring():
    """Render Sub BCS monitoring interface"""
    st.subheader("📊 Monitoreo de Sub BCS")
    st.markdown("Vista general de todos los Sub-BCS del sistema")
    
    # Selector de tipo de Sub-BCS
    col1, col2 = st.columns([2, 3])
    with col1:
        tipo_sub_bcs = st.selectbox(
            "🔍 Selecciona el tipo de Sub-BCS",
            ["Sub-BCS de Clientes", "Sub-BCS de Partners"],
            key="tipo_sub_bcs_monitor"
        )
    
    st.markdown("---")
    
    if tipo_sub_bcs == "Sub-BCS de Clientes":
        render_client_sub_bcs_monitoring()
    else:
        render_partner_sub_bcs_monitoring()

def render_client_sub_bcs_monitoring():
    """Monitor Sub-BCS assigned to clients"""
    st.markdown("### 🏢 Sub-BCS de Clientes")
    st.caption("Aplicaciones y plataformas asignadas a usuarios clientes")
    
    conn = get_db_connection()
    
    # Get all client Sub-BCS with user info
    client_bcs = pd.read_sql_query('''
        SELECT 
            ubs.id,
            ubs.app_name,
            ubs.app_type,
            ubs.app_url,
            ubs.status,
            ubs.access_count,
            ubs.last_accessed,
            ubs.created_at,
            u.username as client_username,
            u.email as client_email,
            p.username as partner_name
        FROM user_sub_bcs ubs
        JOIN users u ON ubs.user_id = u.id
        LEFT JOIN users p ON ubs.partner_id = p.id
        ORDER BY ubs.created_at DESC
    ''', conn)
    
    conn.close()
    
    if client_bcs.empty:
        st.warning("⚠️ No hay Sub-BCS de clientes registrados en el sistema")
        st.info("💡 Los Sub-BCS de clientes son aplicaciones asignadas a usuarios con rol 'cliente'")
        return
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📱 Total Apps", len(client_bcs))
    
    with col2:
        active_count = len(client_bcs[client_bcs['status'] == 'active'])
        st.metric("✅ Activas", active_count)
    
    with col3:
        total_accesses = client_bcs['access_count'].sum()
        st.metric("🔢 Total Accesos", int(total_accesses))
    
    with col4:
        unique_clients = client_bcs['client_username'].nunique()
        st.metric("👥 Clientes", unique_clients)
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Estado",
            ["Todos"] + list(client_bcs['status'].unique()),
            key="client_bcs_status_filter"
        )
    
    with col2:
        type_filter = st.selectbox(
            "Tipo",
            ["Todos"] + list(client_bcs['app_type'].dropna().unique()),
            key="client_bcs_type_filter"
        )
    
    with col3:
        search = st.text_input(
            "🔍 Buscar",
            placeholder="App o cliente...",
            key="client_bcs_search"
        )
    
    # Apply filters
    filtered_bcs = client_bcs.copy()
    
    if status_filter != "Todos":
        filtered_bcs = filtered_bcs[filtered_bcs['status'] == status_filter]
    
    if type_filter != "Todos":
        filtered_bcs = filtered_bcs[filtered_bcs['app_type'] == type_filter]
    
    if search:
        filtered_bcs = filtered_bcs[
            filtered_bcs['app_name'].str.contains(search, case=False, na=False) |
            filtered_bcs['client_username'].str.contains(search, case=False, na=False)
        ]
    
    st.markdown(f"**Mostrando {len(filtered_bcs)} de {len(client_bcs)} Sub-BCS**")
    
    # Display as expandable cards
    if not filtered_bcs.empty:
        for _, bcs in filtered_bcs.iterrows():
            status_emoji = "✅" if bcs['status'] == 'active' else "❌"
            
            with st.expander(
                f"{status_emoji} {bcs['app_name']} - Cliente: {bcs['client_username']} | Accesos: {bcs['access_count']}"
            ):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**📱 Aplicación:** {bcs['app_name']}")
                    st.write(f"**🔗 URL:** {bcs['app_url']}")
                    st.write(f"**📂 Tipo:** {bcs['app_type'] or 'N/A'}")
                
                with col2:
                    st.write(f"**👤 Cliente:** {bcs['client_username']}")
                    st.write(f"**📧 Email:** {bcs['client_email'] or 'N/A'}")
                    st.write(f"**🤝 Partner:** {bcs['partner_name'] or 'Admin'}")
                
                with col3:
                    st.write(f"**📊 Estado:** {bcs['status']}")
                    st.write(f"**🔢 Accesos:** {bcs['access_count']}")
                    if bcs['last_accessed']:
                        st.write(f"**🕐 Último Acceso:** {bcs['last_accessed'][:16]}")
                    else:
                        st.write(f"**🕐 Último Acceso:** Nunca")
                    st.write(f"**📅 Creado:** {bcs['created_at'][:10]}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"🔗 Abrir URL", key=f"open_client_bcs_{bcs['id']}"):
                        st.link_button("Ir a la app", bcs['app_url'])
                
                with col2:
                    new_status = 'inactive' if bcs['status'] == 'active' else 'active'
                    if st.button(f"🔄 Cambiar a {new_status}", key=f"toggle_client_bcs_{bcs['id']}"):
                        update_client_bcs_status(bcs['id'], new_status)
                        st.success(f"Estado actualizado a {new_status}")
                        st.rerun()
                
                with col3:
                    if st.button(f"🗑️ Eliminar", key=f"delete_client_bcs_{bcs['id']}"):
                        if delete_client_bcs(bcs['id']):
                            st.success("Sub-BCS eliminado")
                            st.rerun()
    else:
        st.info("No se encontraron Sub-BCS con los filtros aplicados")
    
    # Summary by type
    st.markdown("---")
    st.markdown("### 📊 Distribución por Tipo")
    
    type_distribution = client_bcs['app_type'].value_counts()
    if not type_distribution.empty:
        col1, col2 = st.columns([2, 3])
        
        with col1:
            for tipo, count in type_distribution.items():
                st.write(f"**{tipo or 'Sin tipo'}:** {count} apps")
        
        with col2:
            # Most active clients
            st.markdown("#### 🏆 Top 5 Clientes por Apps")
            client_counts = client_bcs.groupby('client_username').size().sort_values(ascending=False).head(5)
            for username, count in client_counts.items():
                st.write(f"**{username}:** {count} apps")

def render_partner_sub_bcs_monitoring():
    """Monitor Sub-BCS created by partners"""
    st.markdown("### 🔧 Sub-BCS de Partners")
    st.caption("Sub-BCS propios creados por los partners para uso interno")
    
    conn = get_db_connection()
    
    # Get all partner Sub-BCS with partner info
    partner_bcs = pd.read_sql_query('''
        SELECT 
            pbs.id,
            pbs.bcs_name,
            pbs.bcs_type,
            pbs.description,
            pbs.modules,
            pbs.status,
            pbs.created_at,
            pbs.notes,
            u.username as partner_username,
            u.email as partner_email
        FROM partner_sub_bcs pbs
        JOIN users u ON pbs.partner_id = u.id
        ORDER BY pbs.created_at DESC
    ''', conn)
    
    conn.close()
    
    if partner_bcs.empty:
        st.warning("⚠️ No hay Sub-BCS de partners registrados en el sistema")
        st.info("💡 Los Sub-BCS de partners son herramientas internas creadas por socios comerciales")
        return
    
    # Statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔧 Total Sub-BCS", len(partner_bcs))
    
    with col2:
        active_count = len(partner_bcs[partner_bcs['status'] == 'active'])
        st.metric("✅ Activos", active_count)
    
    with col3:
        dev_count = len(partner_bcs[partner_bcs['status'] == 'development'])
        st.metric("🚧 En Desarrollo", dev_count)
    
    with col4:
        unique_partners = partner_bcs['partner_username'].nunique()
        st.metric("🤝 Partners", unique_partners)
    
    st.markdown("---")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox(
            "Estado",
            ["Todos"] + list(partner_bcs['status'].unique()),
            key="partner_bcs_status_filter"
        )
    
    with col2:
        type_filter = st.selectbox(
            "Tipo",
            ["Todos"] + list(partner_bcs['bcs_type'].dropna().unique()),
            key="partner_bcs_type_filter"
        )
    
    with col3:
        search = st.text_input(
            "🔍 Buscar",
            placeholder="Nombre o partner...",
            key="partner_bcs_search"
        )
    
    # Apply filters
    filtered_bcs = partner_bcs.copy()
    
    if status_filter != "Todos":
        filtered_bcs = filtered_bcs[filtered_bcs['status'] == status_filter]
    
    if type_filter != "Todos":
        filtered_bcs = filtered_bcs[filtered_bcs['bcs_type'] == type_filter]
    
    if search:
        filtered_bcs = filtered_bcs[
            filtered_bcs['bcs_name'].str.contains(search, case=False, na=False) |
            filtered_bcs['partner_username'].str.contains(search, case=False, na=False)
        ]
    
    st.markdown(f"**Mostrando {len(filtered_bcs)} de {len(partner_bcs)} Sub-BCS**")
    
    # Display as expandable cards
    if not filtered_bcs.empty:
        for _, bcs in filtered_bcs.iterrows():
            status_emoji = {"active": "✅", "inactive": "❌", "development": "🚧"}.get(bcs['status'], "❓")
            
            with st.expander(
                f"{status_emoji} {bcs['bcs_name']} - Partner: {bcs['partner_username']} | Tipo: {bcs['bcs_type']}"
            ):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**🔧 Nombre:** {bcs['bcs_name']}")
                    st.write(f"**📂 Tipo:** {bcs['bcs_type']}")
                    st.write(f"**📊 Estado:** {bcs['status']}")
                    if bcs['modules']:
                        st.write(f"**⚙️ Módulos:** {bcs['modules']}")
                
                with col2:
                    st.write(f"**🤝 Partner:** {bcs['partner_username']}")
                    st.write(f"**📧 Email:** {bcs['partner_email'] or 'N/A'}")
                    st.write(f"**📅 Creado:** {bcs['created_at'][:10]}")
                
                if bcs['description']:
                    st.write(f"**📝 Descripción:** {bcs['description']}")
                
                if bcs['notes']:
                    st.write(f"**📋 Notas:** {bcs['notes']}")
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button(f"📝 Ver Detalles", key=f"details_partner_bcs_{bcs['id']}"):
                        st.info("Vista de detalles completos")
                
                with col2:
                    new_status = 'inactive' if bcs['status'] == 'active' else 'active'
                    if st.button(f"🔄 Cambiar a {new_status}", key=f"toggle_partner_bcs_{bcs['id']}"):
                        update_partner_bcs_status(bcs['id'], new_status)
                        st.success(f"Estado actualizado a {new_status}")
                        st.rerun()
                
                with col3:
                    if st.button(f"🗑️ Eliminar", key=f"delete_partner_bcs_{bcs['id']}"):
                        if delete_partner_bcs(bcs['id']):
                            st.success("Sub-BCS eliminado")
                            st.rerun()
    else:
        st.info("No se encontraron Sub-BCS con los filtros aplicados")
    
    # Summary by type
    st.markdown("---")
    st.markdown("### 📊 Distribución por Tipo")
    
    type_distribution = partner_bcs['bcs_type'].value_counts()
    if not type_distribution.empty:
        col1, col2 = st.columns([2, 3])
        
        with col1:
            for tipo, count in type_distribution.items():
                st.write(f"**{tipo or 'Sin tipo'}:** {count} Sub-BCS")
        
        with col2:
            # Most active partners
            st.markdown("#### 🏆 Top 5 Partners por Sub-BCS")
            partner_counts = partner_bcs.groupby('partner_username').size().sort_values(ascending=False).head(5)
            for username, count in partner_counts.items():
                st.write(f"**{username}:** {count} Sub-BCS")

def render_assign_client_sub_bcs():
    """Interface to assign Sub-BCS apps to clients"""
    st.markdown("### 📱 Asignar Aplicación a Cliente")
    st.caption("Crea un link a una aplicación Streamlit para un cliente específico")
    
    conn = get_db_connection()
    
    # Get all clients (role = 3)
    clients = pd.read_sql_query(
        "SELECT id, username, email FROM users WHERE role_id = 3 ORDER BY username",
        conn
    )
    
    # Get all partners for optional assignment
    partners = pd.read_sql_query(
        "SELECT id, username FROM users WHERE role_id = 2 ORDER BY username",
        conn
    )
    
    if clients.empty:
        st.warning("⚠️ No hay clientes registrados en el sistema")
        conn.close()
        return
    
    st.markdown("---")
    
    # Form to create new assignment
    with st.form("assign_client_sub_bcs_form", clear_on_submit=True):
        st.markdown("#### 📝 Nueva Asignación")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Client selection
            client_options = {f"{c['username']} ({c['email']})": c['id'] for _, c in clients.iterrows()}
            selected_client = st.selectbox(
                "👤 Cliente *",
                options=list(client_options.keys()),
                help="Cliente que recibirá acceso a la aplicación"
            )
            
            # App name
            app_name = st.text_input(
                "📱 Nombre de la Aplicación *",
                placeholder="Ej: Dashboard Financiero",
                help="Nombre descriptivo de la aplicación"
            )
            
            # App type
            app_type = st.selectbox(
                "📂 Tipo de Aplicación *",
                ["Dashboard", "CRM", "Analytics", "Reports", "ERP", "Custom"],
                help="Categoría de la aplicación"
            )
            
            # App icon
            app_icon = st.text_input(
                "🎨 Icono (Emoji)",
                value="📊",
                help="Emoji que representa la aplicación"
            )
        
        with col2:
            # Partner assignment (optional)
            partner_options = {"Sin Partner Asignado": None}
            partner_options.update({p['username']: p['id'] for _, p in partners.iterrows()})
            selected_partner = st.selectbox(
                "🤝 Partner (Opcional)",
                options=list(partner_options.keys()),
                help="Partner responsable de la aplicación (opcional)"
            )
            
            # App URL
            app_url = st.text_input(
                "🔗 URL de la Aplicación *",
                placeholder="https://your-app.streamlit.app",
                help="URL completa de la aplicación en Streamlit Cloud"
            )
            
            # App description
            app_description = st.text_area(
                "📝 Descripción",
                placeholder="Descripción breve de la aplicación y sus funcionalidades",
                help="Descripción opcional de la aplicación"
            )
            
            # Status
            status = st.selectbox(
                "📊 Estado *",
                ["active", "inactive"],
                index=0,
                help="Estado inicial de la aplicación"
            )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submit = st.form_submit_button("✅ Asignar Aplicación", use_container_width=True)
        with col2:
            clear = st.form_submit_button("🔄 Limpiar", use_container_width=True)
        
        if submit:
            if not app_name or not app_url:
                st.error("❌ Por favor completa todos los campos obligatorios (*)")
            elif not app_url.startswith("http"):
                st.error("❌ La URL debe comenzar con http:// o https://")
            else:
                client_id = client_options[selected_client]
                partner_id = partner_options[selected_partner]
                
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO user_sub_bcs 
                        (user_id, partner_id, app_name, app_description, app_url, app_icon, app_type, status, created_at, access_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), 0)
                    ''', (client_id, partner_id, app_name, app_description, app_url, app_icon, app_type, status))
                    conn.commit()
                    st.success(f"✅ Aplicación '{app_name}' asignada exitosamente a {selected_client.split(' (')[0]}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al asignar aplicación: {str(e)}")
    
    conn.close()
    
    # Show existing assignments
    st.markdown("---")
    st.markdown("### 📋 Asignaciones Existentes")
    
    conn = get_db_connection()
    existing_apps = pd.read_sql_query('''
        SELECT 
            ubs.id,
            ubs.app_name,
            ubs.app_type,
            ubs.app_url,
            ubs.status,
            ubs.access_count,
            ubs.created_at,
            u.username as client_username,
            p.username as partner_name
        FROM user_sub_bcs ubs
        JOIN users u ON ubs.user_id = u.id
        LEFT JOIN users p ON ubs.partner_id = p.id
        ORDER BY ubs.created_at DESC
        LIMIT 10
    ''', conn)
    conn.close()
    
    if not existing_apps.empty:
        st.caption(f"Mostrando las últimas {len(existing_apps)} asignaciones")
        
        for _, app in existing_apps.iterrows():
            status_emoji = "✅" if app['status'] == 'active' else "❌"
            
            with st.expander(f"{status_emoji} {app['app_name']} → {app['client_username']} ({app['app_type']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**📱 App:** {app['app_name']}")
                    st.write(f"**🔗 URL:** {app['app_url']}")
                
                with col2:
                    st.write(f"**👤 Cliente:** {app['client_username']}")
                    st.write(f"**🤝 Partner:** {app['partner_name'] or 'N/A'}")
                
                with col3:
                    st.write(f"**📊 Estado:** {app['status']}")
                    st.write(f"**🔢 Accesos:** {app['access_count']}")
                    st.write(f"**📅 Creado:** {app['created_at'][:10]}")
    else:
        st.info("No hay asignaciones previas")

def render_assign_partner_sub_bcs():
    """Interface to assign Sub-BCS tools to partners"""
    st.markdown("### 🔧 Asignar Sub-BCS a Partner")
    st.caption("Registra un Sub-BCS propio del partner (herramientas internas)")
    
    conn = get_db_connection()
    
    # Get all partners (role = 2)
    partners = pd.read_sql_query(
        "SELECT id, username, email FROM users WHERE role_id = 2 ORDER BY username",
        conn
    )
    
    if partners.empty:
        st.warning("⚠️ No hay partners registrados en el sistema")
        conn.close()
        return
    
    st.markdown("---")
    
    # Form to create new Sub-BCS assignment
    with st.form("assign_partner_sub_bcs_form", clear_on_submit=True):
        st.markdown("#### 📝 Nuevo Sub-BCS de Partner")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Partner selection
            partner_options = {f"{p['username']} ({p['email']})": p['id'] for _, p in partners.iterrows()}
            selected_partner = st.selectbox(
                "🤝 Partner *",
                options=list(partner_options.keys()),
                help="Partner propietario del Sub-BCS"
            )
            
            # Sub-BCS name
            bcs_name = st.text_input(
                "🔧 Nombre del Sub-BCS *",
                placeholder="Ej: Sistema de Gestión Interna",
                help="Nombre del Sub-BCS"
            )
            
            # Sub-BCS type
            bcs_type = st.selectbox(
                "📂 Tipo de Sub-BCS *",
                ["CRM Interno", "ERP", "Analytics", "Dashboard", "Gestión", "Custom"],
                help="Tipo de Sub-BCS"
            )
            
            # Modules
            modules = st.text_input(
                "⚙️ Módulos",
                placeholder="Ej: Ventas, Inventario, Reportes",
                help="Módulos incluidos (separados por coma)"
            )
        
        with col2:
            # Description
            description = st.text_area(
                "📝 Descripción *",
                placeholder="Descripción del Sub-BCS y su funcionalidad",
                help="Descripción del Sub-BCS"
            )
            
            # Notes
            notes = st.text_area(
                "📋 Notas",
                placeholder="Notas adicionales o comentarios",
                help="Notas internas (opcional)"
            )
            
            # Status
            status = st.selectbox(
                "📊 Estado *",
                ["active", "inactive", "development"],
                index=0,
                help="Estado actual del Sub-BCS"
            )
        
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            submit = st.form_submit_button("✅ Asignar Sub-BCS", use_container_width=True)
        with col2:
            clear = st.form_submit_button("🔄 Limpiar", use_container_width=True)
        
        if submit:
            if not bcs_name or not bcs_type or not description:
                st.error("❌ Por favor completa todos los campos obligatorios (*)")
            else:
                partner_id = partner_options[selected_partner]
                
                try:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO partner_sub_bcs 
                        (partner_id, bcs_name, bcs_type, description, modules, status, created_at, notes)
                        VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
                    ''', (partner_id, bcs_name, bcs_type, description, modules, status, notes))
                    conn.commit()
                    st.success(f"✅ Sub-BCS '{bcs_name}' asignado exitosamente a {selected_partner.split(' (')[0]}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error al asignar Sub-BCS: {str(e)}")
    
    conn.close()
    
    # Show existing assignments
    st.markdown("---")
    st.markdown("### 📋 Sub-BCS de Partners Existentes")
    
    conn = get_db_connection()
    existing_bcs = pd.read_sql_query('''
        SELECT 
            pbs.id,
            pbs.bcs_name,
            pbs.bcs_type,
            pbs.description,
            pbs.modules,
            pbs.status,
            pbs.created_at,
            u.username as partner_username
        FROM partner_sub_bcs pbs
        JOIN users u ON pbs.partner_id = u.id
        ORDER BY pbs.created_at DESC
        LIMIT 10
    ''', conn)
    conn.close()
    
    if not existing_bcs.empty:
        st.caption(f"Mostrando los últimos {len(existing_bcs)} Sub-BCS")
        
        for _, bcs in existing_bcs.iterrows():
            status_emoji = {"active": "✅", "inactive": "❌", "development": "🚧"}.get(bcs['status'], "❓")
            
            with st.expander(f"{status_emoji} {bcs['bcs_name']} → {bcs['partner_username']} ({bcs['bcs_type']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**🔧 Nombre:** {bcs['bcs_name']}")
                    st.write(f"**📂 Tipo:** {bcs['bcs_type']}")
                    st.write(f"**⚙️ Módulos:** {bcs['modules'] or 'N/A'}")
                
                with col2:
                    st.write(f"**🤝 Partner:** {bcs['partner_username']}")
                    st.write(f"**📊 Estado:** {bcs['status']}")
                    st.write(f"**📅 Creado:** {bcs['created_at'][:10]}")
                
                st.write(f"**📝 Descripción:** {bcs['description']}")
    else:
        st.info("No hay Sub-BCS de partners registrados")

# Helper functions
def get_db_connection():
    """Get database connection"""
    return sqlite3.connect('bcs_system.db')

def update_client_bcs_status(bcs_id, new_status):
    """Update status of client Sub-BCS"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE user_sub_bcs SET status = ? WHERE id = ?",
        (new_status, bcs_id)
    )
    conn.commit()
    conn.close()

def delete_client_bcs(bcs_id):
    """Delete client Sub-BCS"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_sub_bcs WHERE id = ?", (bcs_id,))
    conn.commit()
    conn.close()
    return True

def update_partner_bcs_status(bcs_id, new_status):
    """Update status of partner Sub-BCS"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE partner_sub_bcs SET status = ? WHERE id = ?",
        (new_status, bcs_id)
    )
    conn.commit()
    conn.close()

def delete_partner_bcs(bcs_id):
    """Delete partner Sub-BCS"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM partner_sub_bcs WHERE id = ?", (bcs_id,))
    conn.commit()
    conn.close()
    return True

def logout():
    """Logout function"""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_data = None
    st.rerun()
