# backend/utils.py
"""
Utility module for PDF parsing, text extraction, and ID validation
"""
# ----------------------------------------------------------------------
# 1. Use the modern pypdf package (PyPDF2 is now deprecated)
# ----------------------------------------------------------------------
from pypdf import PdfReader               
from pathlib import Path
from typing import Optional
from bson import ObjectId
from fastapi import HTTPException
from jose import JWTError, jwt
from config import settings  

# ----------------------------------------------------------------------
# PDFParser – unchanged logic, only import changed
# ----------------------------------------------------------------------
class PDFParser:
    """Parser for extracting text from PDF files"""

    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
        try:
            pdf_file = Path(pdf_path)

            if not pdf_file.exists():
                print(f"Error: PDF file not found at {pdf_path}")
                return None

            if pdf_file.suffix.lower() != ".pdf":
                print(f"Error: File is not a PDF: {pdf_path}")
                return None

            text_content: list[str] = []
            reader = PdfReader(pdf_file)                 # <-- NEW
            print(f"PDF has {len(reader.pages)} pages")

            if reader.is_encrypted:
                print(f"Error: PDF at {pdf_path} is encrypted")
                return None

            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                except Exception as e:
                    print(f"Warning: Could not extract text from page {page_num + 1}: {e}")
                    continue

            if not text_content:
                print("Warning: No text content extracted from PDF")
                return None

            return "\n\n".join(text_content)

        except Exception as e:          # catches PdfReadError, PermissionError, etc.
            print(f"Error extracting PDF: {e}")
            return None

    @staticmethod
    def parse_cv(pdf_path: str) -> dict:
        text = PDFParser.extract_text_from_pdf(pdf_path)

        if not text:
            return {
                "raw_text": "",
                "success": False,
                "error": "Failed to extract text from PDF",
            }

        return {
            "raw_text": text,
            "success": True,
            "page_count": text.count("\n\n") + 1,
            "char_count": len(text),
            "word_count": len(text.split()),
        }


# ----------------------------------------------------------------------
# safe_object_id – **keep it here** (shared across the whole project)
# ----------------------------------------------------------------------
def safe_object_id(id_str: str, param_name: str = "id") -> ObjectId:
    """
    Validate and convert a string to a MongoDB ObjectId.
    """
    if not isinstance(id_str, str) or not ObjectId.is_valid(id_str):
        raise HTTPException(status_code=400, detail=f"Invalid {param_name} format")
    return ObjectId(id_str)

def decode_token(token: str) -> dict:
    try:
        if settings.ALGORITHM == "RS256":
            if not settings.JWT_PUBLIC_KEY:
                raise HTTPException(status_code=500, detail="JWT public key missing")
            return jwt.decode(token, settings.JWT_PUBLIC_KEY, algorithms=["RS256"])
        else:
            return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc