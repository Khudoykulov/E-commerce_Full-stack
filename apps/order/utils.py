from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

def generate_receipt_pdf(order_data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    styles = getSampleStyleSheet()

    # Chek sarlavhasi
    c.setFont("Helvetica-Bold", 18)
    c.drawString(1 * inch, height - 1 * inch, "Order Receipt")

    # Buyurtma asosiy ma'lumotlari
    c.setFont("Helvetica", 12)
    # c.drawString(1 * inch, height - 1.5 * inch, f"Order ID: {order_data['order_id']}")
    c.drawString(1 * inch, height - 1.8 * inch, f"User: {order_data['user']}")
    c.drawString(1 * inch, height - 2.1 * inch, f"Order Date: {order_data['order_date']}")
    c.drawString(1 * inch, height - 2.4 * inch, f"Total Amount: ${order_data['amount']}")

    # Mahsulotlar jadvali ma'lumotlarini tayyorlash
    data = [["Product Name", "Description", "Quantity", "Unit Price", "Total Price"]]
    for item in order_data['items']:
        data.append([
            item['name'],
            item.get('description', 'No description'),  # Tavsif yoki `No description`
            str(item['quantity']),
            f"${item['price']}"
        ])

    # Jadval uslubi va dekoratsiyasi
    table = Table(data, colWidths=[2.5 * inch, 3 * inch, 1 * inch, 1 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    # Jadvalni sahifaga qo'shish
    table.wrapOn(c, width, height)
    table.drawOn(c, 1 * inch, height - 5 * inch)

    # PDF-ni yakunlash
    c.showPage()
    c.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf