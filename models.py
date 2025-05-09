from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, TIMESTAMP
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
    fecha_lectura = Column(Date)
    paginas_leidas = Column(Integer)

    notas = relationship("Nota", back_populates="libro")
    autor = relationship("Autor", back_populates="libros")
    genero = relationship("Genero", back_populates="libros")

class Nota(Base):
    __tablename__ = 'nota'

    id_nota = Column(Integer, primary_key=True)
    titulo = Column(String)
    id_libro = Column(Integer, ForeignKey('libro.id_libro'))
    contenido = Column(Text)
    fecha_creacion = Column(TIMESTAMP, default=datetime.datetime.utcnow)

    libro = relationship("Libro", back_populates="notas")
