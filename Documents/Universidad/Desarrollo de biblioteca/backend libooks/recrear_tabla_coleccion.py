from sqlalchemy import inspect, text
from db import engine, Base, session
from models import Coleccion

# Obtener el inspector de la base de datos
inspector = inspect(engine)

# Verificar si la tabla existe
if 'coleccion' in inspector.get_table_names():
    print("Eliminando tabla 'coleccion' existente...")
    # Eliminar la tabla existente con CASCADE
    with engine.connect() as conn:
        conn.execute(text('DROP TABLE IF EXISTS coleccion CASCADE'))
        conn.commit()

# Crear la tabla nuevamente
print("\nCreando la tabla 'coleccion' con el esquema actualizado...")
Base.metadata.create_all(engine, tables=[Coleccion.__table__])

# Verificar que la tabla se creó correctamente
if 'coleccion' in inspector.get_table_names():
    print("\n¡Tabla 'coleccion' recreada exitosamente!")
    
    # Mostrar la estructura de la tabla
    print("\nEstructura de la tabla 'coleccion':")
    columns = inspector.get_columns('coleccion')
    for column in columns:
        print(f"- {column['name']}: {column['type']}")
else:
    print("\nError: No se pudo crear la tabla 'coleccion'")

print("\nProceso completado.")
