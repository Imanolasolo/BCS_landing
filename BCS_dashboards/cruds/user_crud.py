import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

class UserCRUD:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_all_users(self):
        """Get all users with their roles - NOW INCLUDES USERS WITHOUT role_id"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Changed INNER JOIN to LEFT JOIN to include users without role_id
        cursor.execute('''
            SELECT 
                u.id, 
                u.username, 
                u.email, 
                COALESCE(r.name, u.role, 'Sin Rol') as role,
                u.created_at, 
                u.is_active,
                u.created_by_partner_id
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            ORDER BY u.created_at DESC
        ''')
        
        users = cursor.fetchall()
        conn.close()
        
        if users:
            df = pd.DataFrame(users, columns=[
                'ID', 'Usuario', 'Email', 'Rol', 'Fecha Registro', 'Activo', 'Creado Por Partner'
            ])
            return df
        return pd.DataFrame()
    
    def get_user_by_id(self, user_id):
        """Get user by ID - NOW WORKS WITH OR WITHOUT role_id"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                u.id, 
                u.username, 
                u.email, 
                u.role_id, 
                COALESCE(r.name, u.role, 'Sin Rol') as role, 
                u.is_active,
                u.created_by_partner_id
            FROM users u
            LEFT JOIN roles r ON u.role_id = r.id
            WHERE u.id = ?
        ''', (user_id,))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'role_id': user[3],
                'role': user[4],
                'is_active': user[5],
                'created_by_partner_id': user[6]
            }
        return None
    
    def get_roles(self):
        """Get all available roles"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, name, description FROM roles')
        roles = cursor.fetchall()
        conn.close()
        
        return {role[1]: role[0] for role in roles}  # {role_name: role_id}
    
    def update_user(self, user_id, username, email, role_id, is_active):
        """Update user information"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE users 
                SET username = ?, email = ?, role_id = ?, is_active = ?
                WHERE id = ?
            ''', (username, email, role_id, is_active, user_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "Usuario actualizado exitosamente"
            else:
                conn.close()
                return False, "Usuario no encontrado"
                
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Error: El nombre de usuario ya existe"
        except Exception as e:
            conn.close()
            return False, f"Error al actualizar usuario: {str(e)}"
    
    def delete_user(self, user_id):
        """Delete user (except admin)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check if it's the admin user
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if user and user[0] == 'admin':
            conn.close()
            return False, "No se puede eliminar el usuario administrador"
        
        try:
            cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "Usuario eliminado exitosamente"
            else:
                conn.close()
                return False, "Usuario no encontrado"
                
        except Exception as e:
            conn.close()
            return False, f"Error al eliminar usuario: {str(e)}"
    
    def get_user_stats(self):
        """Get user statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM users')
        total = cursor.fetchone()[0]
        
        # Active users
        cursor.execute('SELECT COUNT(*) FROM users WHERE is_active = 1')
        active = cursor.fetchone()[0]
        
        # Users by role
        cursor.execute('''
            SELECT r.name, COUNT(*) 
            FROM users u 
            JOIN roles r ON u.role_id = r.id 
            GROUP BY r.name
        ''')
        by_role = cursor.fetchall()
        
        conn.close()
        
        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'by_role': dict(by_role)
        }

def render_user_crud(db):
    """Render the complete user CRUD interface"""
    user_crud = UserCRUD(db)
    
    # Tabs for different operations
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista", "➕ Crear", "✏️ Editar", "📊 Estadísticas"])
    
    with tab1:
        render_user_list(user_crud, db)
    
    with tab2:
        render_create_user(user_crud, db)
    
    with tab3:
        render_edit_user(user_crud)
    
    with tab4:
        render_user_stats(user_crud)

