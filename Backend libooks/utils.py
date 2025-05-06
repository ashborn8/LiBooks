import tkinter as tk
from tkinter import filedialog

def seleccionar_pdf():
    try:
        print("Iniciando selección de PDF...")
        root = tk.Tk()
        root.withdraw()  
        print("Abriendo diálogo de selección...")
        ruta_pdf = filedialog.askopenfilename(
            title="Selecciona un archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        print(f"Ruta seleccionada: {ruta_pdf}")
        return ruta_pdf
    except Exception as e:
        print(f"Error al seleccionar PDF: {e}")
        return None
