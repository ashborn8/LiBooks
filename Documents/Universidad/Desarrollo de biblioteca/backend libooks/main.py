import sys
from PyQt5.QtWidgets import QApplication
from interfaz import BibliotecaApp

def main():
    """
    Punto de entrada principal de la aplicación.
    Inicializa la aplicación Qt y muestra la ventana principal.
    """
    app = QApplication(sys.argv)
    
    # Configuración global de la aplicación
    app.setStyle('Fusion')  # Usar el estilo Fusion para una apariencia más moderna
    
    # Crear y mostrar la ventana principal
    window = BibliotecaApp()
    window.show()
    
    # Ejecutar el bucle de eventos de la aplicación
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
