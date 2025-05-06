from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout

class Datos(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Información del Libro")
        self.setGeometry(400, 400, 400, 200)

        layout = QVBoxLayout()

        self.label_nombre = QLabel("Nombre del Libro:")
        self.input_nombre = QLineEdit()

        self.label_autor = QLabel("Nombre del Autor:")
        self.input_autor = QLineEdit()

        self.label_genero = QLabel("Género Literario:")
        self.input_genero = QLineEdit()

        self.boton_guardar = QPushButton("Guardar")
        self.boton_guardar.clicked.connect(self.accept)

        layout.addWidget(self.label_nombre)
        layout.addWidget(self.input_nombre)
        layout.addWidget(self.label_autor)
        layout.addWidget(self.input_autor)
        layout.addWidget(self.label_genero)
        layout.addWidget(self.input_genero)
        layout.addWidget(self.boton_guardar)

        self.setLayout(layout)

    def obtener_datos(self):
        return self.input_nombre.text(), self.input_autor.text(), self.input_genero.text()
