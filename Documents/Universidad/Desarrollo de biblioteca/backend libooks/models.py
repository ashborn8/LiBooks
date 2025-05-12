from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, TIMESTAMP, Table
from sqlalchemy.orm import relationship
import datetime
from db import Base

class Autor(Base):
    __tablename__ = 'autor'

    id_autor = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    
    libros = relationship("Libro", back_populates="autor")

class Genero(Base):
    __tablename__ = 'genero'

    id_genero = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    
    libros = relationship("Libro", back_populates="genero")

class Libro(Base):
    __tablename__ = 'libro'

    id_libro = Column(Integer, primary_key=True)
    id_autor = Column(Integer, ForeignKey('autor.id_autor'))
    archivo_pdf = Column(String)
    titulo = Column(String)
    id_genero = Column(Integer, ForeignKey('genero.id_genero'))
    paginas_leidas = Column(Integer)

    notas = relationship("Nota", back_populates="libro")
    autor = relationship("Autor", back_populates="libros")
    genero = relationship("Genero", back_populates="libros")
    colecciones = relationship("Coleccion", secondary="libro_coleccion", back_populates="libros")

class Nota(Base):
    __tablename__ = 'nota'

    id_nota = Column(Integer, primary_key=True)
    titulo = Column(String)
    id_libro = Column(Integer, ForeignKey('libro.id_libro'))
    contenido = Column(Text)
    fecha_creacion = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    libro = relationship("Libro", back_populates="notas")

# Tabla de asociación para la relación muchos a muchos entre Libro y Coleccion
libro_coleccion = Table('libro_coleccion', Base.metadata,
    Column('id_libro', Integer, ForeignKey('libro.id_libro'), primary_key=True),
    Column('id_coleccion', Integer, ForeignKey('coleccion.id_coleccion'), primary_key=True)
)

class Coleccion(Base):
    __tablename__ = 'coleccion'

    id_coleccion = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False, unique=True)
    
    # Relación muchos a muchos con Libro a través de la tabla de asociación
    libros = relationship("Libro", secondary=libro_coleccion, back_populates="colecciones")
