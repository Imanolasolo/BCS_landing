import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
import hashlib

# --- STYLES ---
def load_custom_css():
    st.markdown("""
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 10px;
            color: white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
        }
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #f0f2f6;
            border-radius: 5px;
            padding: 10px 20px;
        }
    </style>
    """, unsafe_allow_html=True)

# --- DATABASE FUNCTIONS ---
def get_db_connection():
    return sqlite3.connect('bcs_system.db')

def get_partner_stats(partner_id):
    """Get statistics for partner dashboard"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total contacts
    cursor.execute('SELECT COUNT(*) FROM contacts WHERE partner_id = ? AND status = "active"', (partner_id,))
    total_contacts = cursor.fetchone()[0]
    
    # Validated contacts pending conversion
    cursor.execute('SELECT COUNT(*) FROM contacts WHERE partner_id = ? AND status = "active" AND validated = 1 AND converted_to_user = 0', (partner_id,))
    validated_pending = cursor.fetchone()[0]
    
    # Total client Sub-BCS (from both tables)
    cursor.execute('SELECT COUNT(*) FROM client_sub_bcs WHERE partner_id = ? AND status = "active"', (partner_id,))
    client_bcs_crm = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM user_sub_bcs WHERE partner_id = ? AND status = "active"', (partner_id,))
    client_bcs_apps = cursor.fetchone()[0]
    
    total_client_bcs = client_bcs_crm + client_bcs_apps
    
    # Total partner Sub-BCS
    cursor.execute('SELECT COUNT(*) FROM partner_sub_bcs WHERE partner_id = ? AND status = "active"', (partner_id,))
    total_partner_bcs = cursor.fetchone()[0]
    
    # Monthly revenue from clients
    cursor.execute('SELECT COALESCE(SUM(monthly_value), 0) FROM client_sub_bcs WHERE partner_id = ? AND status = "active"', (partner_id,))
    monthly_revenue = cursor.fetchone()[0]
    
    # Pending activities
    cursor.execute('SELECT COUNT(*) FROM partner_activities WHERE partner_id = ? AND completed = 0', (partner_id,))
    pending_activities = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        'total_contacts': total_contacts,
        'validated_pending': validated_pending,
        'total_client_bcs': total_client_bcs,
        'total_partner_bcs': total_partner_bcs,
        'monthly_revenue': monthly_revenue,
        'pending_activities': pending_activities
    }

# --- MAIN DASHBOARD ---
def partner_dashboard():
    """Partner CRM Dashboard"""
    load_custom_css()
    
    user_data = st.session_state.user_data
    partner_id = user_data['id']
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"🤝 CRM Partner - {user_data['username']}")
        st.markdown("Gestiona tus contactos, clientes y Sub-BCS")
    with col2:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            logout()
    
    st.divider()
    
    # Dashboard Stats
    stats = get_partner_stats(partner_id)
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("👥 Contactos", stats['total_contacts'])
    with col2:
        st.metric("✅ Validados", stats['validated_pending'], help="Contactos validados pendientes de conversión")
    with col3:
        st.metric("🏢 Sub-BCS Clientes", stats['total_client_bcs'])
    with col4:
        st.metric("🔧 Sub-BCS Propios", stats['total_partner_bcs'])
    with col5:
        st.metric("💰 Ingresos Mes", f"${stats['monthly_revenue']:,.0f}")
    with col6:
        st.metric("📋 Actividades", stats['pending_activities'])
    
    st.divider()
    
    # Navigation Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Dashboard", 
        "👥 Contactos", 
        "🏢 Sub-BCS Clientes",
        "🔧 Sub-BCS Propios",
        "📝 Actividades"
    ])
    
    with tab1:
        show_dashboard_overview(partner_id)
    
    with tab2:
        show_contacts_management(partner_id)
    
    with tab3:
        show_client_bcs_management(partner_id)
    
    with tab4:
        show_partner_bcs_management(partner_id)
    
    with tab5:
        show_activities_management(partner_id)

# --- DASHBOARD OVERVIEW ---
def show_dashboard_overview(partner_id):
    st.subheader("📊 Resumen General")
    
    conn = get_db_connection()
    
    # Recent activities
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📝 Actividades Recientes")
        activities = pd.read_sql_query('''
            SELECT pa.*, c.name as contact_name
            FROM partner_activities pa
            LEFT JOIN contacts c ON pa.contact_id = c.id
            WHERE pa.partner_id = ?
            ORDER BY pa.activity_date DESC
            LIMIT 5
        ''', conn, params=(partner_id,))
        
        if not activities.empty:
            for _, activity in activities.iterrows():
                status = "✅" if activity['completed'] else "⏳"
                st.write(f"{status} **{activity['activity_type']}** - {activity['subject']}")
                st.caption(f"Contacto: {activity['contact_name']} | {activity['activity_date']}")
                st.divider()
        else:
            st.info("No hay actividades recientes")
    
    with col2:
        st.markdown("### 💼 Sub-BCS Activos")
        client_bcs = pd.read_sql_query('''
            SELECT bcs_type, COUNT(*) as count
            FROM client_sub_bcs
            WHERE partner_id = ? AND status = 'active'
            GROUP BY bcs_type
        ''', conn, params=(partner_id,))
        
        if not client_bcs.empty:
            fig = px.pie(client_bcs, values='count', names='bcs_type', 
                        title='Distribución por Tipo de BCS')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay Sub-BCS registrados")
    
    # Revenue chart
    st.markdown("### 📈 Ingresos Mensuales por Cliente")
    revenue_data = pd.read_sql_query('''
        SELECT client_name, monthly_value
        FROM client_sub_bcs
        WHERE partner_id = ? AND status = 'active' AND monthly_value > 0
        ORDER BY monthly_value DESC
        LIMIT 10
    ''', conn, params=(partner_id,))
    
    if not revenue_data.empty:
        fig = px.bar(revenue_data, x='client_name', y='monthly_value',
                    labels={'monthly_value': 'Ingresos Mensuales', 'client_name': 'Cliente'},
                    color='monthly_value')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de ingresos")
    
    conn.close()

# --- CONTACTS MANAGEMENT ---
def show_contacts_management(partner_id):
    st.subheader("👥 Gestión de Contactos")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nuevo Contacto", use_container_width=True):
            st.session_state.show_add_contact = True
    
    # Add new contact form
    if st.session_state.get('show_add_contact', False):
        with st.form("add_contact_form"):
            st.markdown("### Agregar Nuevo Contacto")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Nombre Completo *")
                email = st.text_input("Email")
                phone = st.text_input("Teléfono")
            
            with col2:
                company = st.text_input("Empresa")
                position = st.text_input("Cargo")
                industry = st.selectbox("Industria", [
                    "Hospitalaria", "Pesquera", "Industrial", "Comercial", 
                    "Tecnología", "Educación", "Otro"
                ])
            
            notes = st.text_area("Notas")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Guardar Contacto", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                if name:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO contacts (partner_id, name, company, email, phone, position, industry, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (partner_id, name, company, email, phone, position, industry, notes))
                    conn.commit()
                    conn.close()
                    st.success("✅ Contacto agregado exitosamente")
                    st.session_state.show_add_contact = False
                    st.rerun()
                else:
                    st.error("El nombre es obligatorio")
            
            if cancel:
                st.session_state.show_add_contact = False
                st.rerun()
    
    # List contacts
    conn = get_db_connection()
    contacts = pd.read_sql_query('''
        SELECT * FROM contacts 
        WHERE partner_id = ?
        ORDER BY validated DESC, created_at DESC
    ''', conn, params=(partner_id,))
    
    if not contacts.empty:
        # Filter options
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            status_filter = st.selectbox("Estado", ["Todos", "active", "inactive"])
        with col2:
            validation_filter = st.selectbox("Validación", ["Todos", "Validados", "Sin validar", "Convertidos"])
        with col3:
            industry_filter = st.selectbox("Industria", ["Todas"] + list(contacts['industry'].unique()))
        with col4:
            search = st.text_input("🔍 Buscar", placeholder="Nombre o empresa...")
        
        # Apply filters
        filtered_contacts = contacts.copy()
        if status_filter != "Todos":
            filtered_contacts = filtered_contacts[filtered_contacts['status'] == status_filter]
        
        if validation_filter == "Validados":
            filtered_contacts = filtered_contacts[(filtered_contacts['validated'] == 1) & (filtered_contacts['converted_to_user'] == 0)]
        elif validation_filter == "Sin validar":
            filtered_contacts = filtered_contacts[filtered_contacts['validated'] == 0]
        elif validation_filter == "Convertidos":
            filtered_contacts = filtered_contacts[filtered_contacts['converted_to_user'] == 1]
        
        if industry_filter != "Todas":
            filtered_contacts = filtered_contacts[filtered_contacts['industry'] == industry_filter]
        if search:
            filtered_contacts = filtered_contacts[
                filtered_contacts['name'].str.contains(search, case=False, na=False) |
                filtered_contacts['company'].str.contains(search, case=False, na=False)
            ]
        
        st.markdown(f"**Total: {len(filtered_contacts)} contactos**")
        
        # Display contacts
        for _, contact in filtered_contacts.iterrows():
            # Status badges
            validated_badge = "✅ VALIDADO" if contact['validated'] else "⏳ Pendiente"
            converted_badge = "👤 CONVERTIDO" if contact['converted_to_user'] else ""
            
            title = f"👤 {contact['name']} - {contact['company'] or 'Sin empresa'}"
            if contact['validated']:
                title = f"✅ {title}"
            if contact['converted_to_user']:
                title = f"👥 {title} (Usuario creado)"
            
            with st.expander(title):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Email:** {contact['email'] or 'N/A'}")
                    st.write(f"**Teléfono:** {contact['phone'] or 'N/A'}")
                
                with col2:
                    st.write(f"**Cargo:** {contact['position'] or 'N/A'}")
                    st.write(f"**Industria:** {contact['industry'] or 'N/A'}")
                
                with col3:
                    st.write(f"**Estado:** {contact['status']}")
                    st.write(f"**Validación:** {validated_badge}")
                    if contact['validated']:
                        st.write(f"**Fecha validación:** {contact['validation_date'] or 'N/A'}")
                    if contact['converted_to_user']:
                        st.write(f"**{converted_badge}**")
                        st.write(f"**Fecha conversión:** {contact['conversion_date'] or 'N/A'}")
                        
                        # Show username of created user
                        if contact['converted_user_id']:
                            cursor = conn.cursor()
                            cursor.execute('SELECT username, role, status FROM users WHERE id = ?', (contact['converted_user_id'],))
                            user_info = cursor.fetchone()
                            if user_info:
                                st.write(f"**👤 Usuario:** {user_info[0]}")
                                st.write(f"**🔐 Rol:** {user_info[1]}")
                                st.write(f"**📊 Estado:** {user_info[2]}")
                            else:
                                st.warning("⚠️ Usuario no encontrado en la base de datos")
                
                if contact['notes']:
                    st.write(f"**Notas:** {contact['notes']}")
                
                st.divider()
                
                # Action buttons
                if contact['converted_to_user']:
                    # Already converted
                    st.info("✅ Este contacto ya fue convertido a usuario/cliente")
                    
                    # Show user credentials info
                    if contact['converted_user_id']:
                        cursor = conn.cursor()
                        cursor.execute('SELECT username, email FROM users WHERE id = ?', (contact['converted_user_id'],))
                        user_creds = cursor.fetchone()
                        if user_creds:
                            st.success(f"**Credenciales de acceso:**\n\n👤 Usuario: `{user_creds[0]}`\n\n📧 Email: `{user_creds[1]}`")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"👁️ Ver Usuario Completo", key=f"view_user_{contact['converted_user_id']}"):
                            # Show detailed user info
                            cursor = conn.cursor()
                            cursor.execute('SELECT * FROM users WHERE id = ?', (contact['converted_user_id'],))
                            full_user = cursor.fetchone()
                            cursor.execute("PRAGMA table_info(users)")
                            columns = [col[1] for col in cursor.fetchall()]
                            
                            if full_user:
                                st.session_state[f'show_user_detail_{contact["converted_user_id"]}'] = True
                    with col2:
                        if st.button(f"🗑️ Eliminar Contacto", key=f"delete_contact_{contact['id']}"):
                            cursor = conn.cursor()
                            cursor.execute('DELETE FROM contacts WHERE id = ?', (contact['id'],))
                            conn.commit()
                            st.success("Contacto eliminado")
                            st.rerun()
                    
                    # Show detailed user info if requested
                    if st.session_state.get(f'show_user_detail_{contact["converted_user_id"]}', False):
                        with st.expander("📋 Información Completa del Usuario", expanded=True):
                            cursor = conn.cursor()
                            cursor.execute('SELECT * FROM users WHERE id = ?', (contact['converted_user_id'],))
                            full_user = cursor.fetchone()
                            cursor.execute("PRAGMA table_info(users)")
                            columns = [col[1] for col in cursor.fetchall()]
                            
                            if full_user:
                                for i, col in enumerate(columns):
                                    if col not in ['password', 'password_hash']:
                                        st.write(f"**{col}:** {full_user[i]}")
                            
                            if st.button("✖️ Cerrar", key=f"close_detail_{contact['converted_user_id']}"):
                                del st.session_state[f'show_user_detail_{contact["converted_user_id"]}']
                                st.rerun()
                
                elif contact['validated']:
                    # Validated but not converted
                    st.success("✅ Contacto validado - Listo para convertir a usuario")
                    
                    if st.button(f"🔄 Convertir a Usuario", key=f"convert_{contact['id']}", use_container_width=True):
                        st.session_state[f'show_convert_{contact["id"]}'] = True
                        st.rerun()
                    
                    # Show conversion form
                    if st.session_state.get(f'show_convert_{contact["id"]}', False):
                        with st.form(f"convert_form_{contact['id']}"):
                            st.markdown("### 👤 Crear Usuario desde Contacto")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                username = st.text_input("Usuario *", value=contact['email'].split('@')[0] if contact['email'] else "")
                                password = st.text_input("Contraseña *", type="password")
                            with col2:
                                confirm_password = st.text_input("Confirmar Contraseña *", type="password")
                            

                            st.info(f"📧 Email: {contact['email']}\n👤 Nombre: {contact['name']}\n🏢 Empresa: {contact['company']}")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                submit = st.form_submit_button("✅ Crear Usuario", use_container_width=True)
                            with col2:
                                cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
                            

                            if submit:
                                if username and password and password == confirm_password:
                                    with st.spinner("Creando usuario..."):
                                        success, message = create_user_from_contact(contact['id'], username, password, partner_id)
                                    
                                    if success:
                                        st.success(message)
                                        st.balloons()
                                        # Clean up session state
                                        if f'show_convert_{contact["id"]}' in st.session_state:
                                            del st.session_state[f'show_convert_{contact["id"]}']
                                        # Wait a moment before rerun
                                        import time
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(message)
                                        # Show debug info in expander
                                        with st.expander("🔍 Información de depuración"):
                                            st.code(f"""
                                            Contact ID: {contact['id']}
                                            Username: {username}
                                            Email: {contact['email']}
                                            Partner ID: {partner_id}
                                            Error: {message}
                                            """)
                                elif password != confirm_password:
                                    st.error("Las contraseñas no coinciden")
                                else:
                                    st.error("Completa todos los campos")
                            
                            if cancel:
                                if f'show_convert_{contact["id"]}' in st.session_state:
                                    del st.session_state[f'show_convert_{contact["id"]}']
                                st.rerun()
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"📝 Editar", key=f"edit_contact_{contact['id']}"):
                            st.session_state[f'edit_contact_{contact["id"]}'] = True
                            st.rerun()
                    with col2:
                        if st.button(f"🗑️ Eliminar", key=f"delete_contact_{contact['id']}"):
                            cursor = conn.cursor()
                            cursor.execute('DELETE FROM contacts WHERE id = ?', (contact['id'],))
                            conn.commit()
                            st.success("Contacto eliminado")
                            st.rerun()
                
                else:
                    # Not validated yet
                    st.warning("⏳ Contacto pendiente de validación")
                    st.info("💡 Registra una actividad de 'Validación de Cliente' con resultado exitoso para poder convertirlo a usuario")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"📝 Editar", key=f"edit_contact_{contact['id']}"):
                            st.session_state[f'edit_contact_{contact["id"]}'] = True
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🗑️ Eliminar", key=f"delete_contact_{contact['id']}"):
                            cursor = conn.cursor()
                            cursor.execute('DELETE FROM contacts WHERE id = ?', (contact['id'],))
                            conn.commit()
                            st.success("Contacto eliminado")
                            st.rerun()
                    
                    with col3:
                        new_status = "inactive" if contact['status'] == "active" else "active"
                        if st.button(f"🔄 {new_status}", key=f"toggle_contact_{contact['id']}"):
                            cursor = conn.cursor()
                            cursor.execute('UPDATE contacts SET status = ? WHERE id = ?', (new_status, contact['id']))
                            conn.commit()
                            st.success(f"Estado actualizado a {new_status}")
                            st.rerun()
    else:
        st.info("No tienes contactos registrados. ¡Agrega tu primer contacto!")
    
    conn.close()

def convert_contact_to_user(contact_id, partner_id):
    """Convert a validated contact to a user/client"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get contact info
    cursor.execute('SELECT * FROM contacts WHERE id = ? AND partner_id = ?', (contact_id, partner_id))
    contact = cursor.fetchone()
    
    if not contact:
        conn.close()
        return False, "Contacto no encontrado"
    
    # Check if already converted
    cursor.execute('SELECT converted_to_user FROM contacts WHERE id = ?', (contact_id,))
    if cursor.fetchone()[0] == 1:
        conn.close()
        return False, "Este contacto ya fue convertido a usuario"
    
    conn.close()
    return True, contact

