from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QFrame,
    QFileDialog, QMessageBox, QDialog
)
from pdf_viewer import PDFViewer

from datos import Datos
from PyQt5.QtGui import QFont, QIcon, QColor, QPixmap
from PyQt5.QtCore import Qt, QSize
import sys
import os

from crud import crear_libro_pdf

class BibliotecaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Biblioteca Digital')
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #0F3444;")  

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout(self)

        
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet("background-color: #0F3444;")
        sidebar_layout = QVBoxLayout(sidebar)

        books_icon = QLabel()
        pixmap = QPixmap(100, 100)
        pixmap.fill(Qt.transparent)
        books_icon.setPixmap(QPixmap("icono_libros.png").scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        books_icon.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(books_icon)

        colecciones_label = QLabel("Colecciones +")
        colecciones_label.setFont(QFont("Arial", 18, QFont.Bold))
        colecciones_label.setStyleSheet("color: white;")
        colecciones_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(colecciones_label)

        sub_label = QLabel('Presiona en el "+" \npara agregar una nueva colección')
        sub_label.setFont(QFont("Arial", 12))
        sub_label.setStyleSheet("color: lightgray;")
        sub_label.setAlignment(Qt.AlignCenter)
        sidebar_layout.addWidget(sub_label)

        sidebar_layout.addStretch()

        config_button = QPushButton("Configuraciones")
        config_button.setIcon(QIcon.fromTheme("settings"))
        config_button.setStyleSheet("""
            QPushButton {
                color: white;
                font-size: 14px;
                background-color: transparent;
                border: none;
                margin-bottom: 10px;
            }
        """)
        sidebar_layout.addWidget(config_button, alignment=Qt.AlignBottom)

        line = QFrame()
        line.setFrameShape(QFrame.VLine)
        line.setStyleSheet("border: 2px dashed lightgray;")
        main_layout.addWidget(sidebar)
        main_layout.addWidget(line)

        
        right_panel = QVBoxLayout()

        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Buscar")
        search_input.setFixedHeight(40)
        search_input.setStyleSheet("""
            QLineEdit {
                background-color: #73C3AD;
                border-radius: 20px;
                padding-left: 20px;
                font-size: 16px;
            }
        """)
        search_layout.addWidget(search_input)

        search_button = QPushButton()
        search_button.setIcon(QIcon.fromTheme("search"))
        search_button.setFixedSize(40, 40)
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #73C3AD;
                border-radius: 20px;
            }
        """)
        search_layout.addWidget(search_button)
        search_layout.addStretch()

        right_panel.addLayout(search_layout)
        right_panel.addSpacing(20)

        add_book_btn = QPushButton("Añadir Libro +")
        add_book_btn.setFixedHeight(70)
        add_book_btn.setStyleSheet("""
            QPushButton {
                background-color: #518C7A;
                color: white;
                font-size: 20px;
                border: 2px dashed lightgray;
                border-radius: 30px;
            }
        """)
        add_book_btn.clicked.connect(self.agregar_libro_pdf) 
        right_panel.addWidget(add_book_btn)

        # Lista de PDFs
        self.pdf_list = QListWidget()
        self.pdf_list.setStyleSheet("""
            QListWidget {
                background-color: #73C3AD;
                border-radius: 15px;
                padding: 10px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
                margin: 5px;
            }
            QListWidget::item:selected {
                background-color: #518C7A;
                color: white;
            }
        """)
        right_panel.addWidget(self.pdf_list)
        
        # Conectar la señal de selección
        self.pdf_list.itemDoubleClicked.connect(self.abrir_pdf)

        right_panel.addStretch()

        main_layout.addLayout(right_panel)

        # Cargar PDFs desde la base de datos
        self.cargar_pdf_desde_db()

    def agregar_libro_pdf(self):
        ruta_pdf, _ = QFileDialog.getOpenFileName(self, "Selecciona un archivo PDF", "", "Archivos PDF (*.pdf)")
        if ruta_pdf:
            try:
                dialogo = Datos()
                if dialogo.exec_() == QDialog.Accepted:
                    nombre_libro, nombre_autor, nombre_genero = dialogo.obtener_datos()

                    id_autor = 1
                    id_genero = 1

                    libro = crear_libro_pdf(
                        ruta_pdf_original=ruta_pdf,
                        titulo_libro=nombre_libro,
                        nombre_autor=nombre_autor,
                        nombre_genero=nombre_genero
                    )
                    
                    # Agregar el PDF a la lista
                    item = QListWidgetItem()
                    item.setText(f"{libro.archivo_pdf}")
                    item.setToolTip(ruta_pdf)
                    self.pdf_list.addItem(item)
                    
                    # Guardar la ruta del PDF en los datos del ítem
                    item.setData(Qt.UserRole, ruta_pdf)
                    
                    QMessageBox.information(self, "Éxito", f"Libro '{libro.archivo_pdf}' agregado exitosamente.")
                else:
                    QMessageBox.warning(self, "Cancelado", "Se canceló el ingreso del autor y género.")    
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo agregar el libro.\nError: {e}")
        else:
            QMessageBox.warning(self, "Cancelado", "No se seleccionó ningún archivo.")  

    def abrir_pdf(self, item):
        """Abre el PDF seleccionado en el visualizador"""
        datos_libro = item.data(Qt.UserRole)
        if datos_libro and 'ruta_pdf' in datos_libro:
            viewer = PDFViewer(datos_libro['ruta_pdf'])
            viewer.exec_()

    def cargar_pdf_desde_db(self):
        """Carga los PDFs desde la base de datos"""
        from crud import obtener_libros
        from db import PDF_FOLDER
        
        # Limpiar la lista actual
        self.pdf_list.clear()
        
        # Obtener todos los libros de la base de datos
        libros = obtener_libros()
        
        for libro in libros:
            # Crear el ítem
            item = QListWidgetItem()
            item.setText(libro.archivo_pdf)
            
            # Construir la ruta completa del PDF
            ruta_pdf = os.path.join(PDF_FOLDER, libro.archivo_pdf)
            if os.path.exists(ruta_pdf):
                item.setToolTip(ruta_pdf)
                item.setData(Qt.UserRole, ruta_pdf)
                self.pdf_list.addItem(item)



if __name__ == "__main__":  
    app = QApplication(sys.argv)
    window = BibliotecaApp()
    window.show()
    sys.exit(app.exec_())
