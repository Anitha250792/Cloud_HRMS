from datetime import date
from payroll.models import Payroll
from employees.models import Employee
from attendance.models import Attendance
from django.utils.timezone import now
from decimal import Decimal

def generate_monthly_payroll():
    today = date.today()
    month = today.month
    year = today.year

    employees = Employee.objects.all()

    for emp in employees:
        # Get attendance for this month
        records = Attendance.objects.filter(
            employee=emp,
            date__month=month,
            date__year=year
        )

        present_days = records.exclude(check_in=None).count()
        working_days = 30
        absent_days = working_days - present_days
        lop_days = absent_days

        basic_salary = emp.salary
        per_day_salary = basic_salary / working_days
        net_salary = basic_salary - (per_day_salary * lop_days)

        Payroll.objects.create(
            employee=emp,
            month=month,
            year=year,
            basic_salary=basic_salary,
            working_days=working_days,
            present_days=present_days,
            absent_days=absent_days,
            lop_days=lop_days,
            overtime_hours=Decimal("0.00"),
            overtime_pay=Decimal("0.00"),
            gross_salary=basic_salary,
            net_salary=net_salary,
            generated_on=now()
        )

    return "Payroll generated Successfully!"