def create_user_from_contact(contact_id, username, password, partner_id):
    """Create a new user from validated contact"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Get contact info
        cursor.execute('SELECT name, email, company FROM contacts WHERE id = ?', (contact_id,))
        contact = cursor.fetchone()
        
        if not contact:
            conn.close()
            return False, "Contacto no encontrado"
        
        # Check if username already exists
        cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return False, f"El username '{username}' ya está en uso. Intenta con otro nombre de usuario."
        
        # Check if email already exists (if email column exists)
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        if 'email' in columns and contact[1]:
            cursor.execute('SELECT id FROM users WHERE email = ?', (contact[1],))
            if cursor.fetchone():
                conn.close()
                return False, f"El email '{contact[1]}' ya está registrado en otro usuario."
        
        # Check if contact is validated
        cursor.execute('SELECT validated, converted_to_user FROM contacts WHERE id = ?', (contact_id,))
        validation_status = cursor.fetchone()
        
        if not validation_status or validation_status[0] != 1:
            conn.close()
            return False, "El contacto debe estar validado antes de convertirlo a usuario"
        
        if validation_status[1] == 1:
            conn.close()
            return False, "Este contacto ya fue convertido a usuario"
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Get the 'cliente' role_id for the new user
        cursor.execute("SELECT id FROM roles WHERE name = 'cliente'")
        cliente_role = cursor.fetchone()
        cliente_role_id = cliente_role[0] if cliente_role else None
        
        # Build dynamic INSERT query based on available columns
        insert_columns = ['username']
        insert_values = [username]
        
        # Add password (check for both 'password' and 'password_hash')
        if 'password' in columns:
            insert_columns.append('password')
            insert_values.append(hashed_password)
            print("DEBUG: Adding password column")
        elif 'password_hash' in columns:
            insert_columns.append('password_hash')
            insert_values.append(hashed_password)
            print("DEBUG: Adding password_hash column")
        else:
            print("WARNING: No password column found in users table")
        
        # Add email if column exists
        if 'email' in columns and contact[1]:
            insert_columns.append('email')
            insert_values.append(contact[1])
            print(f"DEBUG: Adding email: {contact[1]}")
        
        # Add role_id if column exists (CRITICAL for authentication)
        if 'role_id' in columns and cliente_role_id:
            insert_columns.append('role_id')
            insert_values.append(cliente_role_id)
            print(f"DEBUG: Adding role_id: {cliente_role_id}")
        
        # Add role if column exists
        if 'role' in columns:
            insert_columns.append('role')
            insert_values.append('cliente')
            print("DEBUG: Adding role: cliente")
        
        # Add status if column exists
        if 'status' in columns:
            insert_columns.append('status')
            insert_values.append('active')
            print("DEBUG: Adding status: active")
        
        # Add is_active if column exists
        if 'is_active' in columns:
            insert_columns.append('is_active')
            insert_values.append(1)
            print("DEBUG: Adding is_active: 1")
        
        # Add created_by_partner_id if column exists
        if 'created_by_partner_id' in columns:
            insert_columns.append('created_by_partner_id')
            insert_values.append(partner_id)
            print(f"DEBUG: Adding created_by_partner_id: {partner_id}")
        
        # Build and execute INSERT query
        columns_str = ', '.join(insert_columns)
        placeholders = ', '.join(['?' for _ in insert_values])
        query = f'INSERT INTO users ({columns_str}) VALUES ({placeholders})'
        
        print(f"DEBUG: Executing query: {query}")
        print(f"DEBUG: With values: {insert_values}")
        
        cursor.execute(query, insert_values)
        new_user_id = cursor.lastrowid
        
        print(f"DEBUG: User created with ID: {new_user_id}")
        
        if new_user_id == 0:
            conn.rollback()
            conn.close()
            return False, "Error: No se pudo crear el usuario (ID = 0)"
        
        # Update contact as converted
        cursor.execute('''
            UPDATE contacts 
            SET converted_to_user = 1, converted_user_id = ?, conversion_date = ?
            WHERE id = ?
        ''', (new_user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), contact_id))
        
        print(f"DEBUG: Contact updated as converted")
        
        # Verify the user was created
        cursor.execute('SELECT username, email FROM users WHERE id = ?', (new_user_id,))
        created_user = cursor.fetchone()
        
        if not created_user:
            conn.rollback()
            conn.close()
            return False, "Error: El usuario no se encontró después de crearlo"
        
        print(f"DEBUG: User verified - Username: {created_user[0]}, Email: {created_user[1]}")
        
        conn.commit()
        print(f"DEBUG: Transaction committed successfully")
        conn.close()
        
        success_message = f"""✅ Usuario creado exitosamente!

