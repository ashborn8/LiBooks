import os
import shutil
from db import session
from models import Libro, Nota, Autor, Genero
from sqlalchemy import or_


PDF_FOLDER = "libros"

if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)



def buscar_o_crear_autor(nombre_autor):
    autor = session.query(Autor).filter(
        Autor.nombre.ilike(f"%{nombre_autor}%")
    ).first()
    
    if not autor:
        autor = Autor(nombre=nombre_autor)
        session.add(autor)
        session.commit()
    
    return autor

def buscar_o_crear_genero(nombre_genero):
    genero = session.query(Genero).filter(
        Genero.nombre.ilike(f"%{nombre_genero}%")
    ).first()
    
    if not genero:
        # Si no existe, crear nuevo género
        genero = Genero(nombre=nombre_genero)
        session.add(genero)
        session.commit()
    
    return genero

def crear_libro_pdf(ruta_pdf_original, titulo_libro=None, nombre_autor=None, nombre_genero=None, fecha_lectura=None, paginas_leidas=None):
    # Usar el nombre del libro proporcionado o el nombre del archivo PDF si no se proporciona
    nombre_archivo = titulo_libro if titulo_libro else os.path.basename(ruta_pdf_original)
    destino = os.path.join(PDF_FOLDER, nombre_archivo)
    shutil.copy(ruta_pdf_original, destino)

    id_autor = None
    if nombre_autor:
        autor = buscar_o_crear_autor(nombre_autor)
        id_autor = autor.id_autor

    id_genero = None
    if nombre_genero:
        genero = buscar_o_crear_genero(nombre_genero)
        id_genero = genero.id_genero

    nuevo_libro = Libro(
        titulo=titulo_libro if titulo_libro else os.path.basename(ruta_pdf_original),
        archivo_pdf=nombre_archivo,
        id_autor=id_autor,
        id_genero=id_genero,
        fecha_lectura=fecha_lectura,
        paginas_leidas=paginas_leidas
    )
    session.add(nuevo_libro)
    session.commit()
    return nuevo_libro

def obtener_libros():
    return session.query(Libro).all()

def actualizar_libro(id_libro, nuevo_ruta_pdf=None, nuevo_id_autor=None):
    libro = session.query(Libro).filter_by(id_libro=id_libro).first()
    if libro:
        if nuevo_ruta_pdf:
            
            ruta_anterior = os.path.join(PDF_FOLDER, libro.archivo_pdf)
            if os.path.exists(ruta_anterior):
                os.remove(ruta_anterior)
           
            nombre_archivo = os.path.basename(nuevo_ruta_pdf)
            nuevo_destino = os.path.join(PDF_FOLDER, nombre_archivo)
            shutil.copy(nuevo_ruta_pdf, nuevo_destino)
            libro.archivo_pdf = nombre_archivo
        if nuevo_id_autor:
            libro.id_autor = nuevo_id_autor
        session.commit()
        return libro
    return None

def actualizar_libro(id_libro, nombre_autor=None, nombre_genero=None, fecha_lectura=None, paginas_leidas=None):
    """Actualiza la información de un libro"""
    libro = session.query(Libro).filter_by(id_libro=id_libro).first()
    if libro:
        # Actualizar autor si se proporciona
        if nombre_autor is not None:
            autor = buscar_o_crear_autor(nombre_autor)
            libro.id_autor = autor.id_autor

        # Actualizar género si se proporciona
        if nombre_genero is not None:
            genero = buscar_o_crear_genero(nombre_genero)
            libro.id_genero = genero.id_genero

        # Actualizar otros campos
        if fecha_lectura is not None:
            libro.fecha_lectura = fecha_lectura
        if paginas_leidas is not None:
            libro.paginas_leidas = paginas_leidas

        session.commit()
        return libro
    return None

def eliminar_libro(id_libro):
    libro = session.query(Libro).filter_by(id_libro=id_libro).first()
    if libro:
        
        ruta_pdf = os.path.join(PDF_FOLDER, libro.archivo_pdf)
        if os.path.exists(ruta_pdf):
            os.remove(ruta_pdf)
        
        session.delete(libro)
        session.commit()
        return True
    return False

def buscar_libro_por_nombre(nombre_archivo_pdf):
    return session.query(Libro).filter(Libro.archivo_pdf.ilike(f"%{nombre_archivo_pdf}%")).first()



def crear_nota(titulo, id_libro, contenido):
    nueva_nota = Nota(
        titulo=titulo,
        id_libro=id_libro,
        contenido=contenido
    )
    session.add(nueva_nota)
    session.commit()
    return nueva_nota

def obtener_notas():
    return session.query(Nota).all()

def obtener_notas_de_libro(id_libro):
    return session.query(Nota).filter_by(id_libro=id_libro).all()

def actualizar_nota(id_nota, nuevo_titulo=None, nuevo_contenido=None):
    nota = session.query(Nota).filter_by(id_nota=id_nota).first()
    if nota:
        if nuevo_titulo:
            nota.titulo = nuevo_titulo
        if nuevo_contenido:
            nota.contenido = nuevo_contenido
        session.commit()
        return nota
    return None

def eliminar_nota(id_nota):
    nota = session.query(Nota).filter_by(id_nota=id_nota).first()
    if nota:
        session.delete(nota)
        session.commit()
        return True
    return False
