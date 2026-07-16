import os
import sys
import qrcode
from dotenv import load_dotenv

load_dotenv()

SITE_URL = os.getenv("SITE_URL", "https://ai-rank-one.hasnainrazalakhani7272.workers.dev").rstrip("/")
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register a standard system font that supports Arabic
FONT_PATH = "C:\\Windows\\Fonts\\arial.ttf"
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont('ArialArabic', FONT_PATH))
    FONT_NAME = 'ArialArabic'
else:
    FONT_NAME = 'Helvetica' # Fallback for non-Windows (won't render Arabic properly, but won't crash)

def generate_pdf_certificate(code, student_name, course_title, date_str, score):
    os.makedirs("certificates/generated", exist_ok=True)
    pdf_path = f"certificates/generated/{code}.pdf"
    qr_path = f"certificates/generated/qr_{code}.png"

    # 1. Generate QR Code
    qr = qrcode.QRCode(version=1, box_size=4, border=1)
    qr.add_data(f"{SITE_URL}/verify.html?code={code}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#0f172a", back_color="white")
    qr_img.save(qr_path)

    # 2. Setup landscape letter canvas
    c = canvas.Canvas(pdf_path, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Background Color (Dark Navy theme matching PWA)
    c.setFillColorRGB(0.01, 0.02, 0.09) # #020617
    c.rect(0, 0, width, height, fill=True, stroke=False)

    # Outer border
    c.setStrokeColorRGB(0.2, 0.55, 1.0) # Brand blue
    c.setLineWidth(4)
    c.rect(20, 20, width - 40, height - 40)
    
    # Inner thin border
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(1)
    c.rect(28, 28, width - 56, height - 56)

    # Header / Title
    c.setFillColorRGB(1.0, 1.0, 1.0)
    c.setFont(FONT_NAME, 28)
    c.drawCentredString(width / 2, height - 100, "شهادة إتمام الدورة")
    
    c.setFont(FONT_NAME, 16)
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.drawCentredString(width / 2, height - 130, "Certificate of Completion")

    # Body text
    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.setFont(FONT_NAME, 18)
    c.drawCentredString(width / 2, height - 200, "تُمنح هذه الشهادة لـ / This is to certify that")
    
    c.setFillColorRGB(0.2, 0.55, 1.0) # Brand blue
    c.setFont(FONT_NAME, 26)
    c.drawCentredString(width / 2, height - 240, student_name)

    c.setFillColorRGB(0.9, 0.9, 0.9)
    c.setFont(FONT_NAME, 18)
    c.drawCentredString(width / 2, height - 290, "لاجتيازه بنجاح دورة / for successfully completing the course")

    c.setFillColorRGB(0.66, 0.33, 0.97) # Purple
    c.setFont(FONT_NAME, 22)
    c.drawCentredString(width / 2, height - 330, course_title)

    # Date and Score info
    c.setFillColorRGB(0.7, 0.7, 0.7)
    c.setFont(FONT_NAME, 14)
    c.drawString(60, 120, f"التاريخ / Date: {date_str}")
    c.drawString(60, 90, f"الدرجة / Score: {score}")
    c.drawString(60, 60, f"الرمز / Code: {code}")

    # Draw QR code
    c.drawImage(qr_path, width - 180, 60, width=120, height=120)
    
    # Signature placeholder
    c.setFont(FONT_NAME, 14)
    c.drawString(width / 2 - 50, 90, "د. خالد الراشدي")
    c.setStrokeColorRGB(0.5, 0.5, 0.5)
    c.setLineWidth(1)
    c.line(width / 2 - 70, 110, width / 2 + 70, 110)
    c.setFont(FONT_NAME, 10)
    c.drawString(width / 2 - 40, 70, "توقيع المنسق الأكاديمي")

    c.showPage()
    c.save()

    # Clean up QR code image
    if os.path.exists(qr_path):
        os.remove(qr_path)

    print(f"Generated PDF certificate: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    if len(sys.argv) > 5:
        generate_pdf_certificate(
            sys.argv[1], # code
            sys.argv[2], # name
            sys.argv[3], # course
            sys.argv[4], # date
            sys.argv[5]  # score
        )
    else:
        # Default test cert
        generate_pdf_certificate("CERT-TEST", "أحمد محمد", "بناء أنظمة الوكلاء المتعددة باستخدام LangGraph", "2026-07-16", "85/100")
