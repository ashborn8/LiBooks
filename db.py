import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:junsy@localhost:5432/libooks"

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# Carpeta donde se guardarán los PDFs
PDF_FOLDER = "libros"

# Crear la carpeta si no existe
if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)
