import os
import shutil
from db import session
from models import Libro, Nota, Autor, Genero, Coleccion
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload
from typing import List, Optional
import traceback as tb


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

def obtener_libros() -> List[Libro]:
    """Obtiene todos los libros de la base de datos"""
    return session.query(Libro).all()

def obtener_libros_por_ids(ids_libros: List[int]) -> List[Libro]:
    """
    Obtiene una lista de libros por sus IDs
    
    Args:
        ids_libros: Lista de IDs de libros a buscar
        
    Returns:
        List[Libro]: Lista de libros encontrados
    """
    if not ids_libros:
        return []
        
    return session.query(Libro).filter(Libro.id_libro.in_(ids_libros)).all()


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

def crear_coleccion(nombre):
    """Crea una nueva colección"""
    try:
        print(f"Intentando crear colección: {nombre}")
        # Verificar si ya existe una colección con el mismo nombre
        coleccion_existente = session.query(Coleccion).filter_by(nombre=nombre).first()
        if coleccion_existente:
            print(f"Ya existe una colección con el nombre: {nombre}")
            print(f"ID de colección existente: {coleccion_existente.id_coleccion}")
            return False
            
        # Crear la nueva colección
        nueva_coleccion = Coleccion(nombre=nombre)
        session.add(nueva_coleccion)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error al crear la colección: {e}")
        tb.print_exc()
        return False

def obtener_colecciones():
    """Obtiene todas las colecciones"""
    try:
        print("Obteniendo todas las colecciones...")
        colecciones = session.query(Coleccion).all()
        print(f"Número de colecciones encontradas: {len(colecciones)}")
        for i, coleccion in enumerate(colecciones, 1):
            print(f"Colección {i}: {coleccion.nombre} (ID: {coleccion.id_coleccion})")
            print(f"  Libros en la colección: {[libro.titulo for libro in coleccion.libros]}")
        return colecciones
    except Exception as e:
        print(f"Error al obtener las colecciones: {e}")
        tb.print_exc()
        return []

def eliminar_coleccion(id_coleccion):
    """Elimina una colección por su ID"""
    try:
        coleccion = session.query(Coleccion).get(id_coleccion)
        if coleccion:
            # Eliminar las relaciones en la tabla puente primero
            coleccion.libros = []
            session.commit()
            
            # Luego eliminar la colección
            session.delete(coleccion)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error al eliminar la colección: {e}")
        tb.print_exc()
        return False

def eliminar_libro(id_libro):
    """
    Elimina un libro de la base de datos junto con todas sus referencias.
    
    Args:
        id_libro (int): ID del libro a eliminar
        
    Returns:
        bool: True si se eliminó correctamente, False en caso contrario
    """
    try:
        # Obtener el libro
        libro = session.query(Libro).get(id_libro)
        if not libro:
            return False
        
        # Obtener las relaciones por separado
        notas = session.query(Nota).filter_by(id_libro=id_libro).all()
        colecciones = session.query(Coleccion).filter(Coleccion.libros.any(id_libro=id_libro)).all()
        
        # 1. Eliminar el archivo PDF físico si existe
        if libro.archivo_pdf:
            ruta_pdf = os.path.join(PDF_FOLDER, libro.archivo_pdf)
            if os.path.exists(ruta_pdf):
                try:
                    os.remove(ruta_pdf)
                except Exception as e:
                    print(f"Error al eliminar el archivo PDF: {e}")
        
        # 2. Eliminar todas las notas asociadas al libro
        for nota in notas:
            session.delete(nota)
        
        # 3. Eliminar las relaciones con las colecciones
        for coleccion in colecciones:
            libro.colecciones.remove(coleccion)
        
        # 4. Guardar referencias a autor y género antes de eliminar el libro
        autor_id = libro.id_autor
        genero_id = libro.id_genero
        
        # 5. Eliminar el libro
        session.delete(libro)
        session.commit()
        
        # 6. Verificar si el autor y el género quedan sin referencias y eliminarlos si es necesario
        if autor_id:
            # Verificar si el autor tiene más libros
            libros_del_autor = session.query(Libro).filter_by(id_autor=autor_id).count()
            if libros_del_autor == 0:
                autor = session.query(Autor).get(autor_id)
                if autor:
                    session.delete(autor)
                    session.commit()
        
        if genero_id:
            # Verificar si el género tiene más libros
            libros_del_genero = session.query(Libro).filter_by(id_genero=genero_id).count()
            if libros_del_genero == 0:
                genero = session.query(Genero).get(genero_id)
                if genero:
                    session.delete(genero)
                    session.commit()
        
        return True
        
    except Exception as e:
        session.rollback()
        print(f"Error al eliminar el libro: {e}")
        import traceback
        traceback.print_exc()
        return False

