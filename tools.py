import os
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def compute_totals(raw_json: str) -> str:
    try:
        if raw_json.strip().startswith("```"):
            raw_json = raw_json.strip().strip("`").replace("json", "", 1).strip()
        invoice = json.loads(raw_json)
    except Exception as e:
        return json.dumps({
            "error": f"Invalid JSON input: {e}",
            "invoice_number": "N/A",
            "client": "Unknown",
            "items": [],
            "subtotal": 0,
            "tax": 0,
            "total": 0
        })


    if "line_items" in invoice:
        invoice["items"] = []
        for li in invoice["line_items"]:
            invoice["items"].append({
                "description": li.get("description", ""),
                "unit_price": li.get("amount", 0),
                "quantity": 1,
                "tax": invoice.get("tax_rate", 0)
            })

    subtotal = 0.0
    tax_total = 0.0
    for item in invoice.get("items", []):
        try:
            unit_price = float(item.get("unit_price", 0))
            qty = int(item.get("quantity", 1))
            line_total = unit_price * qty
            subtotal += line_total
            tax_total += line_total * float(item.get("tax", 0))
        except Exception:
            continue

    invoice["subtotal"] = subtotal
    invoice["tax"] = tax_total
    invoice["total"] = subtotal + tax_total
    return json.dumps(invoice)


def generate_invoice_pdf(raw_json: str, file_name: str = None) -> str:
    if file_name is None:
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)
        file_name = os.path.join(output_dir, "invoice.pdf")

    try:
        invoice = json.loads(raw_json)
    except Exception:
        invoice = {}

    pdf = canvas.Canvas(file_name, pagesize=letter)
    width, height = letter

    # Currency formatting
    def fmt_currency(value):
        return "$" + "{:,.2f}".format(value)

    # === HEADER ===
    pdf.setFont("Helvetica-Bold", 65)
    pdf.setFillColorRGB(.3, .3, .3)   # dark gray
    pdf.drawString(50, height - 100, "INVOICE")
    pdf.setFillColorRGB(0, 0, 0)

    pdf.setFont("Helvetica", 13)
    pdf.drawRightString(width - 50, height - 80, f"Invoice: #{invoice.get('invoice_number','')}")
    invoice_info = invoice.get("invoice_info", {})
    pdf.drawRightString(width - 50, height - 100, f"Date: {invoice_info.get('invoice_date', invoice.get('date',''))}")
    pdf.drawRightString(width - 50, height - 120, f"Due Date: {invoice_info.get('due_date', invoice.get('due_date',''))}")

    # === CUSTOMER / VENDOR INFO ===
    y_offset = 180
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, height - y_offset, "Billed To:")
    pdf.setFont("Helvetica", 13)
    customer = invoice.get("customer_info", {})
    pdf.drawString(50, height - y_offset - 20, customer.get("name",""))
    pdf.drawString(50, height - y_offset - 40, customer.get("phone",""))
    pdf.drawString(50, height - y_offset - 60, customer.get("address",""))
    pdf.drawString(50, height - y_offset - 80, customer.get("email",""))

    vendor = invoice.get("vendor_info", {})
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawRightString(width - 50, height - y_offset, "Bill From:")
    pdf.setFont("Helvetica", 13)
    pdf.drawRightString(width - 50, height - y_offset - 20, vendor.get("name",""))
    pdf.drawRightString(width - 50, height - y_offset - 40, vendor.get("phone",""))
    pdf.drawRightString(width - 50, height - y_offset - 60, vendor.get("address",""))
    pdf.drawRightString(width - 50, height - y_offset - 80, vendor.get("email",""))

    # === ITEMS TABLE ===
    row_height = 30
    y = height - 300
    header_top = y
    header_bottom = y - row_height
    header_text_y = (header_top + header_bottom) / 2

    # Shaded header background
    pdf.setFillColorRGB(0.9, 0.9, 0.9)
    pdf.rect(50, header_bottom, 500, row_height, fill=1, stroke=0)
    pdf.setFillColorRGB(0, 0, 0)

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(55, header_text_y, "Item")
    pdf.drawString(300, header_text_y, "Unit Price")
    pdf.drawCentredString(400, header_text_y, "Qty")
    pdf.drawRightString(550, header_text_y, "Price")
    pdf.line(50, header_top, 550, header_top)
    pdf.line(50, header_bottom, 550, header_bottom)

    pdf.setFont("Helvetica", 13)
    for i, item in enumerate(invoice.get("items", [])):
        desc = item.get("description", "")
        unit_price = float(item.get("unit_price", 0))
        qty = int(item.get("quantity", 1))
        line_total = unit_price * qty

        row_top = header_bottom - row_height * i
        row_bottom = row_top - row_height
        text_y = (row_top + row_bottom) / 2

        pdf.drawString(55, text_y, desc)
        pdf.drawRightString(340, text_y, fmt_currency(unit_price))
        pdf.drawCentredString(400, text_y, str(qty))
        pdf.drawRightString(550, text_y, fmt_currency(line_total))

        pdf.line(50, row_bottom, 550, row_bottom)

    # === TOTALS ===
    subtotal = float(invoice.get("subtotal", 0))
    tax = float(invoice.get("tax", 0))
    total = float(invoice.get("total", 0))

    labels_x_pos = 480
    base_y = header_bottom - row_height * len(invoice.get("items", []))

    pdf.drawRightString(labels_x_pos, base_y - 20, "Sub Total : ")
    pdf.drawRightString(550, base_y - 20, fmt_currency(subtotal))
    pdf.line(380, base_y - 30, 556, base_y - 30)

    pdf.drawRightString(labels_x_pos, base_y - 50, "Tax : ")
    pdf.drawRightString(550, base_y - 50, "+ " + fmt_currency(tax))
    pdf.line(380, base_y - 60, 556, base_y - 60)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawRightString(labels_x_pos, base_y - 80, "Total : ")
    pdf.drawRightString(550, base_y - 80, fmt_currency(total))
    pdf.line(380, base_y - 90, 556, base_y - 90)

    # === FOOTER ===
    pdf.setFont("Helvetica", 13)
    pdf.drawCentredString(width/2, 50, "Thank you for your business!")

    pdf.save()
    return file_name


