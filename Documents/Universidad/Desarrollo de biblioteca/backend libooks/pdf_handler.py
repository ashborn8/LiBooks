from PyPDF2 import PdfReader
from pdfplumber import open as pdf_open
import json
from datetime import datetime

class PDFHandler:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.reader = PdfReader(pdf_path)
        self.num_pages = len(self.reader.pages)
        self.session_data = {}
        
    def get_text_from_page(self, page_number):
        """Obtiene el texto de una página específica"""
        if 0 <= page_number < self.num_pages:
            with pdf_open(self.pdf_path) as pdf:
                page = pdf.pages[page_number]
                return page.extract_text()
        return None
    
    def get_metadata(self):
        """Obtiene los metadatos del PDF"""
        return self.reader.metadata
    
    def save_session(self, current_page, bookmarks=None):
        """Guarda el estado actual de lectura"""
        self.session_data = {
            'current_page': current_page,
            'bookmarks': bookmarks or [],
            'last_read': datetime.now().isoformat()
        }
        return self.session_data
    
    def load_session(self):
        """Carga el estado de lectura previo"""
        return self.session_data
    
    def get_page_range(self, start_page, end_page):
        """Obtiene el texto de un rango de páginas"""
        if 0 <= start_page < end_page < self.num_pages:
            text = ""
            with pdf_open(self.pdf_path) as pdf:
                for page in pdf.pages[start_page:end_page]:
                    text += page.extract_text() + "\n"
            return text
        return None
