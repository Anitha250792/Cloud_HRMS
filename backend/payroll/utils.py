from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import datetime

def generate_payroll_pdf(payroll, file_path):
    c = canvas.Canvas(file_path, pagesize=A4)
    
    width, height = A4
    margin = 20 * mm
    cursor_y = height - margin

    # HEADER
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.HexColor("#0052cc"))
    c.drawString(margin, cursor_y, "CLOUD HRMS PAYROLL SYSTEM")

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(margin, cursor_y - 15, "Professional Salary Slip (Auto-Generated)")
    
    cursor_y -= 40

    # EMPLOYEE INFO
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, cursor_y, "Employee Information")

    cursor_y -= 10
    c.setFont("Helvetica", 10)
    c.drawString(margin, cursor_y, f"Name: {payroll.employee.name}")
    c.drawString(margin + 200, cursor_y, f"Employee ID: {payroll.employee.id}")

    cursor_y -= 12
    dept = getattr(payroll.employee, "department", "N/A")
    c.drawString(margin, cursor_y, f"Department: {dept}")
    c.drawString(margin + 200, cursor_y, f"Month-Year: {payroll.month}/{payroll.year}")

    cursor_y -= 20

    # SALARY TABLE
    table_data = [
        ["Description", "Value (₹)"],
        ["Basic Salary", f"{payroll.basic_salary:.2f}"],
        ["Working Days", f"{payroll.working_days}"],
        ["Present Days", f"{payroll.present_days}"],
        ["Absent Days", f"{payroll.absent_days}"],
        ["Loss of Pay Days", f"{payroll.lop_days}"],
        ["Gross Salary", f"{payroll.gross_salary:.2f}"],
        ["Net Salary", f"{payroll.net_salary:.2f}"],
    ]

    table = Table(table_data, colWidths=[100 * mm, 60 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0052cc")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    cursor_y -= 20
    table.wrapOn(c, margin, cursor_y)
    table.drawOn(c, margin, cursor_y - 180)

    # FOOTER
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(margin, 30, "This is a computer-generated salary slip. No signature required.")
    c.drawRightString(width - margin, 30, f"Generated on: {datetime.date.today()}")

    c.save()

def generate_bulk_payroll_pdf(payroll_qs, file_path, year, month):
    doc = SimpleDocTemplate(file_path, pagesize=A4, leftMargin=20*mm, rightMargin=20*mm)
    elements = []
    styles = getSampleStyleSheet()

    title = Paragraph(f"Payroll Summary - {month}/{year}", styles["Title"])
    elements.append(title)
    elements.append(Spacer(1, 12))

    data = [["Emp ID", "Name", "Gross (₹)", "Net (₹)"]]
    for p in payroll_qs:
        data.append([
            p.employee.id,
            p.employee.name,
            f"{p.gross_salary:.2f}",
            f"{p.net_salary:.2f}",
        ])

    table = Table(data, colWidths=[25*mm, 60*mm, 40*mm, 40*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0052cc")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (2, 1), (-1, -1), "RIGHT"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
    ]))

    elements.append(table)
    doc.build(elements)    
