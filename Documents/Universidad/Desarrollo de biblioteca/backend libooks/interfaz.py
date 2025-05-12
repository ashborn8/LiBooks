from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem, QFrame,
    QFileDialog, QMessageBox, QDialog, QInputDialog, QMenu, QAction,
    QFormLayout, QComboBox, QDialogButtonBox, QCheckBox, QScrollArea, QStackedWidget, QGridLayout, QSizePolicy
)
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPixmap, QPainterPath, QFont
from PyQt5.QtCore import Qt, QSize
import psycopg2
import sys
import os
from crud import crear_coleccion, agregar_libro_a_coleccion

from pdf_viewer import PDFViewer

from datos import Datos
from PyQt5.QtGui import QFont, QIcon, QColor, QPixmap
from PyQt5.QtCore import Qt, QSize
import os

from crud import crear_libro_pdf

def crear_formulario_coleccion(parent):
    """Crea y devuelve el widget del formulario de creación de colecciones"""
    from crud import obtener_libros
    libros = obtener_libros()
    
    # Widget contenedor
    widget = QWidget()
    
    # Obtener referencia a la instancia de BibliotecaApp
    biblioteca_app = parent
    widget.setStyleSheet("""
        QLabel {
            color: white;
            font-size: 14px;
        }
        QLineEdit, QComboBox {
            background-color: #1A4D5B;
            color: white;
            border: 1px solid #2D7D8F;
            border-radius: 4px;
            padding: 8px;
            min-height: 30px;
            font-size: 14px;
        }
        QComboBox::drop-down {
            border: none;
            padding-right: 10px;
        }
        QComboBox QAbstractItemView {
            background-color: #1A4D5B;
            color: white;
            selection-background-color: #2D7D8F;
            padding: 5px;
        }
        QPushButton {
            background-color: #1A4D5B;
            color: white;
            border: 1px solid #2D7D8F;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
        }
        QPushButton:hover {
            background-color: #2D7D8F;
        }
    """)
    
    layout = QVBoxLayout(widget)
    
    # Título
    titulo_label = QLabel("Crear Colección")
    titulo_label.setFont(QFont("Arial", 16, QFont.Bold))
    titulo_label.setAlignment(Qt.AlignCenter)
    titulo_label.setStyleSheet("color: white; margin-bottom: 20px;")
    layout.addWidget(titulo_label)
    
    # Formulario
    form_layout = QFormLayout()
    form_layout.setSpacing(15)
    
    # Campo de título de la colección
    titulo_input = QLineEdit()
    titulo_input.setPlaceholderText("Ingrese el título de la colección")
    form_layout.addRow("Título de la colección:", titulo_input)
    
    # Lista para seleccionar múltiples libros
    libros_list = QListWidget()
    libros_list.setSelectionMode(QListWidget.MultiSelection)
    libros_list.setStyleSheet("""
        QListWidget {
            background-color: #1A4D5B;
            color: white;
            border: 1px solid #2D7D8F;
            border-radius: 4px;
            padding: 5px;
        }
        QListWidget::item:selected {
            background-color: #2D7D8F;
            color: white;
        }
    """)
    
    # Agregar libros a la lista
    for libro in libros:
        item = QListWidgetItem(libro.titulo)
        item.setData(Qt.UserRole, libro)
        libros_list.addItem(item)
    
    # Ajustar tamaño de la lista
    libros_list.setMinimumHeight(150)
    libros_list.setMaximumHeight(200)
    # Asegurar que el ancho sea consistente con los otros campos
    libros_list.setMinimumWidth(250)
    
    # Crear un widget contenedor con etiqueta
    libros_container = QWidget()
    libros_layout = QVBoxLayout(libros_container)
    libros_layout.setContentsMargins(0, 0, 0, 0)
    libros_layout.addWidget(QLabel("Seleccione uno o más libros:"))
    libros_layout.addWidget(libros_list)
    
    # Asegurar que el contenedor se expanda horizontalmente
    libros_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    
    # Agregar al formulario con la misma alineación que los otros campos
    form_layout.addRow("Libros:", libros_container)
    
    # Combo para seleccionar autor (opcional)
    autor_combo = QComboBox()
    autor_combo.addItem("Seleccionar autor (opcional)", None)
    autores = {}
    for libro in libros:
        if hasattr(libro, 'autor') and libro.autor and libro.autor.id_autor not in autores:
            autores[libro.autor.id_autor] = libro.autor
            autor_combo.addItem(libro.autor.nombre, libro.autor)
    form_layout.addRow("Agregar por autor (opcional):", autor_combo)
    
    # Combo para seleccionar género (opcional)
    genero_combo = QComboBox()
    genero_combo.addItem("Seleccionar género (opcional)", None)
    generos = {}
    for libro in libros:
        if hasattr(libro, 'genero') and libro.genero and libro.genero.id_genero not in generos:
            generos[libro.genero.id_genero] = libro.genero
            genero_combo.addItem(libro.genero.nombre, libro.genero)
    form_layout.addRow("Agregar por género (opcional):", genero_combo)
    
    # Botones
    btn_crear = QPushButton("Crear Colección")
    btn_cancelar = QPushButton("Cancelar")
    
    # Layout para los botones
    botones_layout = QHBoxLayout()
    botones_layout.addStretch()
    botones_layout.addWidget(btn_crear)
    botones_layout.addWidget(btn_cancelar)
    
    # Agregar todo al layout principal
    layout.addLayout(form_layout)
    layout.addStretch()
    layout.addLayout(botones_layout)
    
    # Función para manejar la creación de la colección
    def on_crear_clicked():
        titulo = titulo_input.text().strip()
        if not titulo:
            QMessageBox.warning(widget, "Error", "El título de la colección es obligatorio")
            return
            
        # Obtener los libros seleccionados de la lista
        libros_seleccionados = []
        for i in range(libros_list.count()):
            item = libros_list.item(i)
            if item.isSelected():
                libro = item.data(Qt.UserRole)
                libros_seleccionados.append(libro.id_libro)
        
        # Verificar que se haya seleccionado al menos un libro
        if not libros_seleccionados:
            QMessageBox.warning(widget, "Error", "Debes seleccionar al menos un libro")
            return
            
        # Obtener autor y género seleccionados (opcionales)
        autor_seleccionado = autor_combo.currentData()
        genero_seleccionado = genero_combo.currentData()
        
        # Si se seleccionó un autor o género, agregar esos libros también
        if autor_seleccionado or genero_seleccionado:
            from crud import obtener_libros
            libros = obtener_libros()
            for libro in libros:
                if (autor_seleccionado and libro.autor and libro.autor.id_autor == autor_seleccionado.id_autor) or \
                   (genero_seleccionado and libro.genero and libro.genero.id_genero == genero_seleccionado.id_genero):
                    if libro.id_libro not in libros_seleccionados:
                        libros_seleccionados.append(libro.id_libro)
        
        # Crear la colección en la base de datos
        from crud import session
        try:
            # Crear la colección
            if not crear_coleccion(titulo):
                QMessageBox.warning(widget, "Error", "Ya existe una colección con ese nombre")
                return
            
            # Obtener la colección recién creada
            from models import Coleccion
            coleccion = session.query(Coleccion).filter_by(nombre=titulo).first()
            
            if not coleccion:
                raise Exception("No se pudo obtener la colección recién creada")
            
            # Agregar los libros seleccionados a la colección
            for libro_id in libros_seleccionados:
                if not agregar_libro_a_coleccion(coleccion.id_coleccion, libro_id):
                    print(f"Advertencia: No se pudo agregar el libro con ID {libro_id} a la colección")
            
            # Confirmar los cambios
            session.commit()
            
            # Actualizar la lista de colecciones
            if hasattr(parent, 'actualizar_lista_colecciones'):
                parent.actualizar_lista_colecciones()
            
            # Cerrar el diálogo
            dialog = widget.parent()
            if isinstance(dialog, QDialog):
                dialog.accept()
            else:
                widget.setParent(None)
            
            # Mostrar mensaje de éxito
            QMessageBox.information(widget, "Éxito", f"Colección '{titulo}' creada correctamente con {len(libros_seleccionados)} libros")
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(widget, "Error", f"Ocurrió un error al crear la colección: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Conectar señales
    btn_crear.clicked.connect(on_crear_clicked)
    btn_cancelar.clicked.connect(lambda: widget.setParent(None))
    
    return widget


class BibliotecaApp(QWidget):
    def crear_icono_engranaje(self, size=24):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Configurar el pincel
        pen = QPen(QColor(255, 255, 255))  # Color blanco
        pen.setWidth(2)
        painter.setPen(pen)
        
        # Dibujar el círculo exterior
        painter.drawEllipse(2, 2, size-4, size-4)
        
        # Dibujar los dientes del engranaje
        for i in range(12):
            angle = i * 30  # 360/12 = 30 grados entre cada diente
            painter.save()
            painter.translate(size/2, size/2)
            painter.rotate(angle)
            # Convertir los valores a enteros usando int()
            painter.drawLine(0, -int(size/3), 0, -int(size/2))
            painter.restore()
        
        painter.end()
        return pixmap

    def mostrar_formulario_coleccion(self):
        """Muestra el formulario de creación de colección en el panel derecho"""
        # Limpiar el panel derecho
        self.limpiar_panel_derecho()
        
        # Crear y mostrar el formulario
        formulario = crear_formulario_coleccion(self)
        
        # Asegurarse de que el panel derecho tenga un layout
        if not self.panel_derecho.layout():
            self.panel_derecho.setLayout(QVBoxLayout())
        
        # Agregar el formulario al panel derecho
        self.panel_derecho.layout().addWidget(formulario)
        
        # Asegurarse de que el panel derecho sea visible
        self.panel_derecho.show()

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
        
        # Inicializar la lista de PDFs
        self.pdf_list = []
        
        # Inicializar diccionario de funciones CRUD
        from crud import crear_coleccion, obtener_colecciones, eliminar_coleccion
        self.funciones_crud = {
            'crear_coleccion': crear_coleccion,
            'obtener_colecciones': obtener_colecciones,
            'eliminar_coleccion': eliminar_coleccion
        }
        
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
        
        # Icono de libros
        icon = QLabel("📚")
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("font-size: 80px;")
        sidebar_layout.addWidget(icon)

        # Contenedor para el título y el botón de colecciones
        colecciones_header = QWidget()
        colecciones_layout = QHBoxLayout(colecciones_header)
        colecciones_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título de colecciones
        colecciones_label = QLabel("Colecciones")
        colecciones_label.setFont(QFont("Arial", 18, QFont.Bold))
        colecciones_label.setStyleSheet("color: white;")
        
        # Botón para agregar colección
        btn_agregar = QPushButton("+")
        btn_agregar.setFixedSize(30, 30)
        btn_agregar.setStyleSheet("""
            QPushButton {
                background-color: #7dd6a6;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6bc596;
            }
        """)
        btn_agregar.clicked.connect(self.mostrar_formulario_coleccion)
        
        # Agregar al layout
        colecciones_layout.addStretch()
        colecciones_layout.addWidget(colecciones_label)
        colecciones_layout.addWidget(btn_agregar)
        colecciones_layout.addStretch()
        
        sidebar_layout.addWidget(colecciones_header)

        # Diccionario para almacenar las colecciones y sus filtros
        self.colecciones = {}
        
        # Contenedor principal para las colecciones con scroll
        scroll_container = QScrollArea()
        scroll_container.setWidgetResizable(True)
        scroll_container.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #0F3444;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #2D7D8F;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Widget contenedor para los elementos de la colección
        self.colecciones_container = QWidget()
        self.colecciones_layout = QVBoxLayout(self.colecciones_container)
        self.colecciones_layout.setContentsMargins(5, 5, 5, 5)
        self.colecciones_layout.setSpacing(10)
        
        # Configurar el scroll area
        scroll_container.setWidget(self.colecciones_container)
        
        # Función para actualizar la lista de colecciones
        def actualizar_lista_colecciones():
            # Limpiar el layout actual
            while self.colecciones_layout.count() > 0:
                item = self.colecciones_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Obtener las colecciones de la base de datos
            from crud import obtener_colecciones
            from models import Coleccion
            
            try:
                colecciones = obtener_colecciones()
                
                # Agregar cada colección como un botón
                for coleccion in colecciones:
                    if not isinstance(coleccion, Coleccion):
                        continue
                        
                    # Crear un contenedor horizontal para el botón de colección y el botón de eliminar
                    coleccion_container = QWidget()
                    coleccion_layout = QHBoxLayout(coleccion_container)
                    coleccion_layout.setContentsMargins(0, 0, 0, 0)
                    coleccion_layout.setSpacing(5)
                    
                    # Botón de la colección
                    coleccion_widget = QPushButton(coleccion.nombre)
                    coleccion_widget.setStyleSheet("""
                        QPushButton {
                            background-color: rgba(45, 125, 143, 0.7);
                            color: white;
                            border: none;
                            border-radius: 12px;
                            padding: 10px 15px;
                            text-align: left;
                            font-size: 14px;
                            font-weight: 500;
                        }
                        QPushButton:hover {
                            background-color: rgba(45, 125, 143, 0.9);
                        }
                    """)
                    
                    # Botón de eliminar colección
                    btn_eliminar = QPushButton("×")
                    btn_eliminar.setFixedSize(30, 30)
                    btn_eliminar.setStyleSheet("""
                        QPushButton {
                            background-color: rgba(255, 82, 82, 0.7);
                            color: white;
                            border: none;
                            border-radius: 15px;
                            font-size: 18px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: rgba(255, 23, 68, 0.9);
                        }
                    """)
                    
                    # Conectar el clic del botón de eliminar
                    btn_eliminar.clicked.connect(lambda checked, id_coleccion=coleccion.id_coleccion, nombre_coleccion=coleccion.nombre: 
                                              self.confirmar_eliminar_coleccion(id_coleccion, nombre_coleccion))
                    
                    # Agregar los widgets al layout horizontal
                    coleccion_layout.addWidget(coleccion_widget, 1)  # El 1 es el factor de estiramiento
                    coleccion_layout.addWidget(btn_eliminar)
                    
                    # Mostrar una descripción de los filtros en el tooltip
                    tooltip = f"{coleccion.nombre}\n\nFiltros:"
                    if hasattr(coleccion, 'libros') and coleccion.libros:
                        tooltip += f"\n- Libro específico"
                    if hasattr(coleccion, 'filtro_autor_id') and coleccion.filtro_autor_id:
                        tooltip += f"\n- Mismo autor"
                    if hasattr(coleccion, 'filtro_genero_id') and coleccion.filtro_genero_id:
                        tooltip += f"\n- Mismo género"
                    coleccion_widget.setToolTip(tooltip)
                    
                    # Conectar el clic
                    filtros = {
                        'id_coleccion': coleccion.id_coleccion,
                        'libro_id': coleccion.libros[0].id_libro if hasattr(coleccion, 'libros') and coleccion.libros else None,
                        'autor_id': coleccion.filtro_autor_id if hasattr(coleccion, 'filtro_autor_id') else None,
                        'genero_id': coleccion.filtro_genero_id if hasattr(coleccion, 'filtro_genero_id') else None
                    }
                    coleccion_widget.clicked.connect(
                        lambda checked, f=filtros: self.aplicar_filtros_coleccion(f)
                    )
                    
                    self.colecciones_layout.addWidget(coleccion_container)
                
                # Añadir espaciador al final
                self.colecciones_layout.addStretch()
                
            except Exception as e:
                print(f"Error al cargar colecciones: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Llamar a la función para cargar las colecciones iniciales
        actualizar_lista_colecciones()
        
        # Guardar referencia a la función para usarla en otros métodos
        self.actualizar_lista_colecciones = actualizar_lista_colecciones
        
        # Añadir el contenedor con scroll al layout del panel izquierdo
        sidebar_layout.addWidget(scroll_container)
        sidebar_layout.addStretch()

        config_button = QPushButton("Configuraciones ⚙")
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

        # Panel derecho (contenido principal)
        self.panel_derecho = QWidget()
        self.panel_derecho.setStyleSheet("background-color: #0F3444;")
        self.right_layout = QVBoxLayout(self.panel_derecho)

        # Contenedor para el contenido dinámico
        self.contenido_dinamico = QStackedWidget()

        # Página principal (libros)
        self.pagina_libros = QWidget()
        libros_layout = QVBoxLayout(self.pagina_libros)
        libros_layout.setContentsMargins(20, 20, 20, 20)
        libros_layout.setSpacing(20)

        # Contenedor para la barra de búsqueda y botón de atrás
        header_container = QWidget()
        header_layout = QHBoxLayout(header_container)
        header_layout.setContentsMargins(0, 0, 0, 20)
        
        # Botón de Atrás (inicialmente oculto)
        self.btn_atras = QPushButton("← Atrás")
        self.btn_atras.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #7dd6a6;
                border: 1px solid #7dd6a6;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 14px;
                min-width: 80px;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: rgba(125, 214, 166, 0.1);
            }
        """)
        self.btn_atras.hide()
        
        # Conectar la señal de clic
        self.btn_atras.clicked.connect(self.mostrar_todos_los_libros)
        
        # Contenedor para la barra de búsqueda
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        # Barra de búsqueda
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar libros...")
        self.search_bar.setStyleSheet("""
            QLineEdit {
                background-color: #7dd6a6;
                color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 25px;
                font-size: 16px;
                min-width: 600px;
            }
            QLineEdit::placeholder {
                color: rgba(255, 255, 255, 0.7);
            }
        """)
        self.search_bar.returnPressed.connect(self.realizar_busqueda)
        self.search_bar.textChanged.connect(self.filtrar_libros)
        
        # Añadir la barra de búsqueda al layout
        search_layout.addWidget(self.search_bar)
        
        # Añadir widgets al layout del encabezado
        header_layout.addWidget(self.btn_atras)
        header_layout.addWidget(search_container, 1)  # El 1 hace que la barra de búsqueda ocupe el espacio restante
        
        # Añadir el contenedor del encabezado al layout principal
        libros_layout.addWidget(header_container)
        
        # Botón para agregar libro
        add_libro_btn = QPushButton("Añadir Libro  +")
        add_libro_btn.setFixedHeight(60)  
        add_libro_btn.setStyleSheet("""
            QPushButton {
                background-color: #3f6f75;
                color: white;
                font-size: 18px;
                border: 2px dashed #7dd6a6;
                border-radius: 25px;  /* La mitad de la altura del botón */
                padding: 12px 25px;
                min-width: 700px;
                max-width: 700px;  /* Asegura que el ancho no afecte el redondeo */
            }
            QPushButton:hover {
                background-color: #325961;
            }
        """)
        add_libro_btn.clicked.connect(self.agregar_libro_pdf)
        
        # Contenedor para centrar el botón
        btn_container = QWidget()
        btn_layout = QHBoxLayout(btn_container)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch()
        btn_layout.addWidget(add_libro_btn)
        btn_layout.addStretch()
        
        libros_layout.addWidget(btn_container)

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
            }
        """)
        
        # Conectar el evento de doble clic
        self.pdf_list.itemDoubleClicked.connect(self.abrir_pdf)
        
        # Configurar el scroll area para la lista de libros
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.pdf_list)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        list_layout.addWidget(scroll_area)
        libros_layout.addWidget(list_container)

        # Agregar páginas al stacked widget
        self.contenido_dinamico.addWidget(self.pagina_libros)

        # Configurar el layout principal del panel derecho
        self.right_layout.addWidget(self.contenido_dinamico)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        main_layout.addWidget(self.panel_derecho)
        

        
        # Cargar los libros al iniciar
        self.cargar_pdf_desde_db()

        # Lista para almacenar todos los libros
        self.todos_libros = []

        # Los libros se cargarán automáticamente al iniciar la aplicación
        # a través de la llamada a cargar_pdf_desde_db()

    def limpiar_panel_derecho(self):
        """Limpia el panel derecho, mostrando solo la página de libros"""
        # Eliminar todas las páginas excepto la primera (libros)
        while self.contenido_dinamico.count() > 1:
            widget = self.contenido_dinamico.widget(self.contenido_dinamico.count() - 1)
            self.contenido_dinamico.removeWidget(widget)
            widget.deleteLater()

        # Mostrar la página de libros
        if self.contenido_dinamico.count() > 0:
            self.contenido_dinamico.setCurrentIndex(0)

    def actualizar_lista_colecciones(self):
        """Actualiza la lista de colecciones en la interfaz"""
        # Limpiar el layout actual
        for i in reversed(range(self.colecciones_layout.count())): 
            widget = self.colecciones_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        # Obtener las colecciones de la base de datos
        from crud import obtener_colecciones
        from models import Coleccion
        
        try:
            colecciones = obtener_colecciones()
            
            # Agregar cada colección como un botón
            for coleccion in colecciones:
                if not isinstance(coleccion, Coleccion):
                    continue
                    
                coleccion_widget = QPushButton(coleccion.nombre)
                coleccion_widget.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(45, 125, 143, 0.7);
                        color: white;
                        border: none;
                        border-radius: 12px;
                        padding: 10px 15px;
                        text-align: left;
                        font-size: 14px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background-color: rgba(45, 125, 143, 0.9);
                    }
                """)
                
                # Conectar el clic para mostrar los libros de la colección
                coleccion_widget.clicked.connect(
                    lambda checked, c=coleccion: self.aplicar_filtros_coleccion({
                        'id_coleccion': c.id_coleccion
                    })
                )
                
                self.colecciones_layout.addWidget(coleccion_widget)
                
            # Asegurarse de que el contenedor se actualice
            self.colecciones_container.adjustSize()
            
        except Exception as e:
            print(f"Error al cargar colecciones: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def limpiar_libros(self):
        # Limpiar la lista de libros
        if hasattr(self, 'pdf_list') and self.pdf_list:
            self.pdf_list.clear()

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
        try:
            if not item:
                print("No se proporcionó ningún ítem")
                return
                
            ruta_pdf = item.data(Qt.UserRole)
            libro_id = item.data(Qt.UserRole + 1)
            
            print(f"Intentando abrir PDF. Ruta: {ruta_pdf}, ID: {libro_id}")
            
            if not ruta_pdf:
                QMessageBox.warning(
                    self,
                    "Error",
                    "No se ha especificado una ruta de archivo PDF."
                )
                return
                
            if not os.path.exists(ruta_pdf):
                QMessageBox.warning(
                    self,
                    "Archivo no encontrado",
                    f"No se pudo encontrar el archivo PDF:\n{ruta_pdf}"
                )
                return
                
            print(f"Creando visor PDF para: {ruta_pdf}")
            viewer = PDFViewer(ruta_pdf, libro_id)  # Pasamos el ID del libro
            print("Mostrando visor PDF...")
            viewer.exec_()
            print("Visor PDF cerrado")
        except Exception as e:
            print(f"Error al abrir el PDF: {str(e)}")
            QMessageBox.critical(
                self,
                "Error al abrir PDF",
                f"No se pudo abrir el archivo:\n{str(e)}"
            )

    def mostrar_dialogo_actualizar(self, id_libro):
        """Muestra un diálogo para actualizar la información del libro"""
        # Obtener los datos actuales del libro
        libro = self.obtener_libro(id_libro)

        if not libro:
            QMessageBox.warning(self, "Error", "No se pudo encontrar el libro en la base de datos")
            return

        # Crear el diálogo usando la clase Datos
        dialog = Datos()

        # Prellenar los campos con los datos actuales
        dialog.titulo_input.setText(libro.titulo)
        dialog.autor_input.setText(libro.autor)

        # Cambiar el título del diálogo
        dialog.setWindowTitle("Actualizar Libro")

        # Cambiar el texto del botón
        dialog.boton_guardar.setText("Actualizar")

        # Conectar el botón al método de actualización
        dialog.boton_guardar.clicked.disconnect()  # Desconectar el accept() original
        dialog.boton_guardar.clicked.connect(lambda: self.guardar_actualizacion(id_libro, dialog.titulo_input.text(), dialog.autor_input.text(), dialog))

        # Mostrar el diálogo
        dialog.exec_()

    def guardar_actualizacion(self, id_libro, nuevo_titulo, nuevo_autor, dialog):
        """Guarda los cambios en la base de datos"""
        try:
            from crud import actualizar_libro

            # Actualizar el libro usando la función de crud
            actualizar_libro(id_libro, titulo=nuevo_titulo, nombre_autor=nuevo_autor)

            # Actualizar la interfaz
            self.cargar_pdf_desde_db()

            QMessageBox.information(self, "Éxito", "Libro actualizado correctamente")
            dialog.accept()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al actualizar el libro: {str(e)}")

    def obtener_libro(self, id_libro):
        """Obtiene la información de un libro de la base de datos"""
        try:
            from crud import obtener_libros

            # Obtener todos los libros
            libros = obtener_libros()

            # Buscar el libro por ID
            libro = next((l for l in libros if l.id_libro == id_libro), None)

            if libro:
                return type('Libro', (object,), {
                    'id_libro': libro.id_libro,
                    'titulo': libro.titulo,
                    'autor': libro.autor.nombre if libro.autor else None,
                    'archivo_pdf': libro.archivo_pdf
                })()

            return None

        except Exception as e:
            print(f"Error al obtener el libro: {str(e)}")
            return None

    def confirmar_eliminar_libro(self, id_libro):
        """Confirma si el usuario quiere eliminar el libro"""
        reply = QMessageBox.question(
            self,
            'Confirmar eliminación',
            '¿Estás seguro de que quieres eliminar este libro?\n\nEsta acción no se puede deshacer.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.eliminar_libro(id_libro)

    def confirmar_eliminar_coleccion(self, id_coleccion, nombre_coleccion):
        """Muestra un diálogo de confirmación para eliminar una colección"""
        reply = QMessageBox.question(
            self,
            'Confirmar eliminación',
            f'¿Estás seguro de que quieres eliminar la colección "{nombre_coleccion}"?\n\nEsta acción no se puede deshacer.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.eliminar_coleccion(id_coleccion)

    def eliminar_coleccion(self, id_coleccion):
        """Elimina una colección de la base de datos"""
        from crud import eliminar_coleccion

        if eliminar_coleccion(id_coleccion):
            # Actualizar la lista de colecciones
            self.actualizar_lista_colecciones()
            QMessageBox.information(
                self,
                "Éxito",
                "La colección ha sido eliminada correctamente."
            )
        else:
            QMessageBox.warning(
                self,
                "Error",
                "No se pudo eliminar la colección. Asegúrate de que no esté siendo usada."
            )

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

    def mostrar_todos_los_libros(self):
        """Muestra todos los libros sin filtros"""
        self.btn_atras.hide()
        self.cargar_pdf_desde_db()
        
    def aplicar_filtros_coleccion(self, filtros):
        """Filtra los libros según los criterios de la colección"""
        from crud import obtener_libros, obtener_libros_en_coleccion
        
        # Si hay un ID de colección, obtener los libros de esa colección
        if 'id_coleccion' in filtros and filtros['id_coleccion'] is not None:
            libros = obtener_libros_en_coleccion(filtros['id_coleccion'])
        else:
            # Si no hay ID de colección, obtener todos los libros y aplicar otros filtros
            libros = obtener_libros()
            
            # Aplicar filtros de la colección
            if 'libro_id' in filtros and filtros['libro_id'] is not None:
                libros = [libro for libro in libros if hasattr(libro, 'id_libro') and libro.id_libro == filtros['libro_id']]
            if 'autor_id' in filtros and filtros['autor_id'] is not None:
                libros = [libro for libro in libros if hasattr(libro, 'autor') and libro.autor and libro.autor.id_autor == filtros['autor_id']]
            if 'genero_id' in filtros and filtros['genero_id'] is not None:
                libros = [libro for libro in libros if hasattr(libro, 'genero') and libro.genero and libro.genero.id_genero == filtros['genero_id']]
        
        # Limpiar y mostrar los libros filtrados
        self.limpiar_libros()
        for libro in libros:
            self.agregar_libro_a_lista(libro)
            
        # Mostrar el botón de atrás
        self.btn_atras.show()

    def cargar_pdf_desde_db(self, filtro=None):
        """Carga los PDFs desde la base de datos con opción de filtrado"""
        try:
            from crud import obtener_libros
            from db import PDF_FOLDER
            import os

            # Limpiar la lista actual
            self.limpiar_libros()

            # Obtener todos los libros de la base de datos
            libros = obtener_libros()
            libros_validos = []

            # Verificar qué libros tienen archivos PDF existentes
            for libro in libros:
                ruta_pdf = None
                if hasattr(libro, 'ruta_archivo') and libro.ruta_archivo:
                    ruta_pdf = libro.ruta_archivo
                elif hasattr(libro, 'archivo_pdf') and libro.archivo_pdf:
                    ruta_pdf = os.path.join(PDF_FOLDER, libro.archivo_pdf)
                
                if ruta_pdf and os.path.exists(ruta_pdf):
                    libros_validos.append(libro)
                else:
                    print(f"Advertencia: No se encontró el archivo PDF para el libro ID: {libro.id_libro if hasattr(libro, 'id_libro') else 'N/A'}")

            # Aplicar filtro si se especificó
            if filtro and filtro.strip():
                filtro = filtro.lower()
                libros_filtrados = []
                for libro in libros_validos:
                    titulo = libro.titulo.lower() if libro.titulo else ""
                    autor_nombre = libro.autor.nombre if hasattr(libro, 'autor') and libro.autor else ""
                    autor_nombre = autor_nombre.lower()
                    genero = libro.genero.nombre.lower() if hasattr(libro, 'genero') and libro.genero and hasattr(libro.genero, 'nombre') else ""

                    if (filtro in titulo) or (filtro in autor_nombre) or (genero and filtro in genero):
                        libros_filtrados.append(libro)
                libros_validos = libros_filtrados

            # Agregar solo los libros válidos a la lista
            for libro in libros_validos:
                self.agregar_libro_a_lista(libro)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar los libros: {str(e)}")
            print(f"Error al cargar PDFs: {e}")
            
    def agregar_libro_a_lista(self, libro):
        """Agrega un libro individual a la lista con el nuevo estilo"""
        try:
            # Crear un ítem personalizado para mostrar el libro
            item = QListWidgetItem()
            item.setSizeHint(QSize(0, 60))  # Altura fija para cada ítem
            
            # Crear un widget personalizado para el libro
            widget = QWidget()
            widget.setStyleSheet("""
                QWidget {
                    background-color: transparent;
                    border: none;
                }
            """)
            
            # Layout horizontal para el widget del libro
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(15, 5, 15, 5)
            layout.setSpacing(15)
            
            # Layout para la información del libro
            info_layout = QVBoxLayout()
            info_layout.setContentsMargins(0, 0, 0, 0)
            info_layout.setSpacing(2)
            
            # Crear un ícono de libro
            icon_label = QLabel()
            try:
                if os.path.exists("icono_libro.png"):
                    icon_pixmap = QPixmap("icono_libro.png").scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    icon_label.setPixmap(icon_pixmap)
            except:
                pass
            
            # Configurar etiquetas para mostrar la información del libro
            titulo = libro.titulo if hasattr(libro, 'titulo') and libro.titulo else "Sin título"
            titulo_label = QLabel(titulo)
            titulo_label.setStyleSheet("""
                QLabel {
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    background-color: transparent;
                }
            """)
            titulo_label.setWordWrap(True)
            titulo_label.setMaximumHeight(24)

            # Autor del libro
            autor_nombre = ""
            if hasattr(libro, 'autor') and libro.autor and hasattr(libro.autor, 'nombre') and libro.autor.nombre:
                autor_nombre = libro.autor.nombre
            
            autor_label = QLabel(f"Autor: {autor_nombre if autor_nombre else 'Desconocido'}")
            autor_label.setStyleSheet("""
                QLabel {
                    color: #CCCCCC;
                    font-size: 12px;
                    background-color: transparent;
                }
            """)
            autor_label.setMaximumHeight(18)
            
            # Añadir etiquetas al layout de información
            info_layout.addWidget(titulo_label)
            info_layout.addWidget(autor_label)
            
            # Añadir ícono y layout de información al layout principal
            layout.addWidget(icon_label)
            layout.addLayout(info_layout, 1)  # El 1 hace que el layout de información se expanda
            
            # Crear layout para los botones
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(5)
            
            # Botón de editar
            btn_editar = QPushButton("Editar")
            btn_editar.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 8px 20px;
                    font-size: 14px;
                    min-width: 5px;
                    min-height: 5px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #0D47A1;
                }
            """)
            
            # Botón de eliminar
            btn_eliminar = QPushButton("Eliminar")
            btn_eliminar.setStyleSheet("""
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border: none;
                    border-radius: 10px;
                    padding: 8px 20px;
                    font-size: 14px;
                    min-width: 5px;
                    min-height: 5px;
                    margin: 2px;
                }
                QPushButton:hover {
                    background-color: #D32F2F;
                }
                QPushButton:pressed {
                    background-color: #B71C1C;
                }
            """)
            
            # Configurar botones
            if hasattr(libro, 'id_libro'):
                btn_editar.clicked.connect(lambda checked, id=libro.id_libro: self.mostrar_dialogo_actualizar(id))
                btn_eliminar.clicked.connect(lambda checked, id=libro.id_libro: self.confirmar_eliminar_libro(id))
            else:
                btn_editar.setEnabled(False)
                btn_eliminar.setEnabled(False)
            
            # Añadir botones al layout de botones
            buttons_layout.addWidget(btn_editar)
            buttons_layout.addWidget(btn_eliminar)
            
            # Añadir layout de botones al layout principal
            layout.addLayout(buttons_layout)
            
            # Configurar el ítem
            self.pdf_list.addItem(item)
            self.pdf_list.setItemWidget(item, widget)
            
            # Almacenar datos en el ítem
            if hasattr(libro, 'id_libro'):
                item.setData(Qt.UserRole + 1, libro.id_libro)
                
            # Obtener la ruta del archivo PDF
            ruta_pdf = None
            if hasattr(libro, 'ruta_archivo') and libro.ruta_archivo:
                ruta_pdf = libro.ruta_archivo
            elif hasattr(libro, 'archivo_pdf') and libro.archivo_pdf:
                from db import PDF_FOLDER
                ruta_pdf = os.path.join(PDF_FOLDER, libro.archivo_pdf)
            
            print(f"Guardando ruta PDF: {ruta_pdf} para libro ID: {libro.id_libro if hasattr(libro, 'id_libro') else 'N/A'}")
            item.setData(Qt.UserRole, ruta_pdf)
                
        except Exception as e:
            print(f"Error al agregar libro a la lista: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error al agregar el libro a la lista:\n{str(e)}"
            )
    
    def on_item_double_clicked(self, item):
        """Maneja el evento de doble clic en un ítem de la lista"""
        if item:
            ruta_pdf = item.data(Qt.UserRole)
            libro_id = item.data(Qt.UserRole + 1)
            if ruta_pdf:
                print(f"Doble clic detectado. Abriendo PDF: {ruta_pdf}")
                print(f"ID del libro: {libro_id}")
                self.abrir_pdf(item)
            else:
                print("No se encontró la ruta del PDF en el ítem")
    
    def abrir_pdf_desde_ruta(self, ruta_pdf):
        """Método de compatibilidad que crea un ítem temporal"""
        item = QListWidgetItem()
        item.setData(Qt.UserRole, ruta_pdf)
        item.setData(Qt.UserRole + 1, 0)  # ID por defecto
        self.abrir_pdf(item)
            
    def filtrar_libros(self, texto):
        """Filtra los libros en tiempo real según el texto de búsqueda"""
        self.cargar_pdf_desde_db(filtro=texto)
        
    def realizar_busqueda(self):
        """Método para manejar la búsqueda al presionar Enter"""
        texto = self.search_input.text()
        self.filtrar_libros(texto)

if __name__ == "__main__":  
    app = QApplication(sys.argv)
    window = BibliotecaApp()
    window.show()
    sys.exit(app.exec_())
