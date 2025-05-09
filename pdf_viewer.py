from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QImage, QPixmap
import fitz
import os
from crud import actualizar_paginas_leidas, obtener_paginas_leidas

class PDFViewer(QDialog):
    def __init__(self, pdf_path, libro_id=None):
        super().__init__()
        self.pdf_path = pdf_path
        self.libro_id = libro_id
        self.zoom_level = 1.0
        self.doc = None
        self.current_page = 0
        
        # Timer para guardar el progreso
        self.save_timer = QTimer()
        self.save_timer.setInterval(1000)  # Guardar cada segundo
        self.save_timer.timeout.connect(self.save_reading_progress)
        
        # Configurar ventana
        self.setWindowTitle("Visualizador de PDF")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("""
            QDialog { 
                background-color: #1A4D5B; 
            }
            QLabel { 
                color: black;
                font-size: 14px;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
                margin: 10px;
            }
            QPushButton {
                background-color: #0F3444;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #518C7A;
            }
            QScrollArea { 
                border: none;
                background-color: #1A4D5B;
            }
            QScrollBar:vertical {
                background-color: #0F3444;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #518C7A;
                border-radius: 5px;
            }
        """)
        
        # Crear layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Crear toolbar
        toolbar = QHBoxLayout()
        toolbar.setContentsMargins(5, 5, 5, 5)
        
        # Botón de pantalla completa
        self.fullscreen_btn = QPushButton("⛶")
        self.fullscreen_btn.setFixedWidth(50)
        self.fullscreen_btn.setToolTip("Pantalla Completa (F11)")
        self.fullscreen_btn.clicked.connect(self.toggle_fullscreen)
        toolbar.addStretch()
        toolbar.addWidget(self.fullscreen_btn)
        
        layout.addLayout(toolbar)
        
        # Crear área de visualización
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(self.scroll_area)
        
        # Crear contenedor para las páginas
        self.page_container = QWidget()
        self.page_layout = QVBoxLayout(self.page_container)
        self.page_layout.setContentsMargins(0, 0, 0, 0)
        self.page_layout.setSpacing(0)
        self.page_layout.setAlignment(Qt.AlignHCenter)
        self.scroll_area.setWidget(self.page_container)
        
        # Instalar event filter para zoom
        self.scroll_area.viewport().installEventFilter(self)
        
        # Conectar señal de scroll
        self.scroll_area.verticalScrollBar().valueChanged.connect(self.on_scroll)
        
        # Cargar el PDF
        self.load_pdf()
        
        # Restaurar posición de lectura
        if self.libro_id:
            self.restore_reading_progress()
    
    def eventFilter(self, obj, event):
        if obj == self.scroll_area.viewport() and event.type() == QEvent.Wheel:
            if event.modifiers() & Qt.ControlModifier:
                delta = event.angleDelta().y()
                if delta > 0:
                    self.zoom_level = min(5.0, self.zoom_level * 1.2)
                else:
                    self.zoom_level = max(0.1, self.zoom_level / 1.2)
                self.load_all_pages()
                return True
        return super().eventFilter(obj, event)
    
    def load_pdf(self):
        try:
            if os.path.exists(self.pdf_path):
                self.doc = fitz.open(self.pdf_path)
                self.total_pages = len(self.doc)
                self.load_all_pages()
        except Exception as e:
            print(f"Error al cargar el PDF: {e}")
            self.doc = None
    
    def load_all_pages(self):
        if not self.doc:
            return
            
        try:
            # Limpiar el layout existente
            while self.page_layout.count():
                item = self.page_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
            
            # Cargar cada página
            for page_num in range(self.total_pages):
                page_label = QLabel()
                page_label.setAlignment(Qt.AlignCenter)
                
                page = self.doc.load_page(page_num)
                zoom = fitz.Matrix(self.zoom_level, self.zoom_level)
                pix = page.get_pixmap(matrix=zoom)
                
                img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(img)
                
                page_label.setPixmap(pixmap)
                self.page_layout.addWidget(page_label)
                
        except Exception as e:
            print(f"Error al cargar páginas: {e}")

    def toggle_fullscreen(self):
        """Cambia entre pantalla completa y normal"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def on_scroll(self):
        """Detecta cambios en el scroll y calcula la página actual"""
        if not self.doc:
            return
            
        scroll_pos = self.scroll_area.verticalScrollBar().value()
        total_height = self.scroll_area.verticalScrollBar().maximum()
        
        if total_height > 0:
            # Calcular qué página está más visible
            page_heights = []
            total_height = 0
            
            # Obtener altura de cada página
            for i in range(self.page_layout.count()):
                widget = self.page_layout.itemAt(i).widget()
                if widget:
                    height = widget.height()
                    page_heights.append((total_height, total_height + height))
                    total_height += height
            
            # Encontrar la página más visible
            viewport_top = scroll_pos
            viewport_bottom = viewport_top + self.scroll_area.height()
            
            max_visible = 0
            current_page = 0
            
            for i, (start, end) in enumerate(page_heights):
                visible_top = max(viewport_top, start)
                visible_bottom = min(viewport_bottom, end)
                visible_height = max(0, visible_bottom - visible_top)
                
                if visible_height > max_visible:
                    max_visible = visible_height
                    current_page = i
            
            if current_page != self.current_page:
                self.current_page = current_page
                self.save_timer.start()
    
    def save_reading_progress(self):
        """Guarda la página actual"""
        if self.libro_id:
            try:
                actualizar_paginas_leidas(self.libro_id, self.current_page)
            except Exception as e:
                print(f"Error al guardar progreso: {e}")
            finally:
                self.save_timer.stop()
    
    def restore_reading_progress(self):
        """Restaura la última página leída"""
        try:
            pagina = obtener_paginas_leidas(self.libro_id)
            if pagina is not None and pagina > 0:
                QTimer.singleShot(500, lambda: self.scroll_to_page(pagina))
        except Exception as e:
            print(f"Error al restaurar progreso: {e}")
    
    def scroll_to_page(self, page_num):
        """Hace scroll a una página específica"""
        try:
            if 0 <= page_num < self.page_layout.count():
                widget = self.page_layout.itemAt(page_num).widget()
                if widget:
                    self.scroll_area.ensureWidgetVisible(widget)
        except Exception as e:
            print(f"Error al hacer scroll: {e}")
    
    def closeEvent(self, event):
        # Guardar progreso antes de cerrar
        if self.libro_id:
            self.save_reading_progress()
        
        if self.doc:
            try:
                self.doc.close()
            except:
                pass
        event.accept()
        

