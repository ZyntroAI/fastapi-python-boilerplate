#!/usr/bin/env python3
"""
ปรับปรุงคุณภาพภาพ, คมชัด, ขยายขนาด — พร้อมรักษารายละเอียด
ใช้: python scripts/image-enhance.py input.jpg output_enhanced.png
"""
import sys
import os
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageFilter
except ImportError:
    print("📦 ติดตั้งก่อน: pip install pillow")
    sys.exit(1)

def enhance_image(input_path, output_path,
                  sharpness=1.8, contrast=1.3, brightness=1.05,
                  color=1.1, upscale_factor=2):
    """
    ปรับปรุงภาพแบบครบวงจร
    sharpness: 1.0=เดิม, 1.5-2.0=แนะนำ, >3=รุนแรง
    upscale_factor: 1=ไม่ขยาย, 2=คูณ2, 4=คูณ4
    """
    img = Image.open(input_path).convert("RGB")
    
    # ขยายขนาด (รักษาความเรียบเนียน)
    if upscale_factor > 1:
        new_size = (int(img.width * upscale_factor),
                    int(img.height * upscale_factor))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # ปรับความคมชัด
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(sharpness)
    
    # ปรับคอนทราสต์
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(contrast)
    
    # ปรับความสว่าง
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(brightness)
    
    # ปรับสี
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(color)
    
    # กรองลดจุดรบกวนเบาๆ
    img = img.filter(ImageFilter.UnsharpMask(radius=1.2, amount=1.5))
    
    # บันทึก
    img.save(output_path, optimize=True, quality=95)
    print(f"✅ บันทึก: {output_path}")
    print(f"   ขนาด: {img.width} × {img.height}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("การใช้งาน:")
        print("  python scripts/image-enhance.py <ไฟล์เข้า> <ไฟล์ออก> [คมชัด] [ขยาย]")
        print("\nตัวอย่าง:")
        print("  python scripts/image-enhance.py architecture.jpg enhanced.png 1.8 2")
        sys.exit(1)
    
    in_file = sys.argv[1]
    out_file = sys.argv[2]
    sharp = float(sys.argv[3]) if len(sys.argv) > 3 else 1.8
    scale = float(sys.argv[4]) if len(sys.argv) > 4 else 2
    
    enhance_image(in_file, out_file, sharpness=sharp, upscale_factor=scale)
