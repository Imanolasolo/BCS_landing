import sqlite3
import hashlib
import os

class BCSDatabase:
    def __init__(self, db_name="bcs_system.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create roles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT
            )
        ''')
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role_id INTEGER,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                FOREIGN KEY (role_id) REFERENCES roles (id)
            )
        ''')
        
        # Create contacts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                company TEXT,
                email TEXT,
                phone TEXT,
                position TEXT,
                industry TEXT,
                status TEXT DEFAULT 'active',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_contact TIMESTAMP,
                FOREIGN KEY (partner_id) REFERENCES users (id)
            )
        ''')
        
        # Create client_sub_bcs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_sub_bcs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_id INTEGER NOT NULL,
                contact_id INTEGER,
                client_name TEXT NOT NULL,
                company_name TEXT NOT NULL,
                bcs_type TEXT NOT NULL,
                modules TEXT,
                users_count INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active',
                start_date DATE,
                monthly_value REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (partner_id) REFERENCES users (id),
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            )
        ''')
        
        # Create partner_sub_bcs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS partner_sub_bcs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_id INTEGER NOT NULL,
                bcs_name TEXT NOT NULL,
                bcs_type TEXT NOT NULL,
                description TEXT,
                modules TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (partner_id) REFERENCES users (id)
            )
        ''')
        
        # Create user_sub_bcs table (client apps/platforms)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sub_bcs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                partner_id INTEGER,
                app_name TEXT NOT NULL,
                app_description TEXT,
                app_url TEXT NOT NULL,
                app_icon TEXT DEFAULT '🚀',
                app_type TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                access_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (partner_id) REFERENCES users (id)
            )
        ''')
        
        # Create activities table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS partner_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_id INTEGER NOT NULL,
                contact_id INTEGER,
                activity_type TEXT NOT NULL,
                subject TEXT NOT NULL,
                description TEXT,
                activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                follow_up_date DATE,
                completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (partner_id) REFERENCES users (id),
                FOREIGN KEY (contact_id) REFERENCES contacts (id)
            )
        ''')
        
        # Setup default data first
        self.setup_default_data(cursor)
        conn.commit()
        conn.close()
    
    def setup_default_data(self, cursor):
        """Setup default roles and admin user"""
        # Insert default roles
        roles = [
            ('admin', 'Administrador del sistema'),
            ('partner', 'Socio comercial'),
            ('cliente', 'Usuario cliente')
        ]
        
        for role_name, description in roles:
            cursor.execute(
                'INSERT OR IGNORE INTO roles (name, description) VALUES (?, ?)',
                (role_name, description)
            )
        
        # Get admin role ID
        cursor.execute('SELECT id FROM roles WHERE name = ?', ('admin',))
        admin_role = cursor.fetchone()
        
        if admin_role:
            admin_role_id = admin_role[0]
            
            # Create/Update admin user with hardcoded credentials
            admin_password = self.hash_password("admin123")
            
            # Check if admin exists
            cursor.execute('SELECT id FROM users WHERE username = ?', ("admin",))
            admin_exists = cursor.fetchone()
            
            if admin_exists:
                # Update existing admin
                cursor.execute(
                    'UPDATE users SET password_hash = ?, role_id = ? WHERE username = ?',
                    (admin_password, admin_role_id, "admin")
                )
            else:
                # Create new admin
                cursor.execute(
                    'INSERT INTO users (username, password_hash, role_id, email) VALUES (?, ?, ?, ?)',
                    ("admin", admin_password, admin_role_id, "admin@bcs.com")
                )

    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate_user(self, username, password):
        """Authenticate user and return role"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            SELECT u.id, u.username, r.name as role, u.email
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.username = ? AND u.password_hash = ? AND u.is_active = 1
        ''', (username, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'username': user[1],
                'role': user[2],
                'email': user[3]
            }
        return None
    
    def create_user(self, username, password, role_name, email=None):
        """Create new user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get role ID
        cursor.execute('SELECT id FROM roles WHERE name = ?', (role_name,))
        role = cursor.fetchone()
        
        if not role:
            conn.close()
            return False, "Rol no encontrado"
        
        password_hash = self.hash_password(password)
        
        try:
            cursor.execute(
                'INSERT INTO users (username, password_hash, role_id, email) VALUES (?, ?, ?, ?)',
                (username, password_hash, role[0], email)
            )
            conn.commit()
            conn.close()
            return True, "Usuario creado exitosamente"
        except sqlite3.IntegrityError:
            conn.close()
            return False, "El usuario ya existe"
    
    def user_exists(self, username_or_email):
        """Check if user exists by username or email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM users 
            WHERE username = ? OR email = ?
        ''', (username_or_email, username_or_email))
        
        user = cursor.fetchone()
        conn.close()
        
        return user is not None
