import PyPDF2
import os

class CVProcessor:
    def __init__(self):
        pass

    def process_cv(self, cv_input: str) -> str:
        """
        Process CV from either PDF file path or pasted text
        Returns extracted text
        """
        # Check if input is a file path
        if os.path.isfile(cv_input):
            if cv_input.lower().endswith('.pdf'):
                return self._extract_from_pdf(cv_input)
            elif cv_input.lower().endswith('.txt'):
                return self._extract_from_txt(cv_input)
            else:
                # Try reading as text file anyway
                try:
                    return self._extract_from_txt(cv_input)
                except:
                    return cv_input
        else:
            # Assume it's pasted text
            return cv_input

    def _extract_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""

                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"

                return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {e}")

    def _extract_from_txt(self, txt_path: str) -> str:
        """Extract text from TXT file"""
        try:
            with open(txt_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error reading text file: {e}")
