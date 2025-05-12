from db import session
from models import Coleccion

# Verificar la conexión a la base de datos
try:
    # Intentar contar las colecciones
    count = session.query(Coleccion).count()
    print(f"Número de colecciones en la base de datos: {count}")
    
    # Listar todas las colecciones
    print("\nListando colecciones:")
    colecciones = session.query(Coleccion).all()
    for i, coleccion in enumerate(colecciones, 1):
        print(f"{i}. {coleccion.nombre} (ID: {coleccion.id_coleccion})")
    
    # Intentar crear una nueva colección
    print("\nIntentando crear una nueva colección...")
    from crud import crear_coleccion
    
    # Crear una colección de prueba
    nombre_prueba = "Mi Colección de Prueba"
    print(f"Creando colección: {nombre_prueba}")
    
    if crear_coleccion(nombre_prueba):
        print("¡Colección creada exitosamente!")
        
        # Verificar que se creó
        coleccion_creada = session.query(Coleccion).filter_by(nombre=nombre_prueba).first()
        if coleccion_creada:
            print(f"Colección encontrada en la base de datos - ID: {coleccion_creada.id_coleccion}")
        else:
            print("Error: No se pudo encontrar la colección recién creada")
    else:
        print("Error: No se pudo crear la colección")
        
    # Mostrar las colecciones nuevamente
    print("\nColecciones después de la operación:")
    colecciones = session.query(Coleccion).all()
    for i, coleccion in enumerate(colecciones, 1):
        print(f"{i}. {coleccion.nombre} (ID: {coleccion.id_coleccion})")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Cerrar la sesión
    session.close()
    print("\nPrueba completada.")
