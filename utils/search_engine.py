from database.db import get_db_connection
from datetime import datetime

def search_all_documents(keyword, search_scope="All", user_id=None):
    """Search across all documents including OCR text from scans"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    results = []
    kw = f"%{keyword}%"
    
    # Search document titles and content
    if search_scope in ["All", "Document Titles", "Content"]:
        cursor.execute(f"""
            SELECT doc_id, title, doc_type, created_at, 'Document' as source,
                   SUBSTR(content, 1, 150) as preview
            FROM documents d
            WHERE (d.title LIKE ? OR d.content LIKE ?)
            AND (user_id = ? OR ? = 'admin')
            ORDER BY created_at DESC
            LIMIT 50
        """, (kw, kw, user_id, user_id))
        
        for row in cursor.fetchall():
            results.append(dict(row))
    
    # Search OCR text from scanned images
    if search_scope in ["All", "Text from Scanned Images"]:
        cursor.execute("""
            SELECT scan_id as doc_id, file_name as title, 'Scanned Document' as doc_type,
                   scanned_at as created_at, 'Scanned Image' as source,
                   SUBSTR(ocr_text, 1, 150) as preview
            FROM scanned_documents
            WHERE ocr_text LIKE ? AND (user_id = ? OR ? = 'admin')
            ORDER BY scanned_at DESC
            LIMIT 50
        """, (kw, user_id, user_id))
        
        for row in cursor.fetchall():
            results.append(dict(row))
    
    conn.close()
    return results
