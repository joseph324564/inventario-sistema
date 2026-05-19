import sqlite3
from datetime import datetime

# --- FASE 1: CONEXIÓN ACTUALIZADA ---
def inicializar_db():
    conexion = sqlite3.connect("bodega_inteligente.db")
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha_ingreso TEXT NOT NULL,
            vida_util_minutos INTEGER NOT NULL
        )
    ''')
    conexion.commit()
    conexion.close()

# --- FASE 2: REGISTRO ---
def agregar_producto():
    print("\n--- REGISTRO DE NUEVO PRODUCTO ---")
    nombre = input("Nombre del alimento: ")
    cantidad = int(input("Ingrese el número de tiempo: "))
    print("1. Minutos | 2. Horas | 3. Días | 4. Meses")
    unidad = input("Seleccione la unidad: ")

    minutos = 0
    if unidad == '1': minutos = cantidad
    elif unidad == '2': minutos = cantidad * 60
    elif unidad == '3': minutos = cantidad * 1440
    elif unidad == '4': minutos = cantidad * 43200
    
    # Guardamos la fecha como texto para evitar advertencias de Python 3.14
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conexion = sqlite3.connect("bodega_inteligente.db")
    cursor = conexion.cursor()
    cursor.execute('''
        INSERT INTO inventario (nombre, fecha_ingreso, vida_util_minutos)
        VALUES (?, ?, ?)
    ''', (nombre, fecha_actual, minutos))
    
    conexion.commit()
    conexion.close()
    print(f"\n[OK] '{nombre}' guardado exitosamente.")

# --- FASE 4: EL CALCULADOR DE DAÑO Y ALARMAS (VERSION CORREGIDA) ---
def mostrar_inventario():
    conexion = sqlite3.connect("bodega_inteligente.db")
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, fecha_ingreso, vida_util_minutos FROM inventario")
    productos = cursor.fetchall()
    
    print("\n" + "="*85)
    print(f"{'ID':<4} | {'PRODUCTO':<15} | {'INGRESADO':<20} | {'DAÑO %':<10} | {'ESTADO'}")
    print("-" * 85)

    ahora = datetime.now()

    for p in productos:
        id_p, nombre, fecha_str, vida_min = p
        
        # CORRECCIÓN AQUÍ: Tomamos solo los primeros 19 caracteres (YYYY-MM-DD HH:MM:SS)
        # Esto ignora cualquier milisegundo extra que cause error
        fecha_limpia = fecha_str[:19]
        fecha_ing_dt = datetime.strptime(fecha_limpia, "%Y-%m-%d %H:%M:%S")
        
        diferencia = ahora - fecha_ing_dt
        minutos_pasados = diferencia.total_seconds() / 60
        porcentaje_daño = (minutos_pasados / vida_min) * 100
        
        if porcentaje_daño >= 100:
            estado = "!!! CADUCADO (PELIGRO) !!!"
        elif porcentaje_daño >= 80:
            estado = "!! CRÍTICO (ALARMA) !!"
        elif porcentaje_daño >= 50:
            estado = "! ALERTA (DAÑO MEDIO) !"
        else:
            estado = "SALUDABLE"

        print(f"{id_p:<4} | {nombre:<15} | {fecha_limpia:<20} | {porcentaje_daño:>8.2f}% | {estado}")

    conexion.close()
    print("="*85)

# --- MENÚ PRINCIPAL ---
def menu():
    inicializar_db()
    while True:
        print("\n================================")
        print("   SISTEMA DE BODEGA A3 (DB)")
        print("================================")
        print("1. Registrar Alimento")
        print("2. Ver Inventario y Alarmas")
        print("3. Salir")
        
        opcion = input("\nSeleccione una opción: ")

        if opcion == '1':
            agregar_producto()
        elif opcion == '2':
            mostrar_inventario()
        elif opcion == '3':
            print("Saliendo del sistema...")
            break

if __name__ == "__main__":
    menu()