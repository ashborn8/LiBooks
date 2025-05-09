from utils import seleccionar_pdf
from crud import crear_libro_pdf, crear_nota, obtener_libros, obtener_notas, eliminar_libro as crud_eliminar_libro, eliminar_nota as crud_eliminar_nota, actualizar_libro as crud_actualizar_libro, actualizar_nota as crud_actualizar_nota

def menu():
    while True:
        print("\n===== MENÚ PRINCIPAL =====")
        print("1. Agregar Libro (PDF)")
        print("2. Ver Libros")
        print("3. Actualizar Libro")
        print("4. Eliminar Libro")
        print("5. Agregar Nota")
        print("6. Ver Notas")
        print("7. Actualizar Nota")
        print("8. Eliminar Nota")
        print("9. Salir")
        opcion = input("Selecciona una opción: ")

        if opcion == '1':
            agregar_libro()
        elif opcion == '2':
            ver_libros()
        elif opcion == '3':
            actualizar_libro()
        elif opcion == '4':
            eliminar_libro()
        elif opcion == '5':
            agregar_nota()
        elif opcion == '6':
            ver_notas()
        elif opcion == '7':
            actualizar_nota()
        elif opcion == '8':
            eliminar_nota()
        elif opcion == '9':
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Inténtalo de nuevo.")

def agregar_libro():
    print("\n--- Agregar Libro (PDF) ---")
    ruta_pdf = seleccionar_pdf()

    if not ruta_pdf:
        print("No se seleccionó ningún archivo. Operación cancelada.")
        return

    print("\nNota: Para los siguientes campos, presiona Enter si deseas dejarlos vacíos.")
    
    nombre_autor = input("Nombre del autor (o Enter para dejar vacío): ")
    nombre_genero = input("Género del libro (o Enter para dejar vacío): ")
    fecha_lectura = input("Fecha de lectura (YYYY-MM-DD) (opcional): ")
    
    while True:
        paginas_leidas = input("Páginas leídas (número entero o vacío): ")
        if paginas_leidas == "":
            paginas_leidas = None
            break
        try:
            paginas_leidas = int(paginas_leidas)
            break
        except ValueError:
            print("Error: Las páginas leídas deben ser un número entero. Intenta nuevamente.")

    try:
        libro = crear_libro_pdf(
            ruta_pdf_original=ruta_pdf,
            nombre_autor=nombre_autor if nombre_autor else None,
            nombre_genero=nombre_genero if nombre_genero else None,
            fecha_lectura=fecha_lectura if fecha_lectura else None,
            paginas_leidas=paginas_leidas
        )
        
        detalles = []
        if libro.autor:
            detalles.append(f"autor '{libro.autor.nombre}'")
        if libro.genero:
            detalles.append(f"género '{libro.genero.nombre}'")
            
        if detalles:
            detalles_str = " con " + " y ".join(detalles)
        else:
            detalles_str = " sin autor ni género"
            
        print(f"Libro '{libro.archivo_pdf}' agregado exitosamente{detalles_str} .")
    except Exception as e:
        print(f"Error agregando el libro: {e}")


def ver_libros():
    print("\n--- Lista de Libros ---")
    libros = obtener_libros()
    if libros:
        for libro in libros:
            print(f"ID: {libro.id_libro}, Archivo PDF: {libro.archivo_pdf}")
    else:
        print("No hay libros registrados todavía.")

def agregar_nota():
    print("\n--- Agregar Nota ---")
    nombre_archivo = input("Nombre del archivo PDF asociado al libro: ")

    # Buscar el libro por nombre de PDF
    from db import session
    from models import Libro
    libro = session.query(Libro).filter(Libro.archivo_pdf.ilike(f"%{nombre_archivo}%")).first()

    if libro:
        print(f"Libro encontrado: ID {libro.id_libro} - {libro.archivo_pdf}")
        titulo_nota = input("Título de la nota: ")
        contenido = input("Contenido de la nota: ")

        nota = crear_nota(
            titulo=titulo_nota,
            id_libro=libro.id_libro,
            contenido=contenido
        )

        print(f"Nota '{nota.titulo}' agregada exitosamente al libro '{libro.archivo_pdf}' .")
    else:
        print(f"No se encontró ningún libro con el archivo '{nombre_archivo}'. Inténtalo otra vez")

def ver_notas():
    print("\n--- Lista de Notas ---")
    notas = obtener_notas()
    if notas:
        for nota in notas:
            print(f"ID: {nota.id_nota}, Título: {nota.titulo}, Libro ID: {nota.id_libro}")
    else:
        print("No hay notas registradas todavía.")

