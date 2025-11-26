import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

class PartnerCRUD:
    def __init__(self, db_connection):
        self.db = db_connection
        self.init_partner_table()
    
    def init_partner_table(self):
        """Initialize partners table if it doesn't exist"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='partners'")
        table_exists = cursor.fetchone()
        
        if table_exists:
            # Check if user_id column exists
            cursor.execute("PRAGMA table_info(partners)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'user_id' not in columns:
                # Add user_id column to existing table
                try:
                    cursor.execute('ALTER TABLE partners ADD COLUMN user_id INTEGER')
                    cursor.execute('ALTER TABLE partners ADD FOREIGN KEY (user_id) REFERENCES users (id)')
                    conn.commit()
                except Exception as e:
                    # SQLite doesn't support adding foreign keys to existing tables easily
                    # So we just add the column
                    pass
        else:
            # Create new table with all columns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS partners (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    empresa TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    telefono TEXT,
                    direccion TEXT,
                    estado TEXT DEFAULT 'activo',
                    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notas TEXT,
                    user_id INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            conn.commit()
        
        conn.close()
    
    def create_partner(self, nombre, empresa, email, telefono=None, direccion=None, notas=None, username=None, password=None):
        """Create a new partner with optional user account"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            user_id = None
            
            # If username and password provided, create user account
            if username and password:
                # Get partner role ID
                cursor.execute('SELECT id FROM roles WHERE name = ?', ('partner',))
                partner_role = cursor.fetchone()
                
                if partner_role:
                    password_hash = self.db.hash_password(password)
                    cursor.execute('''
                        INSERT INTO users (username, password_hash, role_id, email)
                        VALUES (?, ?, ?, ?)
                    ''', (username, password_hash, partner_role[0], email))
                    user_id = cursor.lastrowid
            
            # Create partner record
            cursor.execute('''
                INSERT INTO partners (nombre, empresa, email, telefono, direccion, notas, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, empresa, email, telefono, direccion, notas, user_id))
            
            partner_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            message = f"Partner creado exitosamente con ID: {partner_id}"
            if user_id:
                message += f"\n✅ Cuenta de acceso creada - Usuario: {username}"
            
            return True, message
            
        except sqlite3.IntegrityError as e:
            conn.close()
            if "username" in str(e).lower():
                return False, "Error: El nombre de usuario ya existe en el sistema"
            return False, "Error: El email ya existe en el sistema"
        except Exception as e:
            conn.close()
            return False, f"Error al crear partner: {str(e)}"
    
    def get_all_partners(self):
        """Get all partners with user account info"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.nombre, p.empresa, p.email, p.telefono, p.direccion, 
                   p.estado, p.fecha_registro, p.notas, u.username
            FROM partners p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.fecha_registro DESC
        ''')
        
        partners = cursor.fetchall()
        conn.close()
        
        if partners:
            df = pd.DataFrame(partners, columns=[
                'ID', 'Nombre', 'Empresa', 'Email', 'Teléfono', 
                'Dirección', 'Estado', 'Fecha Registro', 'Notas', 'Usuario Sistema'
            ])
            return df
        return pd.DataFrame()
    
    def get_partner_by_id(self, partner_id):
        """Get partner by ID with user account info"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.nombre, p.empresa, p.email, p.telefono, p.direccion, 
                   p.estado, p.fecha_registro, p.notas, p.user_id, u.username, u.is_active
            FROM partners p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.id = ?
        ''', (partner_id,))
        
        partner = cursor.fetchone()
        conn.close()
        
        if partner:
            return {
                'id': partner[0],
                'nombre': partner[1],
                'empresa': partner[2],
                'email': partner[3],
                'telefono': partner[4],
                'direccion': partner[5],
                'estado': partner[6],
                'fecha_registro': partner[7],
                'notas': partner[8],
                'user_id': partner[9],
                'username': partner[10],
                'user_active': partner[11] if partner[11] is not None else None
            }
        return None
    
    def update_partner(self, partner_id, nombre, empresa, email, telefono, direccion, estado, notas, 
                      username=None, password=None, user_active=None):
        """Update partner information and user account"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get current partner data
            cursor.execute('SELECT user_id FROM partners WHERE id = ?', (partner_id,))
            current_partner = cursor.fetchone()
            
            if not current_partner:
                conn.close()
                return False, "Partner no encontrado"
            
            current_user_id = current_partner[0]
            
            # Update or create user account
            if username:
                if current_user_id:
                    # Update existing user
                    if password:
                        password_hash = self.db.hash_password(password)
                        cursor.execute('''
                            UPDATE users 
                            SET username = ?, password_hash = ?, email = ?, is_active = ?
                            WHERE id = ?
                        ''', (username, password_hash, email, user_active if user_active is not None else 1, current_user_id))
                    else:
                        cursor.execute('''
                            UPDATE users 
                            SET username = ?, email = ?, is_active = ?
                            WHERE id = ?
                        ''', (username, email, user_active if user_active is not None else 1, current_user_id))
                else:
                    # Create new user account
                    if password:
                        cursor.execute('SELECT id FROM roles WHERE name = ?', ('partner',))
                        partner_role = cursor.fetchone()
                        
                        if partner_role:
                            password_hash = self.db.hash_password(password)
                            cursor.execute('''
                                INSERT INTO users (username, password_hash, role_id, email, is_active)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (username, password_hash, partner_role[0], email, user_active if user_active is not None else 1))
                            current_user_id = cursor.lastrowid
            
            # Update partner
            cursor.execute('''
                UPDATE partners 
                SET nombre = ?, empresa = ?, email = ?, telefono = ?, 
                    direccion = ?, estado = ?, notas = ?, user_id = ?
                WHERE id = ?
            ''', (nombre, empresa, email, telefono, direccion, estado, notas, current_user_id, partner_id))
            
            conn.commit()
            conn.close()
            return True, "Partner actualizado exitosamente"
                
        except sqlite3.IntegrityError as e:
            conn.close()
            if "username" in str(e).lower():
                return False, "Error: El nombre de usuario ya existe"
            return False, "Error: El email ya existe en el sistema"
        except Exception as e:
            conn.close()
            return False, f"Error al actualizar partner: {str(e)}"
    
    def delete_partner(self, partner_id):
        """Delete partner"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM partners WHERE id = ?', (partner_id,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "Partner eliminado exitosamente"
            else:
                conn.close()
                return False, "Partner no encontrado"
                
        except Exception as e:
            conn.close()
            return False, f"Error al eliminar partner: {str(e)}"
    
    def get_partner_stats(self):
        """Get partner statistics"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Total partners
        cursor.execute('SELECT COUNT(*) FROM partners')
        total = cursor.fetchone()[0]
        
        # Active partners
        cursor.execute("SELECT COUNT(*) FROM partners WHERE estado = 'activo'")
        active = cursor.fetchone()[0]
        
        # Inactive partners
        cursor.execute("SELECT COUNT(*) FROM partners WHERE estado = 'inactivo'")
        inactive = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'activos': active,
            'inactivos': inactive
        }
    
    def has_user_account(self, partner_email):
        """Check if partner has a user account"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM users WHERE email = ?', (partner_email,))
        user = cursor.fetchone()
        conn.close()
        
        return user is not None
    
    def create_user_account_for_partner(self, partner_email, password):
        """Create user account for existing partner"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if partner exists
            cursor.execute('SELECT id FROM partners WHERE email = ?', (partner_email,))
            partner = cursor.fetchone()
            
            if not partner:
                conn.close()
                return False, "Partner no encontrado"
            
            # Check if user already exists
            if self.has_user_account(partner_email):
                conn.close()
                return False, "El partner ya tiene una cuenta de usuario"
            
            # Get partner role ID
            cursor.execute('SELECT id FROM roles WHERE name = ?', ('partner',))
            partner_role = cursor.fetchone()
            
            if partner_role:
                password_hash = self.db.hash_password(password)
                cursor.execute('''
                    INSERT INTO users (username, password_hash, role_id, email)
                    VALUES (?, ?, ?, ?)
                ''', (partner_email, password_hash, partner_role[0], partner_email))
                
                conn.commit()
                conn.close()
                return True, f"Cuenta de usuario creada para {partner_email}"
            else:
                conn.close()
                return False, "Error: Rol de partner no encontrado"
                
        except sqlite3.IntegrityError:
            conn.close()
            return False, "Error: El email ya existe como usuario"
        except Exception as e:
            conn.close()
            return False, f"Error al crear cuenta: {str(e)}"

    def get_all_partners_with_account_status(self):
        """Get all partners with their user account status"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.id, p.nombre, p.empresa, p.email, p.telefono, p.direccion, 
                   p.estado, p.fecha_registro, p.notas,
                   CASE WHEN u.id IS NOT NULL THEN 'Sí' ELSE 'No' END as tiene_cuenta
            FROM partners p
            LEFT JOIN users u ON p.email = u.email
            ORDER BY p.fecha_registro DESC
        ''')
        
        partners = cursor.fetchall()
        conn.close()
        
        if partners:
            df = pd.DataFrame(partners, columns=[
                'ID', 'Nombre', 'Empresa', 'Email', 'Teléfono', 
                'Dirección', 'Estado', 'Fecha Registro', 'Notas', 'Tiene Cuenta'
            ])
            return df
        return pd.DataFrame()