def agregar_libro_a_coleccion(id_coleccion, id_libro):
    """Agrega un libro a una colección"""
    try:
        coleccion = session.query(Coleccion).get(id_coleccion)
        libro = session.query(Libro).get(id_libro)
        
        if not coleccion or not libro:
            print("Colección o libro no encontrado")
            return False
            
        if libro in coleccion.libros:
            print("El libro ya está en la colección")
            return False
            
        coleccion.libros.append(libro)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error al agregar libro a la colección: {e}")
        tb.print_exc()
        return False

def quitar_libro_de_coleccion(id_coleccion, id_libro):
    """Quita un libro de una colección"""
    try:
        coleccion = session.query(Coleccion).get(id_coleccion)
        libro = session.query(Libro).get(id_libro)
        
        if not coleccion or not libro:
            print("Colección o libro no encontrado")
            return False
            
        if libro not in coleccion.libros:
            print("El libro no está en la colección")
            return False
            
        coleccion.libros.remove(libro)
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error al quitar libro de la colección: {e}")
        tb.print_exc()
        return False

def actualizar_nombre_coleccion(id_coleccion, nuevo_nombre):
    """Actualiza el nombre de una colección"""
    try:
        coleccion = session.query(Coleccion).get(id_coleccion)
        if coleccion:
            # Verificar si ya existe otra colección con el mismo nombre
            existe = session.query(Coleccion).filter(
                Coleccion.nombre == nuevo_nombre,
                Coleccion.id_coleccion != id_coleccion
            ).first()
            
            if existe:
                print("Ya existe otra colección con ese nombre")
                return False
                
            coleccion.nombre = nuevo_nombre
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error al actualizar el nombre de la colección: {e}")
        tb.print_exc()
        return False

def obtener_coleccion_por_id(id_coleccion):
    """Obtiene una colección por su ID"""
    try:
        return session.query(Coleccion).get(id_coleccion)
    except Exception as e:
        print(f"Error al obtener la colección: {e}")
        return None

def obtener_libros_en_coleccion(id_coleccion):
    """Obtiene todos los libros que pertenecen a una colección específica"""
    try:
        print(f"\n[DEBUG] Buscando libros para la colección ID: {id_coleccion}")
        
        # Usar una consulta explícita para obtener los libros de la colección
        from models import libro_coleccion, Libro
        
        # Consulta para obtener los libros de la colección usando la tabla de asociación
        libros = session.query(Libro).join(
            libro_coleccion, 
            Libro.id_libro == libro_coleccion.c.id_libro
        ).filter(
            libro_coleccion.c.id_coleccion == id_coleccion
        ).all()
        
        print(f"[DEBUG] Número de libros encontrados en la colección: {len(libros) if libros else 0}")
        
        # Imprimir información de cada libro para depuración
        for i, libro in enumerate(libros, 1):
            print(f"[DEBUG] Libro {i}: ID={libro.id_libro}, Título='{libro.titulo}'")
        
        return libros
    except Exception as e:
        print(f"Error al obtener libros de la colección: {e}")
        tb.print_exc()
        return []
