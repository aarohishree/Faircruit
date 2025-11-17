from utils import PDFParser, safe_object_id

# Test PDF parsing
pdf_path = "C:\\Users\\ASUS\\Desktop\\faircruit1\\backend\\sample.pdf"  # Replace with a real PDF path
result = PDFParser.parse_cv(pdf_path)
print("PDF Parsing Result:", result)

# Test safe_object_id
try:
    oid = safe_object_id("507f1f77bcf86cd799439011")
    print("Valid ObjectId:", oid)
except Exception as e:
    print("ObjectId Error:", e)