def render_partner_crud(db):
    """Render the complete partner CRUD interface"""
    partner_crud = PartnerCRUD(db)
    
    # Tabs for different operations
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Lista", "➕ Crear", "✏️ Editar", "🔐 Cuentas", "📊 Estadísticas"])
    
    with tab1:
        render_partner_list(partner_crud)
    
    with tab2:
        render_create_partner(partner_crud)
    
    with tab3:
        render_edit_partner(partner_crud)
    
    with tab4:
        render_partner_accounts(partner_crud)
    
    with tab5:
        render_partner_stats(partner_crud)

def render_partner_list(partner_crud):
    """Render partner list with search and filter"""
    st.subheader("📋 Lista de Partners")
    
    # Get all partners with account status
    df = partner_crud.get_all_partners_with_account_status()
    
    if not df.empty:
        # Search functionality
        search_term = st.text_input("🔍 Buscar por nombre o empresa:")
        
        if search_term:
            mask = df['Nombre'].str.contains(search_term, case=False, na=False) | \
                   df['Empresa'].str.contains(search_term, case=False, na=False)
            df = df[mask]
        
        # Filter by status
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filtrar por estado:", ["Todos", "activo", "inactivo"])
        with col2:
            account_filter = st.selectbox("Filtrar por cuenta:", ["Todos", "Con cuenta", "Sin cuenta"])
        
        if status_filter != "Todos":
            df = df[df['Estado'] == status_filter]
        
        if account_filter == "Con cuenta":
            df = df[df['Tiene Cuenta'] == 'Sí']
        elif account_filter == "Sin cuenta":
            df = df[df['Tiene Cuenta'] == 'No']
        
        # Display dataframe
        st.dataframe(df, use_container_width=True)
        
        # Delete functionality
        if not df.empty:
            st.markdown("---")
            st.subheader("🗑️ Eliminar Partner")
            
            partner_to_delete = st.selectbox(
                "Seleccionar partner a eliminar:",
                options=df['ID'].tolist(),
                format_func=lambda x: f"ID: {x} - {df[df['ID']==x]['Nombre'].iloc[0]} ({df[df['ID']==x]['Empresa'].iloc[0]})"
            )
            
            if st.button("🗑️ Eliminar Partner", type="secondary"):
                success, message = partner_crud.delete_partner(partner_to_delete)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
    else:
        st.info("No hay partners registrados en el sistema.")

