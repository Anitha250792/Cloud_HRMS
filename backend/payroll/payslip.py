from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from django.http import HttpResponse


def generate_payslip_pdf(payroll):

    response = HttpResponse(content_type="application/pdf")
    filename = f"Payslip_{payroll.employee.name}_{payroll.month}_{payroll.year}.pdf"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # ===============================
    # COMPANY HEADER
    # ===============================
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(40, height - 50, "XYZ Technologies Pvt. Ltd.")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, height - 70, "Chennai, Tamil Nadu, India")
    pdf.drawString(40, height - 85, "Email: hr@xyztech.com | Phone: +91-9876543210")

    # Divider line
    pdf.line(30, height - 95, width - 30, height - 95)

    # ===============================
    # PAYSLIP TITLE
    # ===============================
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawString(210, height - 120, "PAYSLIP")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(210, height - 140, f"{payroll.month} / {payroll.year}")

    # ===============================
    # EMPLOYEE DETAILS TABLE
    # ===============================
    employee_data = [
        ["Employee Name", payroll.employee.name],
        ["Employee Code", payroll.employee.emp_code],
        ["Department", payroll.employee.department],
        ["Role", payroll.employee.role],
        ["Date Joined", str(payroll.employee.date_joined)],
    ]

    table = Table(employee_data, colWidths=[120, 300])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
    ]))

    table.wrapOn(pdf, 30, height - 350)
    table.drawOn(pdf, 30, height - 330)

    # ===============================
    # SALARY DETAILS TABLE
    # ===============================
    salary_data = [
        ["Basic Salary", f"₹ {payroll.basic_salary}"],
        ["Working Days", payroll.working_days],
        ["Present Days", payroll.present_days],
        ["Absent Days", payroll.absent_days],
        ["Loss of Pay (LOP)", payroll.lop_days],
        ["Overtime Hours", payroll.overtime_hours],
        ["Overtime Pay", f"₹ {payroll.overtime_pay}"],
        ["Gross Salary", f"₹ {payroll.gross_salary}"],
        ["NET SALARY (Take Home)", f"₹ {payroll.net_salary}"],
    ]

    salary_table = Table(salary_data, colWidths=[200, 150])
    salary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('BACKGROUND', (0, 8), (-1, 8), colors.lightgreen),
        ('TEXTCOLOR', (0, 8), (-1, 8), colors.darkgreen),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 11),
    ]))

    salary_table.wrapOn(pdf, 30, height - 600)
    salary_table.drawOn(pdf, 30, height - 610)

    # ===============================
    # SIGNATURE BOX
    # ===============================
    pdf.rect(400, 80, 150, 60)  # signature box
    pdf.setFont("Helvetica", 10)
    pdf.drawString(410, 110, "Authorized Signature")
    pdf.drawString(410, 90, "_____________________")

    # ===============================
    # FOOTER
    # ===============================
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(30, 50, "This is a computer-generated payslip and does not require a signature.")

    # Finish PDF
    pdf.showPage()
    pdf.save()

    return response
