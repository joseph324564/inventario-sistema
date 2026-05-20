import sqlite3

def init_db():
    conn = sqlite3.connect("sistema_integral.db")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")
    
    # Tabla de Usuarios con los campos de contacto obligatorios para el 2FA
    cur.execute("""CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY, 
                    user TEXT UNIQUE, 
                    pw TEXT, 
                    correo TEXT, 
                    telefono TEXT, 
                    otp_secret TEXT)""")
                    
    cur.execute("""CREATE TABLE IF NOT EXISTS categorias (
                    id INTEGER PRIMARY KEY, 
                    user_id INTEGER, 
                    nombre TEXT,
                    FOREIGN KEY(user_id) REFERENCES usuarios(id) ON DELETE CASCADE)""")
                    
    cur.execute("""CREATE TABLE IF NOT EXISTS proveedores (
                    id INTEGER PRIMARY KEY, 
                    user_id INTEGER, 
                    nombre TEXT, 
                    contacto TEXT, 
                    nit TEXT,
                    FOREIGN KEY(user_id) REFERENCES usuarios(id) ON DELETE CASCADE)""")
                    
    cur.execute("""CREATE TABLE IF NOT EXISTS sedes (
                    id INTEGER PRIMARY KEY, 
                    user_id INTEGER, 
                    nombre TEXT, 
                    direccion TEXT,
                    FOREIGN KEY(user_id) REFERENCES usuarios(id) ON DELETE CASCADE)""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY, 
                    user_id INTEGER, cat_id INTEGER, prov_id INTEGER, sede_id INTEGER,
                    nombre TEXT, fecha_ingreso TEXT, vida_min INTEGER,
                    FOREIGN KEY(user_id) REFERENCES usuarios(id) ON DELETE CASCADE,
                    FOREIGN KEY(cat_id) REFERENCES categorias(id) ON DELETE CASCADE,
                    FOREIGN KEY(prov_id) REFERENCES proveedores(id) ON DELETE CASCADE,
                    FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE)""")
    
    cur.execute("""CREATE TABLE IF NOT EXISTS detalles (
                    id INTEGER PRIMARY KEY, 
                    prod_id INTEGER UNIQUE, 
                    serial TEXT, 
                    marca TEXT, 
                    FOREIGN KEY(prod_id) REFERENCES productos(id) ON DELETE CASCADE)""")
    
    conn.commit()
    conn.close()

def get_connection():
    conn = sqlite3.connect("sistema_integral.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn