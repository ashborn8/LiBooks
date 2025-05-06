from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                           QLabel, QTextEdit, QSlider)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pdfplumber
import os

class PDFViewer(QDialog):
    def __init__(self, pdf_path):
        super().__init__()
        self.pdf_path = pdf_path
        self.setWindowTitle("Visualizador de PDF")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #0F3444;")
        self.current_page = 0
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # Barra superior con información
        top_bar = QHBoxLayout()
        
        self.page_label = QLabel("Página 1")
        self.page_label.setStyleSheet("color: white;")
        self.page_label.setFont(QFont("Arial", 12))
        top_bar.addWidget(self.page_label)
        
        # Botones de navegación
        nav_layout = QHBoxLayout()
        
        self.prev_btn = QPushButton("<<")
        self.prev_btn.clicked.connect(self.prev_page)
        self.prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #518C7A;
                color: white;
                border: none;
                padding: 5px 10px;
            }
        """)
        nav_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton(">>")
        self.next_btn.clicked.connect(self.next_page)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #518C7A;
                color: white;
                border: none;
                padding: 5px 10px;
            }
        """)
        nav_layout.addWidget(self.next_btn)
        
        top_bar.addLayout(nav_layout)
        layout.addLayout(top_bar)
        
        # Área de visualización
        self.text_edit = QTextEdit()
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border-radius: 10px;
                color: black;
                font-family: Arial;
            }
            QScrollBar:vertical {
                background-color: #73C3AD;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background-color: #518C7A;
                min-height: 20px;
            }
        """)
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)
        
        # Slider para cambiar el tamaño del texto
        size_layout = QHBoxLayout()
        
        size_label = QLabel("Tamaño de texto:")
        size_label.setStyleSheet("color: white;")
        size_layout.addWidget(size_label)
        
        self.size_slider = QSlider(Qt.Horizontal)
        self.size_slider.setRange(10, 30)
        self.size_slider.setValue(16)
        self.size_slider.valueChanged.connect(self.update_text_size)
        size_layout.addWidget(self.size_slider)
        
        layout.addLayout(size_layout)
        
        self.setLayout(layout)
        self.show_current_page()
        
    def show_current_page(self):
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                page = pdf.pages[self.current_page]
                text = page.extract_text()
                
            # Actualizar la etiqueta de página
            self.page_label.setText(f"Página {self.current_page + 1} de {len(pdf.pages)}")
            
            # Actualizar el contenido
            self.text_edit.setFont(QFont("Arial", self.size_slider.value()))
            self.text_edit.setText(text)
            
        except Exception as e:
            print(f"Error al mostrar la página: {e}")
            
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.show_current_page()
    
    def next_page(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            if self.current_page < len(pdf.pages) - 1:
                self.current_page += 1
                self.show_current_page()
    
    def update_text_size(self, value):
        self.text_edit.setFont(QFont("Arial", value))
