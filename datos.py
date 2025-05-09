from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

class Datos(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Información del Libro")
        self.setGeometry(400, 400, 400, 300)
        self.setStyleSheet("""
            QDialog {
                background-color: #0F3444;
            }
            QLabel {
                color: white;
                font-size: 14px;
                margin-top: 10px;
            }
            QLineEdit {
                background-color: #1A4D5B;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
                font-size: 14px;
                margin-bottom: 5px;
            }
            QLineEdit:focus {
                background-color: #518C7A;
            }
            QPushButton {
                background-color: #73C3AD;
                color: white;
                border: none;
                border-radius: 15px;
                padding: 10px;
                font-size: 14px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #518C7A;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Título del libro
        self.label_titulo = QLabel("Título del Libro:")
        self.titulo_input = QLineEdit()
        layout.addWidget(self.label_titulo)
        layout.addWidget(self.titulo_input)

        # Autor
        self.label_autor = QLabel("Autor:")
        self.autor_input = QLineEdit()
        layout.addWidget(self.label_autor)
        layout.addWidget(self.autor_input)

        # Género
        self.label_genero = QLabel("Género:")
        self.genero_input = QLineEdit()
        layout.addWidget(self.label_genero)
        layout.addWidget(self.genero_input)

        # Botón guardar
        self.boton_guardar = QPushButton("Guardar")
        self.boton_guardar.clicked.connect(self.accept)
        layout.addWidget(self.boton_guardar)

        self.setLayout(layout)

    def obtener_datos(self):
        return self.titulo_input.text(), self.autor_input.text(), self.genero_input.text()
