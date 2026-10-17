from PIL import Image
import io

def images_to_pdf(images, page_size="A4"):
    """
    Convert a list of images into a PDF file
    images: list of PIL Image objects
    """
    if not images:
        return b""
    
    # A4 dimensions at 300 DPI
    a4_width = 2480
    a4_height = 3508
    
    pdf_images = []
    
    for img in images:
        # Convert to RGB mode
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Resize to fit A4 while preserving aspect ratio
        img.thumbnail((a4_width - 100, a4_height - 100))
        
        # Center image on a white A4 page
        page = Image.new("RGB", (a4_width, a4_height), "white")
        paste_x = (a4_width - img.width) // 2
        paste_y = (a4_height - img.height) // 2
        page.paste(img, (paste_x, paste_y))
        pdf_images.append(page)
    
    # Save as PDF
    output = io.BytesIO()
    first = pdf_images[0]
    if len(pdf_images) > 1:
        first.save(output, format="PDF", save_all=True, append_images=pdf_images[1:])
    else:
        first.save(output, format="PDF")
    
    return output.getvalue()
