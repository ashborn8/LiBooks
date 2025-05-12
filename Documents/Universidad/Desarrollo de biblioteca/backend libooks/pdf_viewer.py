from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QListWidgetItem, QInputDialog, QMessageBox,
                             QLineEdit, QLabel, QTextBrowser, QTextEdit, QScrollArea, QWidget)
from PyQt5.QtCore import Qt, QEvent, QTimer, QDateTime
from PyQt5.QtGui import QImage, QPixmap, QFont
import fitz
import os
from crud import actualizar_paginas_leidas, obtener_paginas_leidas, crear_nota, obtener_notas_por_libro, actualizar_nota, eliminar_nota

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
        self.save_timer.setInterval(1000) 
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
        
        # Botón de notas
        self.notes_btn = QPushButton("📝 Notas")
        self.notes_btn.setToolTip("Ver y agregar notas")
        self.notes_btn.clicked.connect(self.mostrar_notas)
        
        toolbar.addStretch()
        toolbar.addWidget(self.notes_btn)
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

    def mostrar_notas(self):
        """Muestra el diálogo de notas"""
        if not self.libro_id:
            QMessageBox.warning(self, "Error", "No se puede acceder a las notas sin un ID de libro válido")
            return
            
        dialog = NotasDialog(self.libro_id, self)
        dialog.exec_()
    
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


