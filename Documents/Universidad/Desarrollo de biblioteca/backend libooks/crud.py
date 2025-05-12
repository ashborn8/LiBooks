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

def crear_libro_pdf(ruta_pdf_original, titulo=None, nombre_autor=None, nombre_genero=None, fecha_lectura=None, paginas_leidas=0):
    try:
        # Obtener el nombre del archivo original
        nombre_archivo = os.path.basename(ruta_pdf_original)
        
        # Si no se proporciona un título, usar el nombre del archivo sin extensión
        if not titulo:
            titulo = os.path.splitext(nombre_archivo)[0]
        
        # Copiar el archivo al directorio de libros
        destino = os.path.join(PDF_FOLDER, nombre_archivo)
        shutil.copy(ruta_pdf_original, destino)

        # Buscar o crear autor y género si se proporcionan
        id_autor = None
        if nombre_autor:
            autor = buscar_o_crear_autor(nombre_autor)
            id_autor = autor.id_autor

        id_genero = None
        if nombre_genero:
            genero = buscar_o_crear_genero(nombre_genero)
            id_genero = genero.id_genero

        # Crear el nuevo libro
        nuevo_libro = Libro(
            titulo=titulo,
            archivo_pdf=nombre_archivo,
            id_autor=id_autor,
            id_genero=id_genero,
            paginas_leidas=paginas_leidas
        )
        session.add(nuevo_libro)
        session.commit()
        return nuevo_libro
    except Exception as e:
        print(f"Error al crear libro: {e}")
        session.rollback()
        if os.path.exists(destino):
            os.remove(destino)
        return None

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

def actualizar_libro(id_libro, titulo=None, nombre_autor=None, nombre_genero=None, fecha_lectura=None, paginas_leidas=None):
    """Actualiza la información de un libro"""
    libro = session.query(Libro).filter_by(id_libro=id_libro).first()
    if libro:
        # Actualizar título si se proporciona
        if titulo is not None:
            libro.titulo = titulo

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

def obtener_notas_por_libro(id_libro):
    """Obtiene todas las notas de un libro específico"""
    return session.query(Nota).filter_by(id_libro=id_libro).order_by(Nota.fecha_creacion.desc()).all()

def obtener_nota_por_id(id_nota):
    """Obtiene una nota por su ID"""
    return session.query(Nota).filter_by(id_nota=id_nota).first()

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

def actualizar_paginas_leidas(id_libro, pagina_actual):
    """Actualiza la página actual del libro"""
    try:
        libro = session.query(Libro).filter_by(id_libro=id_libro).first()
        if libro:
            libro.paginas_leidas = pagina_actual
            session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error al actualizar páginas leídas: {e}")
        session.rollback()
        return False

def obtener_paginas_leidas(id_libro):
    """Obtiene la última página leída del libro"""
    try:
        libro = session.query(Libro).filter_by(id_libro=id_libro).first()
        if libro:
            return libro.paginas_leidas
        return 0
    except Exception as e:
        print(f"Error al obtener páginas leídas: {e}")
        return 0

def eliminar_libro(id_libro):
    """Elimina un libro de la base de datos"""
    try:
        libro = session.query(Libro).filter_by(id_libro=id_libro).first()
        if libro:
            # Eliminar el archivo PDF si existe
            from db import PDF_FOLDER
            import os
            ruta_pdf = os.path.join(PDF_FOLDER, libro.archivo_pdf)
            if os.path.exists(ruta_pdf):
                os.remove(ruta_pdf)
            
            # Eliminar el libro de la base de datos
            session.delete(libro)
            session.commit()
            return True
        return False
    except Exception as e:
        print(f"Error al eliminar libro: {e}")
        session.rollback()
        return False