def render_create_partner(partner_crud):
    """Render create partner form"""
    st.subheader("➕ Crear Nuevo Partner")
    
    with st.form("create_partner_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre *", placeholder="Nombre completo del contacto")
            empresa = st.text_input("Empresa *", placeholder="Nombre de la empresa")
            email = st.text_input("Email *", placeholder="email@empresa.com")
        
        with col2:
            telefono = st.text_input("Teléfono", placeholder="+1234567890")
            direccion = st.text_area("Dirección", placeholder="Dirección completa")
        
        notas = st.text_area("Notas", placeholder="Notas adicionales sobre el partner")
        
        # Password section
        st.markdown("---")
        st.subheader("🔐 Acceso al Sistema")
        st.info("Cree una cuenta de acceso para que el partner pueda ingresar al sistema")
        create_account = st.checkbox("Crear cuenta de acceso para el partner", value=True)
        
        username = None
        password = None
        confirm_password = None
        
        if create_account:
            col_user, col_pass1, col_pass2 = st.columns(3)
            with col_user:
                username = st.text_input("Usuario *", placeholder="Nombre de usuario único")
            with col_pass1:
                password = st.text_input("Contraseña *", type="password", placeholder="Mínimo 6 caracteres")
            with col_pass2:
                confirm_password = st.text_input("Confirmar Contraseña *", type="password", placeholder="Repetir contraseña")
        
        submit = st.form_submit_button("✅ Crear Partner", use_container_width=True)
        
        if submit:
            if nombre and empresa and email:
                # Validate account creation if enabled
                if create_account:
                    if not username or not password or not confirm_password:
                        st.error("Por favor complete todos los campos de acceso (Usuario, Contraseña y Confirmar)")
                        return
                    if password != confirm_password:
                        st.error("❌ Las contraseñas no coinciden")
                        return
                    if len(password) < 6:
                        st.error("❌ La contraseña debe tener al menos 6 caracteres")
                        return
                
                success, message = partner_crud.create_partner(
                    nombre, empresa, email, telefono, direccion, notas, 
                    username if create_account else None,
                    password if create_account else None
                )
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.error("Por favor complete todos los campos obligatorios (*)")

