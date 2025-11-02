"""
Utility module for PDF parsing and text extraction
"""
import PyPDF2
from pathlib import Path
from typing import Optional


class PDFParser:
    """Parser for extracting text from PDF files"""

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
        """
        Extract text content from a PDF file

        Args:
            pdf_path: Path to the PDF file

        Returns:
            Extracted text or None if extraction fails
        """
        try:
            pdf_file = Path(pdf_path)

            if not pdf_file.exists():
                print(f"Error: PDF file not found at {pdf_path}")
                return None

            if not pdf_file.suffix.lower() == '.pdf':
                print(f"Error: File is not a PDF: {pdf_path}")
                return None

            text_content = []

            with open(pdf_file, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                # Extract text from all pages
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_content.append(page_text)
                    except Exception as e:
                        print(f"Warning: Could not extract text from page {page_num + 1}: {str(e)}")
                        continue

            if not text_content:
                print("Warning: No text content extracted from PDF")
                return None

            return "\n\n".join(text_content)

        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return None

    @staticmethod
    def parse_cv(pdf_path: str) -> dict:
        """
        Parse a CV/resume PDF and extract structured information

        Args:
            pdf_path: Path to the CV PDF file

        Returns:
            Dictionary with extracted CV information
        """
        text = PDFParser.extract_text_from_pdf(pdf_path)

        if not text:
            return {
                'raw_text': '',
                'success': False,
                'error': 'Failed to extract text from PDF'
            }

        return {
            'raw_text': text,
            'success': True,
            'page_count': text.count('\n\n') + 1,
            'char_count': len(text),
            'word_count': len(text.split())
        }