def render_user_list(user_crud, db):
    """Render user list with search and filter"""
    st.subheader("📋 Lista de Usuarios")
    
    # Get all users
    df = user_crud.get_all_users()
    
    if not df.empty:
        # Add badge for partner-created users
        df['Origen'] = df.apply(
            lambda row: '🤝 Por Partner' if pd.notna(row['Creado Por Partner']) else '🛠️ Sistema',
            axis=1
        )
        
        # Display summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Total Usuarios", len(df))
        with col2:
            active_count = len(df[df['Activo'] == 1])
            st.metric("✅ Activos", active_count)
        with col3:
            partner_created = len(df[df['Creado Por Partner'].notna()])
            st.metric("🤝 Creados por Partners", partner_created)
        
        st.markdown("---")
        
        # Search functionality
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_term = st.text_input("🔍 Buscar por usuario o email:")
        
        with col2:
            # Filter by role
            all_roles = ["Todos"] + sorted(df['Rol'].unique().tolist())
            role_filter = st.selectbox("Filtrar por rol:", all_roles)
        
        with col3:
            # Filter by origin
            origin_filter = st.selectbox("Filtrar por origen:", ["Todos", "Sistema", "Por Partners"])
        
        # Apply filters
        filtered_df = df.copy()
        
        if search_term:
            mask = filtered_df['Usuario'].str.contains(search_term, case=False, na=False) | \
                   filtered_df['Email'].str.contains(search_term, case=False, na=False)
            filtered_df = filtered_df[mask]
        
        if role_filter != "Todos":
            filtered_df = filtered_df[filtered_df['Rol'] == role_filter]
        
        if origin_filter == "Sistema":
            filtered_df = filtered_df[filtered_df['Creado Por Partner'].isna()]
        elif origin_filter == "Por Partners":
            filtered_df = filtered_df[filtered_df['Creado Por Partner'].notna()]
        
        # Display count
        st.markdown(f"**Mostrando {len(filtered_df)} de {len(df)} usuarios**")
        
        # Display dataframe (without internal columns)
        display_df = filtered_df[['ID', 'Usuario', 'Email', 'Rol', 'Origen', 'Fecha Registro', 'Activo']]
        st.dataframe(display_df, use_container_width=True)
        
        # Expandable details for each user
        st.markdown("---")
        st.subheader("🔍 Detalles de Usuarios")
        
        for _, user in filtered_df.iterrows():
            with st.expander(f"{'✅' if user['Activo'] else '❌'} {user['Usuario']} - {user['Rol']} | {user['Origen']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**🆔 ID:** {user['ID']}")
                    st.write(f"**👤 Usuario:** {user['Usuario']}")
                    st.write(f"**📧 Email:** {user['Email'] or 'N/A'}")
                
                with col2:
                    st.write(f"**🎭 Rol:** {user['Rol']}")
                    st.write(f"**✅ Activo:** {'Sí' if user['Activo'] else 'No'}")
                    st.write(f"**🏷️ Origen:** {user['Origen']}")
                
                with col3:
                    st.write(f"**📅 Registrado:** {user['Fecha Registro'][:10]}")
                    if pd.notna(user['Creado Por Partner']):
                        st.write(f"**🤝 Partner ID:** {user['Creado Por Partner']}")
                
                # Action buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    if user['Usuario'] != 'admin':  # Protect admin
                        if st.button(f"🗑️ Eliminar", key=f"delete_user_list_{user['ID']}"):
                            success, message = user_crud.delete_user(user['ID'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                    else:
                        st.caption("👑 Usuario protegido")
                
                with col2:
                    # Toggle active status
                    new_status = 0 if user['Activo'] else 1
                    status_text = "Desactivar" if user['Activo'] else "Activar"
                    if st.button(f"🔄 {status_text}", key=f"toggle_user_list_{user['ID']}"):
                        # Update status
                        conn = user_crud.db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute('UPDATE users SET is_active = ? WHERE id = ?', (new_status, user['ID']))
                        conn.commit()
                        conn.close()
                        st.success(f"Usuario {status_text.lower()}do")
                        st.rerun()
        
        # Delete functionality (legacy - now in expanders)
        if False:  # Disabled, now in expanders
            st.markdown("---")
            st.subheader("🗑️ Eliminar Usuario")
            
            user_to_delete = st.selectbox(
                "Seleccionar usuario a eliminar:",
                options=filtered_df['ID'].tolist(),
                format_func=lambda x: f"ID: {x} - {filtered_df[filtered_df['ID']==x]['Usuario'].iloc[0]} ({filtered_df[filtered_df['ID']==x]['Rol'].iloc[0]})"
            )
            
            if st.button("🗑️ Eliminar Usuario", type="secondary"):
                success, message = user_crud.delete_user(user_to_delete)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    else:
        st.info("No hay usuarios registrados en el sistema.")

def render_create_user(user_crud, db):
    """Render create user form"""
    st.subheader("➕ Crear Nuevo Usuario")
    
    roles = user_crud.get_roles()
    
    with st.form("create_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Usuario *", placeholder="Nombre de usuario")
            email = st.text_input("Email *", placeholder="usuario@email.com")
        
        with col2:
            role = st.selectbox("Rol *", options=list(roles.keys()))
            
        st.markdown("---")
        st.subheader("🔐 Credenciales de Acceso")
        
        col_pass1, col_pass2 = st.columns(2)
        with col_pass1:
            password = st.text_input("Contraseña *", type="password", placeholder="Contraseña")
        with col_pass2:
            confirm_password = st.text_input("Confirmar Contraseña *", type="password", placeholder="Confirmar contraseña")
        
        submit = st.form_submit_button("✅ Crear Usuario", use_container_width=True)
        
        if submit:
            if username and email and password and role and confirm_password:
                # Password validation
                if password != confirm_password:
                    st.error("Las contraseñas no coinciden")
                    return
                if len(password) < 6:
                    st.error("La contraseña debe tener al menos 6 caracteres")
                    return
                
                success, message = db.create_user(username, password, role, email)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Por favor complete todos los campos obligatorios (*)")

def render_edit_user(user_crud):
    """Render edit user form"""
    st.subheader("✏️ Editar Usuario")
    
    # Get all users for selection
    df = user_crud.get_all_users()
    
    if not df.empty:
        user_id = st.selectbox(
            "Seleccionar usuario a editar:",
            options=df['ID'].tolist(),
            format_func=lambda x: f"ID: {x} - {df[df['ID']==x]['Usuario'].iloc[0]} ({df[df['ID']==x]['Rol'].iloc[0]})"
        )
        
        if user_id:
            user_data = user_crud.get_user_by_id(user_id)
            roles = user_crud.get_roles()
            
            if user_data:
                with st.form("edit_user_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        username = st.text_input("Usuario *", value=user_data['username'])
                        email = st.text_input("Email *", value=user_data['email'] or "")
                    
                    with col2:
                        role = st.selectbox("Rol *", options=list(roles.keys()),
                                          index=list(roles.keys()).index(user_data['role']))
                        is_active = st.checkbox("Usuario Activo", value=bool(user_data['is_active']))
                    
                    submit = st.form_submit_button("💾 Actualizar Usuario", use_container_width=True)
                    
                    if submit:
                        if username and email and role:
                            role_id = roles[role]
                            success, message = user_crud.update_user(
                                user_id, username, email, role_id, is_active
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Por favor complete todos los campos obligatorios (*)")
    else:
        st.info("No hay usuarios registrados para editar.")

def render_user_stats(user_crud):
    """Render user statistics"""
    st.subheader("📊 Estadísticas de Usuarios")
    
    stats = user_crud.get_user_stats()
    df = user_crud.get_all_users()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Total Usuarios",
            value=stats['total']
        )
    
    with col2:
        st.metric(
            label="✅ Usuarios Activos",
            value=stats['active']
        )
    
    with col3:
        st.metric(
            label="❌ Usuarios Inactivos",
            value=stats['inactive']
        )
    
    with col4:
        if not df.empty:
            partner_created = len(df[df['Creado Por Partner'].notna()])
            st.metric(
                label="🤝 Por Partners",
                value=partner_created
            )
        else:
            st.metric(
                label="🤝 Por Partners",
                value=0
            )
    
    # Users by role
    if stats['by_role']:
        st.markdown("---")
        st.subheader("👤 Usuarios por Rol")
        
        role_cols = st.columns(len(stats['by_role']))
        
        for i, (role, count) in enumerate(stats['by_role'].items()):
            with role_cols[i]:
                st.metric(
                    label=f"🎭 {role.title()}",
                    value=count
                )
    
    # Users created by partners
    if not df.empty:
        partner_users = df[df['Creado Por Partner'].notna()]
        if not partner_users.empty:
            st.markdown("---")
            st.subheader("🤝 Usuarios Creados por Partners")
            st.dataframe(
                partner_users[['Usuario', 'Email', 'Rol', 'Creado Por Partner', 'Fecha Registro']],
                use_container_width=True
            )
    
    # Recent users
    if stats['total'] > 0:
        st.markdown("---")
        if not df.empty:
            st.subheader("🕒 Usuarios Registrados Recientemente")
            recent_users = df.head(10)[['Usuario', 'Email', 'Rol', 'Origen', 'Fecha Registro']]
            st.dataframe(recent_users, use_container_width=True)