def render_edit_partner(partner_crud):
    """Render edit partner form"""
    st.subheader("✏️ Editar Partner")
    
    # Get all partners for selection
    df = partner_crud.get_all_partners()
    
    if not df.empty:
        partner_id = st.selectbox(
            "Seleccionar partner a editar:",
            options=df['ID'].tolist(),
            format_func=lambda x: f"ID: {x} - {df[df['ID']==x]['Nombre'].iloc[0]} ({df[df['ID']==x]['Empresa'].iloc[0]})"
        )
        
        if partner_id:
            partner_data = partner_crud.get_partner_by_id(partner_id)
            
            if partner_data:
                with st.form("edit_partner_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nombre = st.text_input("Nombre *", value=partner_data['nombre'])
                        empresa = st.text_input("Empresa *", value=partner_data['empresa'])
                        email = st.text_input("Email *", value=partner_data['email'])
                    
                    with col2:
                        telefono = st.text_input("Teléfono", value=partner_data['telefono'] or "")
                        direccion = st.text_area("Dirección", value=partner_data['direccion'] or "")
                        estado = st.selectbox("Estado", ["activo", "inactivo"], 
                                            index=0 if partner_data['estado'] == 'activo' else 1)
                    
                    notas = st.text_area("Notas", value=partner_data['notas'] or "")
                    
                    # User account section
                    st.markdown("---")
                    st.subheader("🔐 Cuenta de Acceso al Sistema")
                    
                    has_account = partner_data['user_id'] is not None
                    
                    if has_account:
                        st.info(f"✅ Este partner tiene cuenta de acceso con usuario: **{partner_data['username']}**")
                        
                        col_user, col_active = st.columns(2)
                        with col_user:
                            username = st.text_input("Usuario *", value=partner_data['username'])
                        with col_active:
                            user_active = st.checkbox("Cuenta Activa", value=bool(partner_data['user_active']))
                        
                        change_password = st.checkbox("Cambiar contraseña")
                        password = None
                        confirm_password = None
                        
                        if change_password:
                            col_pass1, col_pass2 = st.columns(2)
                            with col_pass1:
                                password = st.text_input("Nueva Contraseña *", type="password", placeholder="Mínimo 6 caracteres")
                            with col_pass2:
                                confirm_password = st.text_input("Confirmar Nueva Contraseña *", type="password")
                    else:
                        st.warning("⚠️ Este partner NO tiene cuenta de acceso al sistema")
                        create_account = st.checkbox("Crear cuenta de acceso")
                        
                        username = None
                        password = None
                        confirm_password = None
                        user_active = True
                        
                        if create_account:
                            col_user, col_pass1, col_pass2 = st.columns(3)
                            with col_user:
                                username = st.text_input("Usuario *", placeholder="Nombre de usuario único")
                            with col_pass1:
                                password = st.text_input("Contraseña *", type="password", placeholder="Mínimo 6 caracteres")
                            with col_pass2:
                                confirm_password = st.text_input("Confirmar Contraseña *", type="password")
                    
                    submit = st.form_submit_button("💾 Actualizar Partner", use_container_width=True)
                    
                    if submit:
                        if nombre and empresa and email:
                            # Validate passwords if changing/creating
                            if password or confirm_password:
                                if not username:
                                    st.error("Por favor ingrese un nombre de usuario")
                                    return
                                if password != confirm_password:
                                    st.error("❌ Las contraseñas no coinciden")
                                    return
                                if len(password) < 6:
                                    st.error("❌ La contraseña debe tener al menos 6 caracteres")
                                    return
                            
                            success, message = partner_crud.update_partner(
                                partner_id, nombre, empresa, email, telefono, direccion, estado, notas,
                                username if username else None,
                                password if password else None,
                                user_active if has_account or username else None
                            )
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                        else:
                            st.error("Por favor complete todos los campos obligatorios (*)")
    else:
        st.info("No hay partners registrados para editar.")

def render_partner_stats(partner_crud):
    """Render partner statistics"""
    st.subheader("📊 Estadísticas de Partners")
    
    stats = partner_crud.get_partner_stats()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="📈 Total Partners",
            value=stats['total']
        )
    
    with col2:
        st.metric(
            label="✅ Partners Activos",
            value=stats['activos']
        )
    
    with col3:
        st.metric(
            label="❌ Partners Inactivos",
            value=stats['inactivos']
        )
    
    # Additional stats
    if stats['total'] > 0:
        st.markdown("---")
        
        # Get recent partners
        df = partner_crud.get_all_partners()
        if not df.empty:
            st.subheader("🕒 Partners Registrados Recientemente")
            recent_partners = df.head(5)[['Nombre', 'Empresa', 'Email', 'Fecha Registro']]
            st.dataframe(recent_partners, use_container_width=True)