class NotasDialog(QDialog):
    """Diálogo para ver y agregar notas"""
    def __init__(self, libro_id, parent=None):
        super().__init__(parent)
        self.libro_id = libro_id
        self.setWindowTitle("Notas del Libro")
        self.setMinimumSize(800, 600)
        
        # Estilos CSS
        self.setStyleSheet("""
            QDialog {
                background-color: #1A4D5B;
                color: #FFFFFF;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QListWidget {
                background-color: #0F3444;
                border: 1px solid #518C7A;
                border-radius: 5px;
                padding: 5px;
                color: #FFFFFF;
                font-size: 14px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #518C7A;
                background-color: #0F3444;
            }
            QListWidget::item:selected {
                background-color: #518C7A;
                color: white;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: #3f6f75;
            }
            QPushButton {
                background-color: #0F3444;
                color: white;
                border: 1px solid #518C7A;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #518C7A;
            }
            QPushButton:pressed {
                background-color: #3f6f75;
            }
            QTextEdit, QTextBrowser {
                background-color: #0F3444;
                color: #FFFFFF;
                border: 1px solid #518C7A;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
        """)
        
        # Layout principal
        main_layout = QHBoxLayout(self)
        
        # Panel izquierdo - Lista de notas
        left_panel = QVBoxLayout()
        
        # Título
        title_label = QLabel("Tus Notas")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #7DD6A6;
                padding: 10px 0;
            }
        """)
        left_panel.addWidget(title_label)
        
        # Lista de notas
        self.notas_list = QListWidget()
        self.notas_list.setMinimumWidth(250)
        self.notas_list.itemClicked.connect(self.mostrar_nota_seleccionada)
        left_panel.addWidget(self.notas_list)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ Nueva Nota")
        self.add_btn.clicked.connect(self.agregar_nota)
        
        self.delete_btn = QPushButton("🗑️ Eliminar")
        self.delete_btn.clicked.connect(self.eliminar_nota)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.delete_btn)
        left_panel.addLayout(btn_layout)
        
        # Panel derecho - Vista previa de la nota
        right_panel = QVBoxLayout()
        
        # Título de la nota seleccionada
        self.note_title = QLabel("Selecciona una nota")
        self.note_title.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #7DD6A6;
                padding: 10px 0;
            }
        """)
        
        # Fecha de creación
        self.note_date = QLabel("")
        self.note_date.setStyleSheet("""
            QLabel {
                color: #AAAAAA;
                font-size: 12px;
                padding-bottom: 10px;
            }
        """)
        
        # Contenido de la nota
        self.note_content = QTextBrowser()
        self.note_content.setReadOnly(True)
        self.note_content.setStyleSheet("""
            QTextBrowser {
                background-color: #0F3444;
                border: 1px solid #518C7A;
                border-radius: 5px;
                padding: 15px;
                color: #FFFFFF;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        
        # Botón de editar
        self.edit_btn = QPushButton("✏️ Editar Nota")
        self.edit_btn.clicked.connect(self.editar_nota_actual)
        self.edit_btn.setVisible(False)
        
        right_panel.addWidget(self.note_title)
        right_panel.addWidget(self.note_date)
        right_panel.addWidget(self.note_content, 1)  # Estirar el contenido
        right_panel.addWidget(self.edit_btn, 0, Qt.AlignRight)
        
        # Agregar paneles al layout principal
        main_layout.addLayout(left_panel, 1)  # 30% del ancho
        main_layout.addLayout(right_panel, 2)  # 70% del ancho
        
        # Cargar notas existentes
        self.cargar_notas()
        
        # Conectar doble clic después de cargar las notas
        self.notas_list.itemDoubleClicked.connect(self.editar_nota_actual)
    
    def cargar_notas(self):
        """Carga las notas del libro actual"""
        self.notas_list.clear()
        self.notas = obtener_notas_por_libro(self.libro_id)
        
        for nota in self.notas:
            # Formato de fecha más legible
            fecha_formateada = nota.fecha_creacion.strftime('%d %b %Y %H:%M')
            
            # Crear un ítem personalizado
            item = QListWidgetItem(f"{nota.titulo}")
            item.setData(Qt.UserRole, nota.id_nota)
            item.setData(Qt.UserRole + 1, nota)  # Guardar el objeto nota completo
            
            # Establecer tooltip con la fecha de creación
            item.setToolTip(f"Creada: {fecha_formateada}")
            
            self.notas_list.addItem(item)
        
        # Limpiar la vista previa si no hay notas
        if not self.notas:
            self.note_title.setText("No hay notas")
            self.note_date.clear()
            self.note_content.clear()
            self.edit_btn.setVisible(False)
    
    def agregar_nota(self):
        """Abre un diálogo para agregar una nueva nota"""
        # Crear diálogo personalizado
        dialog = QDialog(self)
        dialog.setWindowTitle("Nueva Nota")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1A4D5B;
                color: white;
            }
            QLabel {
                color: #7DD6A6;
                font-size: 14px;
                margin-bottom: 5px;
            }
            QLineEdit, QTextEdit {
                background-color: #0F3444;
                border: 1px solid #518C7A;
                border-radius: 5px;
                color: white;
                padding: 8px;
                margin-bottom: 15px;
            }
            QPushButton {
                background-color: #0F3444;
                color: white;
                border: 1px solid #518C7A;
                border-radius: 15px;
                padding: 8px 20px;
                min-width: 100px;
                margin: 0 5px;
            }
            QPushButton:hover {
                background-color: #518C7A;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Título
        layout.addWidget(QLabel("Título:"))
        titulo_edit = QLineEdit()
        titulo_edit.setPlaceholderText("Ingresa un título para la nota")
        layout.addWidget(titulo_edit)
        
        # Contenido
        layout.addWidget(QLabel("Contenido:"))
        contenido_edit = QTextEdit()
        contenido_edit.setPlaceholderText("Escribe el contenido de tu nota aquí...")
        contenido_edit.setMinimumHeight(200)
        layout.addWidget(contenido_edit)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(dialog.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            titulo = titulo_edit.text().strip()
            contenido = contenido_edit.toPlainText().strip()
            
            if not titulo:
                QMessageBox.warning(self, "Error", "El título no puede estar vacío")
                return
                
            try:
                crear_nota(titulo, self.libro_id, contenido)
                self.cargar_notas()
                # Seleccionar la nueva nota
                if self.notas_list.count() > 0:
                    self.notas_list.setCurrentRow(0)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo crear la nota: {str(e)}")
    
    def mostrar_nota_seleccionada(self, item):
        """Muestra la nota seleccionada en el panel de vista previa"""
        if not item:
            return
            
        nota = item.data(Qt.UserRole + 1)  # Obtenemos el objeto nota completo
        if not nota:
            return
            
        self.note_title.setText(nota.titulo)
        self.note_date.setText(f"Creada: {nota.fecha_creacion.strftime('%d/%m/%Y %H:%M')}")
        self.note_content.setPlainText(nota.contenido)
        self.edit_btn.setVisible(True)
        self.current_note_id = nota.id_nota
    
    def editar_nota_actual(self):
        """Edita la nota actualmente seleccionada"""
        current_item = self.notas_list.currentItem()
        if not current_item:
            return
            
        self.editar_nota(current_item)
    
    def editar_nota(self, item):
        """Edita una nota existente"""
        nota = item.data(Qt.UserRole + 1)  # Obtenemos el objeto nota completo
        if not nota:
            return
            
        # Crear diálogo de edición
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Editar Nota: {nota.titulo}")
        dialog.setMinimumWidth(500)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1A4D5B;
                color: white;
            }
            QLabel {
                color: #7DD6A6;
                font-size: 14px;
                margin-bottom: 5px;
            }
            QLineEdit, QTextEdit {
                background-color: #0F3444;
                border: 1px solid #518C7A;
                border-radius: 5px;
                color: white;
                padding: 8px;
                margin-bottom: 15px;
            }
            QTextEdit {
                min-height: 200px;
            }
            QPushButton {
                background-color: #0F3444;
                color: white;
                border: 1px solid #518C7A;
                border-radius: 15px;
                padding: 8px 20px;
                min-width: 100px;
                margin: 0 5px;
            }
            QPushButton:hover {
                background-color: #518C7A;
            }
        """)
        
        layout = QVBoxLayout(dialog)
        
        # Título
        titulo_edit = QLineEdit()
        titulo_edit.setText(nota.titulo)
        layout.addWidget(QLabel("Título:"))
        layout.addWidget(titulo_edit)
        
        # Contenido
        contenido_edit = QTextEdit()
        contenido_edit.setPlainText(nota.contenido)
        layout.addWidget(QLabel("Contenido:"))
        layout.addWidget(contenido_edit)
        
        # Botones
        btn_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(dialog.reject)
        
        save_btn = QPushButton("Guardar Cambios")
        save_btn.clicked.connect(dialog.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            nuevo_titulo = titulo_edit.text().strip()
            nuevo_contenido = contenido_edit.toPlainText().strip()
            
            if not nuevo_titulo:
                QMessageBox.warning(self, "Error", "El título no puede estar vacío")
                return
                
            try:
                # Solo actualizar si hay cambios
                if nuevo_titulo != nota.titulo or nuevo_contenido != nota.contenido:
                    actualizar_nota(nota.id_nota, nuevo_titulo, nuevo_contenido)
                    self.cargar_notas()
                    # Actualizar la vista previa
                    for i in range(self.notas_list.count()):
                        current_item = self.notas_list.item(i)
                        if current_item.data(Qt.UserRole) == nota.id_nota:
                            self.notas_list.setCurrentItem(current_item)
                            self.mostrar_nota_seleccionada(current_item)
                            break
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo actualizar la nota: {str(e)}")
                import traceback
                print(traceback.format_exc())
    
    def eliminar_nota(self):
        """Elimina la nota seleccionada"""
        current_item = self.notas_list.currentItem()
        if not current_item:
            return
            
        nota_id = current_item.data(Qt.UserRole)
        if not nota_id:
            return
            
        # Obtener el título de la nota para mostrarlo en el mensaje
        titulo_nota = current_item.text()
        
        # Crear un mensaje más descriptivo
        mensaje = (
            f"¿Estás seguro de que deseas eliminar la nota?\n\n"
            f"Título: {titulo_nota}\n\n"
            "Esta acción no se puede deshacer."
        )
        
        # Crear el cuadro de diálogo personalizado
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle("Confirmar eliminación")
        msg_box.setText("Eliminar nota")
        msg_box.setInformativeText(mensaje)
        
        # Configurar botones personalizados
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        
        # Establecer el estilo del diálogo
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #1A4D5B;
                color: white;
            }
            QLabel {
                color: white;
            }
            QPushButton {
                background-color: #0F3444;
                color: white;
                border: 1px solid #518C7A;
                border-radius: 10px;
                padding: 5px 15px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #518C7A;
            }
        """)
        
        # Mostrar el diálogo y obtener la respuesta
        reply = msg_box.exec_()
        
        if reply == QMessageBox.Yes:
            try:
                eliminar_nota(nota_id)
                self.cargar_notas()
                # Limpiar la vista previa después de eliminar
                self.note_title.setText("Selecciona una nota")
                self.note_date.clear()
                self.note_content.clear()
                self.edit_btn.setVisible(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo eliminar la nota: {str(e)}")
        