**Credenciales de acceso:**
- 👤 Usuario: `{username}`
- 📧 Email: `{created_user[1] if len(created_user) > 1 else 'N/A'}`
- 🆔 ID: {new_user_id}
- 🔐 Contraseña: (la que ingresaste)

El usuario ya puede iniciar sesión con estas credenciales."""
        
        return True, success_message
    
    except sqlite3.IntegrityError as e:
        conn.rollback()
        conn.close()
        error_msg = str(e).lower()
        print(f"ERROR IntegrityError: {e}")
        if 'username' in error_msg or 'unique' in error_msg:
            return False, f"El nombre de usuario '{username}' ya existe. Intenta con otro."
        elif 'email' in error_msg:
            return False, f"El email '{contact[1]}' ya está registrado."
        else:
            return False, f"Error de integridad: {str(e)}"
    except Exception as e:
        conn.rollback()
        conn.close()
        print(f"ERROR Exception: {e}")
        import traceback
        traceback.print_exc()
        return False, f"Error al crear usuario: {str(e)}"

# --- CLIENT SUB-BCS MANAGEMENT ---
def show_client_bcs_management(partner_id):
    st.subheader("🏢 Sub-BCS de Clientes")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nuevo Sub-BCS Cliente", use_container_width=True):
            st.session_state.show_add_client_bcs = True
    
    # Add new client BCS form
    if st.session_state.get('show_add_client_bcs', False):
        with st.form("add_client_bcs_form"):
            st.markdown("### Registrar Sub-BCS de Cliente")
            
            # Get contacts for selection
            conn = get_db_connection()
            contacts = pd.read_sql_query('''
                SELECT id, name, company FROM contacts 
                WHERE partner_id = ? AND status = 'active'
            ''', conn, params=(partner_id,))
            conn.close()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if not contacts.empty:
                    contact_options = {f"{row['name']} - {row['company']}": row['id'] 
                                     for _, row in contacts.iterrows()}
                    selected_contact = st.selectbox("Contacto/Cliente *", list(contact_options.keys()))
                    contact_id = contact_options[selected_contact]
                else:
                    st.warning("Debes agregar contactos primero")
                    contact_id = None
                
                client_name = st.text_input("Nombre del Cliente *")
                company_name = st.text_input("Empresa *")
                bcs_type = st.selectbox("Tipo de BCS *", [
                    "Hospitalario", "Pesquero", "Industrial", "Comercial", 
                    "Educativo", "Logístico", "Otro"
                ])
            
            with col2:
                users_count = st.number_input("Cantidad de Usuarios", min_value=1, value=1)
                monthly_value = st.number_input("Valor Mensual ($)", min_value=0.0, value=0.0)
                start_date = st.date_input("Fecha de Inicio")
                status = st.selectbox("Estado", ["active", "inactive", "trial"])
            
            modules = st.text_area("Módulos Incluidos", placeholder="Ej: Gestión de usuarios, Reportes, CRM...")
            notes = st.text_area("Notas Adicionales")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Guardar Sub-BCS", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted and contact_id:
                if client_name and company_name and bcs_type:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO client_sub_bcs 
                        (partner_id, contact_id, client_name, company_name, bcs_type, modules, 
                         users_count, status, start_date, monthly_value, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (partner_id, contact_id, client_name, company_name, bcs_type, modules,
                          users_count, status, start_date, monthly_value, notes))
                    conn.commit()
                    conn.close()
                    st.success("✅ Sub-BCS registrado exitosamente")
                    st.session_state.show_add_client_bcs = False
                    st.rerun()
                else:
                    st.error("Completa los campos obligatorios")
            
            if cancel:
                st.session_state.show_add_client_bcs = False
                st.rerun()
    
    # List client BCS from both tables
    conn = get_db_connection()
    
    # Get from client_sub_bcs (CRM managed)
    client_bcs = pd.read_sql_query('''
        SELECT cb.*, c.name as contact_name, 'CRM' as source
        FROM client_sub_bcs cb
        LEFT JOIN contacts c ON cb.contact_id = c.id
        WHERE cb.partner_id = ?
        ORDER BY cb.created_at DESC
    ''', conn, params=(partner_id,))
    
    # Get from user_sub_bcs (apps assigned by admin)
    user_apps = pd.read_sql_query('''
        SELECT 
            ubs.id,
            ubs.app_name as client_name,
            u.username as company_name,
            ubs.app_type as bcs_type,
            ubs.status,
            ubs.created_at,
            ubs.app_url as modules,
            ubs.app_description as notes,
            NULL as contact_name,
            0 as monthly_value,
            0 as users_count,
            NULL as start_date,
            'User Apps' as source
        FROM user_sub_bcs ubs
        JOIN users u ON ubs.user_id = u.id
        WHERE ubs.partner_id = ?
        ORDER BY ubs.created_at DESC
    ''', conn, params=(partner_id,))
    
    # Combine both sources
    if not user_apps.empty:
        if not client_bcs.empty:
            client_bcs = pd.concat([client_bcs, user_apps], ignore_index=True)
        else:
            client_bcs = user_apps
    
    if not client_bcs.empty:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            status_filter = st.selectbox("Estado", ["Todos", "active", "inactive", "trial"], key="client_bcs_status")
        with col2:
            type_filter = st.selectbox("Tipo BCS", ["Todos"] + list(client_bcs['bcs_type'].unique()))
        with col3:
            search = st.text_input("🔍 Buscar", placeholder="Cliente o empresa...", key="client_bcs_search")
        
        # Apply filters
        filtered_bcs = client_bcs.copy()
        if status_filter != "Todos":
            filtered_bcs = filtered_bcs[filtered_bcs['status'] == status_filter]
        if type_filter != "Todos":
            filtered_bcs = filtered_bcs[filtered_bcs['bcs_type'] == type_filter]
        if search:
            filtered_bcs = filtered_bcs[
                filtered_bcs['client_name'].str.contains(search, case=False, na=False) |
                filtered_bcs['company_name'].str.contains(search, case=False, na=False)
            ]
        
        st.markdown(f"**Total: {len(filtered_bcs)} Sub-BCS de Clientes**")
        
        # Display BCS
        for _, bcs in filtered_bcs.iterrows():
            status_emoji = {"active": "✅", "inactive": "❌", "trial": "🔄"}.get(bcs['status'], "❓")
            source_emoji = "📱" if bcs['source'] == 'User Apps' else "📊"
            
            # Different display based on source
            if bcs['source'] == 'User Apps':
                title = f"{status_emoji} {source_emoji} {bcs['client_name']} - {bcs['bcs_type']} | Usuario: {bcs['company_name']}"
            else:
                title = f"{status_emoji} {source_emoji} {bcs['client_name']} - {bcs['bcs_type']} | ${bcs['monthly_value']:,.0f}/mes"
            
            with st.expander(title):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**🏷️ Origen:** {bcs['source']}")
                    st.write(f"**Cliente/App:** {bcs['client_name']}")
                    st.write(f"**Tipo:** {bcs['bcs_type'] or 'N/A'}")
                
                with col2:
                    if bcs['source'] == 'User Apps':
                        st.write(f"**👤 Usuario:** {bcs['company_name']}")
                        st.write(f"**🔗 URL:** {bcs['modules']}")
                    else:
                        st.write(f"**Empresa:** {bcs['company_name']}")
                        st.write(f"**Contacto:** {bcs['contact_name']}")
                        st.write(f"**Usuarios:** {bcs['users_count']}")
                
                with col3:
                    st.write(f"**📊 Estado:** {bcs['status']}")
                    if bcs['source'] != 'User Apps':
                        st.write(f"**💰 Valor Mensual:** ${bcs['monthly_value']:,.0f}")
                        st.write(f"**📅 Inicio:** {bcs['start_date'] or 'N/A'}")
                    st.write(f"**🕐 Creado:** {bcs['created_at'][:10]}")
                
                if bcs['notes']:
                    st.write(f"**📝 Notas:** {bcs['notes']}")
                
                if bcs['source'] != 'User Apps' and bcs['modules']:
                    st.write(f"**⚙️ Módulos:** {bcs['modules']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🗑️ Eliminar", key=f"delete_client_bcs_{bcs['source']}_{bcs['id']}"):
                        cursor = conn.cursor()
                        if bcs['source'] == 'User Apps':
                            cursor.execute('DELETE FROM user_sub_bcs WHERE id = ?', (bcs['id'],))
                        else:
                            cursor.execute('DELETE FROM client_sub_bcs WHERE id = ?', (bcs['id'],))
                        conn.commit()
                        st.success("Sub-BCS eliminado")
                        st.rerun()
                
                with col2:
                    new_status = "inactive" if bcs['status'] == "active" else "active"
                    if st.button(f"🔄 Cambiar a {new_status}", key=f"toggle_client_bcs_{bcs['source']}_{bcs['id']}"):
                        cursor = conn.cursor()
                        if bcs['source'] == 'User Apps':
                            cursor.execute('UPDATE user_sub_bcs SET status = ? WHERE id = ?', (new_status, bcs['id']))
                        else:
                            cursor.execute('UPDATE client_sub_bcs SET status = ? WHERE id = ?', (new_status, bcs['id']))
                        conn.commit()
                        st.success(f"Estado actualizado")
                        st.rerun()
    else:
        st.info("No tienes Sub-BCS de clientes registrados.")
    
    conn.close()

# --- PARTNER SUB-BCS MANAGEMENT ---
def show_partner_bcs_management(partner_id):
    st.subheader("🔧 Sub-BCS Propios")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nuevo Sub-BCS Propio", use_container_width=True):
            st.session_state.show_add_partner_bcs = True
    
    # Add new partner BCS form
    if st.session_state.get('show_add_partner_bcs', False):
        with st.form("add_partner_bcs_form"):
            st.markdown("### Crear Sub-BCS Propio")
            
            col1, col2 = st.columns(2)
            
            with col1:
                bcs_name = st.text_input("Nombre del BCS *")
                bcs_type = st.selectbox("Tipo de BCS *", [
                    "Herramienta Interna", "Demo", "Plantilla", "Proyecto Personal", "Otro"
                ])
            
            with col2:
                status = st.selectbox("Estado", ["active", "inactive", "development"])
                modules = st.text_input("Módulos Principales")
            
            description = st.text_area("Descripción")
            notes = st.text_area("Notas Técnicas")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Guardar Sub-BCS", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                if bcs_name and bcs_type:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO partner_sub_bcs 
                        (partner_id, bcs_name, bcs_type, description, modules, status, notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (partner_id, bcs_name, bcs_type, description, modules, status, notes))
                    conn.commit()
                    conn.close()
                    st.success("✅ Sub-BCS propio creado exitosamente")
                    st.session_state.show_add_partner_bcs = False
                    st.rerun()
                else:
                    st.error("Completa los campos obligatorios")
            
            if cancel:
                st.session_state.show_add_partner_bcs = False
                st.rerun()
    
    # List partner BCS
    conn = get_db_connection()
    partner_bcs = pd.read_sql_query('''
        SELECT * FROM partner_sub_bcs
        WHERE partner_id = ?
        ORDER BY created_at DESC
    ''', conn, params=(partner_id,))
    
    if not partner_bcs.empty:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Estado", ["Todos", "active", "inactive", "development"], key="partner_bcs_status")
        with col2:
            type_filter = st.selectbox("Tipo", ["Todos"] + list(partner_bcs['bcs_type'].unique()))
        
        # Apply filters
        filtered_bcs = partner_bcs.copy()
        if status_filter != "Todos":
            filtered_bcs = filtered_bcs[filtered_bcs['status'] == status_filter]
        if type_filter != "Todos":
            filtered_bcs = filtered_bcs[filtered_bcs['bcs_type'] == type_filter]
        
        st.markdown(f"**Total: {len(filtered_bcs)} Sub-BCS Propios**")
        
        # Display BCS
        for _, bcs in filtered_bcs.iterrows():
            status_emoji = {"active": "✅", "inactive": "❌", "development": "🚧"}.get(bcs['status'], "❓")
            
            with st.expander(f"{status_emoji} {bcs['bcs_name']} - {bcs['bcs_type']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Tipo:** {bcs['bcs_type']}")
                    st.write(f"**Estado:** {bcs['status']}")
                    if bcs['modules']:
                        st.write(f"**Módulos:** {bcs['modules']}")
                
                with col2:
                    st.write(f"**Creado:** {bcs['created_at'][:10]}")
                
                if bcs['description']:
                    st.write(f"**Descripción:** {bcs['description']}")
                
                if bcs['notes']:
                    st.write(f"**Notas:** {bcs['notes']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🗑️ Eliminar", key=f"delete_partner_bcs_{bcs['id']}"):
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM partner_sub_bcs WHERE id = ?', (bcs['id'],))
                        conn.commit()
                        st.success("Sub-BCS eliminado")
                        st.rerun()
                
                with col2:
                    if st.button(f"📝 Editar Estado", key=f"edit_partner_bcs_{bcs['id']}"):
                        st.session_state[f'edit_bcs_{bcs["id"]}'] = True
    else:
        st.info("No tienes Sub-BCS propios registrados.")
    
    conn.close()

# --- ACTIVITIES MANAGEMENT ---
def show_activities_management(partner_id):
    st.subheader("📝 Gestión de Actividades")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("➕ Nueva Actividad", use_container_width=True):
            st.session_state.show_add_activity = True
    
    # Add new activity form
    if st.session_state.get('show_add_activity', False):
        with st.form("add_activity_form"):
            st.markdown("### Registrar Nueva Actividad")
            
            # Get contacts for selection
            conn = get_db_connection()
            contacts = pd.read_sql_query('''
                SELECT id, name, company, validated FROM contacts 
                WHERE partner_id = ? AND status = 'active'
            ''', conn, params=(partner_id,))
            conn.close()
            
            col1, col2 = st.columns(2)
            
            with col1:
                activity_type = st.selectbox("Tipo de Actividad *", [
                    "Validación de Cliente",
                    "Llamada", 
                    "Reunión", 
                    "Email", 
                    "Demo", 
                    "Seguimiento", 
                    "Otro"
                ])
                subject = st.text_input("Asunto *")
                
                if not contacts.empty:
                    contact_options = {}
                    for _, row in contacts.iterrows():
                        label = f"{row['name']} - {row['company']}"
                        if row['validated']:
                            label += " ✅"
                        contact_options[label] = row['id']
                    contact_options["Ninguno"] = None
                    selected_contact = st.selectbox("Contacto", list(contact_options.keys()))
                    contact_id = contact_options[selected_contact]
                else:
                    contact_id = None
                    st.info("No hay contactos disponibles")
            
            with col2:
                activity_date = st.date_input("Fecha de Actividad", value=date.today())
                follow_up_date = st.date_input("Fecha de Seguimiento", value=None)
                completed = st.checkbox("Completada")
            
            description = st.text_area("Descripción")
            
            # Show validation option if activity is "Validación de Cliente"
            validation_successful = False
            if activity_type == "Validación de Cliente":
                st.info("🔔 Esta actividad puede validar al contacto para convertirlo en usuario")
                validation_successful = st.checkbox("✅ Validación exitosa (el contacto aceptó por email)")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Guardar Actividad", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submitted:
                if activity_type and subject:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO partner_activities 
                        (partner_id, contact_id, activity_type, subject, description, 
                         activity_date, follow_up_date, completed)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (partner_id, contact_id, activity_type, subject, description,
                          activity_date, follow_up_date, 1 if completed else 0))
                    
                    # If validation successful, update contact
                    if validation_successful and contact_id and completed:
                        cursor.execute('''
                            UPDATE contacts 
                            SET validated = 1, validation_date = ?
                            WHERE id = ?
                        ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), contact_id))
                        st.success("✅ Contacto validado exitosamente - Ahora puedes convertirlo a usuario")
                    
                    conn.commit()
                    conn.close()
                    st.success("✅ Actividad registrada exitosamente")
                    st.session_state.show_add_activity = False
                    st.rerun()
                else:
                    st.error("Completa los campos obligatorios")
            
            if cancel:
                st.session_state.show_add_activity = False
                st.rerun()
    
    # List activities
    conn = get_db_connection()
    activities = pd.read_sql_query('''
        SELECT pa.*, c.name as contact_name, c.company as contact_company, c.validated
        FROM partner_activities pa
        LEFT JOIN contacts c ON pa.contact_id = c.id
        WHERE pa.partner_id = ?
        ORDER BY pa.activity_date DESC
    ''', conn, params=(partner_id,))
    
    if not activities.empty:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            completed_filter = st.selectbox("Estado", ["Todas", "Pendientes", "Completadas"])
        with col2:
            type_filter = st.selectbox("Tipo", ["Todos"] + list(activities['activity_type'].unique()))
        with col3:
            search = st.text_input("🔍 Buscar", placeholder="Asunto...", key="activity_search")
        
        # Apply filters
        filtered_activities = activities.copy()
        if completed_filter == "Pendientes":
            filtered_activities = filtered_activities[filtered_activities['completed'] == 0]
        elif completed_filter == "Completadas":
            filtered_activities = filtered_activities[filtered_activities['completed'] == 1]
        
        if type_filter != "Todos":
            filtered_activities = filtered_activities[filtered_activities['activity_type'] == type_filter]
        
        if search:
            filtered_activities = filtered_activities[
                filtered_activities['subject'].str.contains(search, case=False, na=False)
            ]
        
        st.markdown(f"**Total: {len(filtered_activities)} actividades**")
        
        # Display activities
        for _, activity in filtered_activities.iterrows():
            status_emoji = "✅" if activity['completed'] else "⏳"
            validation_emoji = "🔔" if activity['activity_type'] == "Validación de Cliente" else ""
            validated_emoji = "✅" if activity.get('validated', 0) == 1 else ""
            
            with st.expander(f"{status_emoji} {validation_emoji} {activity['activity_type']} - {activity['subject']} | {activity['activity_date']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Tipo:** {activity['activity_type']}")
                    st.write(f"**Contacto:** {activity['contact_name'] or 'N/A'} {validated_emoji}")
                    if activity['contact_company']:
                        st.write(f"**Empresa:** {activity['contact_company']}")
                
                with col2:
                    st.write(f"**Fecha:** {activity['activity_date']}")
                    if activity['follow_up_date']:
                        st.write(f"**Seguimiento:** {activity['follow_up_date']}")
                    st.write(f"**Estado:** {'Completada' if activity['completed'] else 'Pendiente'}")
                
                if activity['description']:
                    st.write(f"**Descripción:** {activity['description']}")
                
                if activity['activity_type'] == "Validación de Cliente" and activity.get('validated', 0) == 1:
                    st.success("✅ Esta actividad validó al contacto para conversión a usuario")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"🗑️ Eliminar", key=f"delete_activity_{activity['id']}"):
                        cursor = conn.cursor()
                        cursor.execute('DELETE FROM partner_activities WHERE id = ?', (activity['id'],))
                        conn.commit()
                        st.success("Actividad eliminada")
                        st.rerun()
                
                with col2:
                    new_status = 0 if activity['completed'] else 1
                    status_text = "Pendiente" if activity['completed'] else "Completada"
                    if st.button(f"✓ Marcar como {status_text}", key=f"toggle_activity_{activity['id']}"):
                        cursor = conn.cursor()
                        cursor.execute('UPDATE partner_activities SET completed = ? WHERE id = ?', 
                                     (new_status, activity['id']))
                        conn.commit()
                        st.success(f"Actividad marcada como {status_text}")
                        st.rerun()
    else:
        st.info("No tienes actividades registradas.")
    
    conn.close()

def logout():
    """Logout function"""
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_data = None
    st.rerun()