def render_partner_accounts(partner_crud):
    """Render partner user accounts management"""
    st.subheader("🔐 Gestión de Cuentas de Partner")
    
    # Get partners without user accounts
    df = partner_crud.get_all_partners_with_account_status()
    
    if not df.empty:
        partners_without_account = df[df['Tiene Cuenta'] == 'No']
        
        if not partners_without_account.empty:
            st.markdown("### 👥 Partners sin Cuenta de Acceso")
            st.dataframe(partners_without_account[['ID', 'Nombre', 'Empresa', 'Email']], use_container_width=True)
            
            st.markdown("---")
            st.markdown("### ➕ Crear Cuenta para Partner Existente")
            
            # Select partner
            partner_email = st.selectbox(
                "Seleccionar partner:",
                options=partners_without_account['Email'].tolist(),
                format_func=lambda x: f"{partners_without_account[partners_without_account['Email']==x]['Nombre'].iloc[0]} - {x}"
            )
            
            if partner_email:
                with st.form("create_account_form"):
                    st.info(f"Crear cuenta para: **{partner_email}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        password = st.text_input("Contraseña *", type="password", placeholder="Contraseña para acceder")
                    with col2:
                        confirm_password = st.text_input("Confirmar Contraseña *", type="password", placeholder="Confirmar contraseña")
                    
                    submit = st.form_submit_button("✅ Crear Cuenta de Usuario", use_container_width=True)
                    
                    if submit:
                        if password and confirm_password:
                            if password != confirm_password:
                                st.error("Las contraseñas no coinciden")
                            elif len(password) < 6:
                                st.error("La contraseña debe tener al menos 6 caracteres")
                            else:
                                success, message = partner_crud.create_user_account_for_partner(partner_email, password)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
                        else:
                            st.error("Por favor complete todos los campos de contraseña")
        else:
            st.success("✅ Todos los partners tienen cuenta de acceso")
        
        # Show partners with accounts
        partners_with_account = df[df['Tiene Cuenta'] == 'Sí']
        if not partners_with_account.empty:
            st.markdown("---")
            st.markdown("### ✅ Partners con Cuenta de Acceso")
            st.dataframe(partners_with_account[['ID', 'Nombre', 'Empresa', 'Email']], use_container_width=True)
    
    else:
        st.info("No hay partners registrados en el sistema.")
