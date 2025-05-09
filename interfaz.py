from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QFrame,
    QFileDialog, QMessageBox, QDialog, QInputDialog
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
        self.delete_button_style = """
            QPushButton {
                background-color: #FF5252;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #FF1744;
            }
        """
        self.setWindowTitle('Biblioteca Digital')
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #0F3444;")  

        self.initUI()

    def initUI(self):
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        # Panel izquierdo (sidebar)
        sidebar = QFrame()
        sidebar.setFixedWidth(300)
        sidebar.setStyleSheet("background-color: #0F3444;")
        sidebar_layout = QVBoxLayout(sidebar)
        main_layout.addWidget(sidebar)

        # Logo
        logo_label = QLabel()
        logo_pixmap = QPixmap("logo.png")
        if not logo_pixmap.isNull():
            scaled_pixmap = logo_pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
        sidebar_layout.addWidget(logo_label)

        # Título "Colecciones"
        collections_title = QLabel("Colecciones +")
        collections_title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                margin-bottom: 10px;
            }
        """)
        sidebar_layout.addWidget(collections_title)

        # Subtítulo
        subtitle = QLabel('Presiona en el "+"\npara agregar una nueva colección')
        subtitle.setStyleSheet("""
            QLabel {
                color: #73C3AD;
                font-size: 14px;
            }
        """)
        sidebar_layout.addWidget(subtitle)

        # Icono de libros
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


        common_style = """
            background-color: #1A4D5B;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 15px;
            font-size: 14px;
        """
        
        hover_style = """
            background-color: #518C7A;
        """
        
        # Estilo para el botón de agregar libro
        add_book_btn.setStyleSheet(f"""
            QPushButton {{
                {common_style}
            }}
            QPushButton:hover {{
                {hover_style}
            }}
        """)
        
        # Crear un widget contenedor para la lista con fondo transparente
        list_container = QWidget()
        list_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
            }
        """)
        list_layout = QVBoxLayout(list_container)
        list_layout.setContentsMargins(0, 0, 0, 0)
        
        # Configurar la lista de PDFs
        self.pdf_list = QListWidget()
        self.pdf_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.pdf_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.pdf_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                background-color: #1A4D5B;
                color: white;
                border-radius: 15px;
                margin: 5px;
                min-height: 50px;
            }
            QListWidget::item:hover {
                background-color: #518C7A;
            }
            QListWidget::item:selected {
                background-color: #518C7A;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #518C7A;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background-color: transparent;
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background-color: transparent;
            }}
        """)
        
        # Agregar la lista al contenedor
        list_layout.addWidget(self.pdf_list)
        
        # Agregar el contenedor al panel derecho
        right_panel.addWidget(list_container, 1)  # El 1 hace que tome todo el espacio disponible
        
        # Conectar la señal de selección
        self.pdf_list.itemDoubleClicked.connect(self.abrir_pdf)

        right_panel.addStretch()

        main_layout.addLayout(right_panel)

        # Cargar PDFs desde la base de datos
        self.cargar_pdf_desde_db()

    def agregar_libro_pdf(self):
        """Abre un diálogo para seleccionar y agregar un nuevo libro PDF"""
        archivo, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar PDF",
            "",
            "Archivos PDF (*.pdf)"
        )
        
        if archivo:
            try:
                # Abrir el diálogo para ingresar datos del libro
                dialogo = Datos()
                
                # Establecer el nombre del archivo como título predeterminado
                nombre_sin_extension = os.path.splitext(os.path.basename(archivo))[0]
                dialogo.titulo_input.setText(nombre_sin_extension)
                
                if dialogo.exec_() == QDialog.Accepted:
                    # Obtener los datos ingresados
                    titulo_libro, nombre_autor, nombre_genero = dialogo.obtener_datos()
                    
                    # Crear el libro en la base de datos
                    if crear_libro_pdf(
                        archivo,
                        titulo=titulo_libro,
                        nombre_autor=nombre_autor,
                        nombre_genero=nombre_genero,
                        paginas_leidas=0
                    ):
                        self.cargar_pdf_desde_db()
                        QMessageBox.information(
                            self,
                            "Éxito",
                            "Libro agregado correctamente."
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            "Error",
                            "No se pudo agregar el libro."
                        )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo agregar el libro.\nError: {e}")
        else:
            QMessageBox.warning(self, "Cancelado", "No se seleccionó ningún archivo.")  

    def abrir_pdf(self, item):
        """Abre el PDF seleccionado"""
        if not item:
            return
        
        ruta_pdf = item.data(Qt.UserRole)
        libro_id = item.data(Qt.UserRole + 1)
        
        if os.path.exists(ruta_pdf):
            viewer = PDFViewer(ruta_pdf, libro_id)
            viewer.exec_()
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo encontrar el archivo PDF."
            )
    
    def confirmar_eliminar_libro(self):
        """Confirma si el usuario quiere eliminar el libro"""
        sender = self.sender()
        if not sender:
            return
            
        id_libro = sender.property('id_libro')
        
        reply = QMessageBox.question(
            self,
            'Confirmar eliminación',
            '¿Estás seguro de que quieres eliminar este libro?\n\nEsta acción no se puede deshacer.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.eliminar_libro(id_libro)
    
    def eliminar_libro(self, id_libro):
        """Elimina un libro de la base de datos"""
        from crud import eliminar_libro
        
        if eliminar_libro(id_libro):
            # Actualizar la lista de PDFs
            self.cargar_pdf_desde_db()
            QMessageBox.information(
                self,
                "Éxito",
                "El libro ha sido eliminado correctamente."
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo eliminar el libro."
            )

    def cargar_pdf_desde_db(self):
        """Carga los PDFs desde la base de datos"""
        from crud import obtener_libros
        from db import PDF_FOLDER
        
        # Limpiar la lista actual
        self.pdf_list.clear()
        
        # Obtener todos los libros de la base de datos
        libros = obtener_libros()
        
        for libro in libros:
            # Crear widget contenedor para el item
            item_widget = QWidget()
            item_layout = QHBoxLayout(item_widget)
            item_layout.setContentsMargins(15, 5, 15, 5)
            
            # Label para el título
            title_label = QLabel(libro.titulo if libro.titulo else libro.archivo_pdf)
            title_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-size: 14px;
                }
            """)
            item_layout.addWidget(title_label)
            
            # Botón de eliminar
            delete_btn = QPushButton("×")
            delete_btn.setFixedSize(30, 30)
            delete_btn.setStyleSheet(self.delete_button_style)
            delete_btn.setCursor(Qt.PointingHandCursor)
            
            # Guardar el ID del libro en el botón
            delete_btn.setProperty('id_libro', libro.id_libro)
            delete_btn.clicked.connect(self.confirmar_eliminar_libro)
            
            item_layout.addWidget(delete_btn)
            
            # Crear y configurar el item
            item = QListWidgetItem()
            item.setSizeHint(item_widget.sizeHint())
            
            # Guardar datos en el item
            ruta_pdf = os.path.join(PDF_FOLDER, libro.archivo_pdf)
            if os.path.exists(ruta_pdf):
                item.setData(Qt.UserRole, ruta_pdf)
                item.setData(Qt.UserRole + 1, libro.id_libro)
                
                # Agregar item y widget a la lista
                self.pdf_list.addItem(item)
                self.pdf_list.setItemWidget(item, item_widget)



if __name__ == "__main__":  
    app = QApplication(sys.argv)
    window = BibliotecaApp()
    window.show()
    sys.exit(app.exec_())