def eliminar_libro():
    print("\n--- Eliminar Libro ---")
    ver_libros()
    id_libro = input("\nIngrese el ID del libro a eliminar (o Enter para cancelar): ")
    
    if not id_libro:
        print("Operación cancelada.")
        return
        
    try:
        id_libro = int(id_libro)
        if crud_eliminar_libro(id_libro):
            print(f"Libro con ID {id_libro} eliminado exitosamente.")
        else:
            print(f"No se encontró el libro con ID {id_libro}.")
    except ValueError:
        print("Error: El ID debe ser un número entero.")
    except Exception as e:
        print(f"Error eliminando el libro: {e}")

def eliminar_nota():
    print("\n--- Eliminar Nota ---")
    ver_notas()
    id_nota = input("\nIngrese el ID de la nota a eliminar (o Enter para cancelar): ")
    
    if not id_nota:
        print("Operación cancelada.")
        return
        
    try:
        id_nota = int(id_nota)
        if crud_eliminar_nota(id_nota):
            print(f"Nota con ID {id_nota} eliminada exitosamente.")
        else:
            print(f"No se encontró la nota con ID {id_nota}.")
    except ValueError:
        print("Error: El ID debe ser un número entero.")
    except Exception as e:
        print(f"Error eliminando la nota: {e}")

def actualizar_libro():
    print("\n--- Actualizar Libro ---")
    ver_libros()
    id_libro = input("\nIngrese el ID del libro a actualizar (o Enter para cancelar): ")
    
    if not id_libro:
        print("Operación cancelada.")
        return
        
    try:
        id_libro = int(id_libro)
        from db import session
        from models import Libro
        libro = session.query(Libro).filter_by(id_libro=id_libro).first()
        
        if not libro:
            print(f"No se encontró el libro con ID {id_libro}.")
            return
            
        print(f"\nActualizando libro: {libro.archivo_pdf}")
        print("Deja en blanco los campos que no deseas modificar.")
        
        nombre_autor = input("Nuevo nombre del autor (Enter para no cambiar): ")
        nombre_genero = input("Nuevo género del libro (Enter para no cambiar): ")
        fecha_lectura = input("Nueva fecha de lectura (YYYY-MM-DD) (Enter para no cambiar): ")
        
        while True:
            paginas_leidas = input("Nuevas páginas leídas (número entero o Enter para no cambiar): ")
            if not paginas_leidas:
                paginas_leidas = None
                break
            try:
                paginas_leidas = int(paginas_leidas)
                break
            except ValueError:
                print("Error: Las páginas leídas deben ser un número entero. Intenta nuevamente.")
        
        libro_actualizado = crud_actualizar_libro(
            id_libro,
            nombre_autor=nombre_autor if nombre_autor else None,
            nombre_genero=nombre_genero if nombre_genero else None,
            fecha_lectura=fecha_lectura if fecha_lectura else None,
            paginas_leidas=paginas_leidas
        )
        
        if libro_actualizado:
            detalles = []
            if libro_actualizado.autor:
                detalles.append(f"autor '{libro_actualizado.autor.nombre}'")
            if libro_actualizado.genero:
                detalles.append(f"género '{libro_actualizado.genero.nombre}'")
                
            if detalles:
                detalles_str = " con " + " y ".join(detalles)
            else:
                detalles_str = " sin autor ni género"
                
            print(f"Libro '{libro_actualizado.archivo_pdf}' actualizado exitosamente{detalles_str}.")
        
    except ValueError:
        print("Error: El ID debe ser un número entero.")
    except Exception as e:
        print(f"Error actualizando el libro: {e}")

def actualizar_nota():
    print("\n--- Actualizar Nota ---")
    ver_notas()
    id_nota = input("\nIngrese el ID de la nota a actualizar (o Enter para cancelar): ")
    
    if not id_nota:
        print("Operación cancelada.")
        return
        
    try:
        id_nota = int(id_nota)
        from db import session
        from models import Nota
        nota = session.query(Nota).filter_by(id_nota=id_nota).first()
        
        if not nota:
            print(f"No se encontró la nota con ID {id_nota}.")
            return
            
        print(f"\nActualizando nota del libro: {nota.libro.archivo_pdf}")
        print("Deja en blanco los campos que no deseas modificar.")
        
        nuevo_titulo = input("Nuevo título (Enter para no cambiar): ")
        nuevo_contenido = input("Nuevo contenido (Enter para no cambiar): ")
        
        nota_actualizada = crud_actualizar_nota(
            id_nota,
            nuevo_titulo=nuevo_titulo if nuevo_titulo else None,
            nuevo_contenido=nuevo_contenido if nuevo_contenido else None
        )
        
        if nota_actualizada:
            print(f"Nota '{nota_actualizada.titulo}' actualizada exitosamente.")
        
    except ValueError:
        print("Error: El ID debe ser un número entero.")
    except Exception as e:
        print(f"Error actualizando la nota: {e}")

if __name__ == "__main__":
    menu()
