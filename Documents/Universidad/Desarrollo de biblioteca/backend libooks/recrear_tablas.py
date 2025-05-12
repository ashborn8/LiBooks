"""
Script para eliminar y recrear las tablas de la base de datos.
"""
from sqlalchemy import text
from db import engine, Base, session

def recrear_tablas():
    """Elimina y vuelve a crear todas las tablas."""
    print("Eliminando tablas existentes...")
    
    # Desactivar las restricciones de clave foránea temporalmente
    with engine.connect() as conn:
        conn.execute(text("SET session_replication_role = 'replica';"))
        conn.commit()
    
    # Eliminar todas las tablas
    Base.metadata.drop_all(bind=engine)
    
    # Volver a crear todas las tablas
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    
    # Reactivar las restricciones de clave foránea
    with engine.connect() as conn:
        conn.execute(text("SET session_replication_role = 'origin';"))
        conn.commit()
    
    print("¡Tablas recreadas correctamente!")

if __name__ == "__main__":
    print("Recreando tablas...")
    recrear_tablas()
    print("Proceso completado.")
