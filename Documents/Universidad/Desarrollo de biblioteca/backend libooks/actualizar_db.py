from db import Base, engine
from models import Libro, Nota, Autor, Genero, Coleccion

# Crear todas las tablas definidas en los modelos
print("Creando tablas en la base de datos...")
Base.metadata.create_all(engine)
print("¡Tablas creadas exitosamente!")
