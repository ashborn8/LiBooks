import re
import os

def actualizar_mensajes():
    # Ruta al archivo de origen y destino
    ruta_origen = r"c:\Users\junsy\Documents\Universidad\Desarrollo de biblioteca\backend libooks\interfaz.py"
    ruta_destino = r"c:\Users\junsy\Documents\Universidad\Desarrollo de biblioteca\backend libooks\interfaz_actualizado.py"
    
    # Patrones para los diferentes tipos de mensajes
    patrones = [
        # QMessageBox.information
        (r'QMessageBox\.information\s*\(\s*([^,]+)\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*(?:,\s*QMessageBox\.\w+\s*,\s*QMessageBox\.\w+\s*)?\)',
         'mostrar_mensaje(\1, "\2", "\3", \'info\')'),
        
        # QMessageBox.warning
        (r'QMessageBox\.warning\s*\(\s*([^,]+)\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*(?:,\s*QMessageBox\.\w+\s*,\s*QMessageBox\.\w+\s*)?\)',
         'mostrar_mensaje(\1, "\2", "\3", \'warning\')'),
        
        # QMessageBox.critical
        (r'QMessageBox\.critical\s*\(\s*([^,]+)\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*(?:,\s*QMessageBox\.\w+\s*,\s*QMessageBox\.\w+\s*)?\)',
         'mostrar_mensaje(\1, "\2", "\3", \'error\')'),
        
        # QMessageBox.question (caso especial)
        (r'(\w+)\s*=\s*QMessageBox\.question\s*\(\s*([^,]+)\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*QMessageBox\.Yes\s*\|\s*QMessageBox\.No\s*,\s*QMessageBox\.No\s*\)',
         '\1 = mostrar_mensaje(\2, "\3", "\4", \'question\')'),
        
        # QMessageBox.question (sin asignación)
        (r'QMessageBox\.question\s*\(\s*([^,]+)\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*QMessageBox\.Yes\s*\|\s*QMessageBox\.No\s*,\s*QMessageBox\.No\s*\)',
         'mostrar_mensaje(\1, "\2", "\3", \'question\')')
    ]
    
    # Leer el archivo original
    with open(ruta_origen, 'r', encoding='utf-8') as f:
        contenido = f.read()
    
    # Aplicar las sustituciones
    for patron, reemplazo in patrones:
        contenido = re.sub(patron, reemplazo, contenido, flags=re.DOTALL)
    
    # Reemplazar las comparaciones con QMessageBox.Yes
    contenido = contenido.replace('== QMessageBox.Yes', '== "yes"')
    
    # Escribir el archivo actualizado
    with open(ruta_destino, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"Archivo actualizado guardado en: {ruta_destino}")
    print("Por favor, revisa los cambios antes de reemplazar el archivo original.")

if __name__ == "__main__":
    actualizar_mensajes()
