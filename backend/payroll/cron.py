from datetime import date
from employees.models import Employee
from attendance.models import Attendance
from .models import Payroll


def generate_monthly_payroll():
    today = date.today()

    # Only run on 1st day of each month
    if today.day != 1:
        return
    
    month = today.month - 1 if today.month > 1 else 12
    year = today.year if today.month > 1 else today.year - 1

    employees = Employee.objects.all()

    for emp in employees:

        # Count present days
        present_days = Attendance.objects.filter(
            employee=emp,
            date__month=month,
            date__year=year,
        ).count()

        working_days = 30
        absent_days = working_days - present_days
        lop_days = absent_days

        daily_salary = emp.salary / working_days
        lop_amount = daily_salary * lop_days

        gross_salary = emp.salary
        net_salary = emp.salary - lop_amount

        Payroll.objects.create(
            employee=emp,
            month=month,
            year=year,
            basic_salary=emp.salary,
            working_days=working_days,
            present_days=present_days,
            absent_days=absent_days,
            lop_days=lop_days,
            overtime_hours=0,
            overtime_pay=0,
            gross_salary=gross_salary,
            net_salary=net_salary,
        )

    print("Payroll generated successfully for previous month.")

def auto_generate_payroll():
    today = date.today()

    # Only run on 1st day of month
    if today.day != 1:
        return
    
    month = today.month - 1 if today.month > 1 else 12
    year = today.year if today.month > 1 else today.year - 1

    employees = Employee.objects.all()

    for emp in employees:
        present_days = Attendance.objects.filter(
            employee=emp,
            date__month=month,
            date__year=year
        ).count()

        working_days = 30
        absent_days = working_days - present_days
        lop_days = absent_days

        daily_salary = emp.salary / working_days
        lop_amount = daily_salary * lop_days

        Payroll.objects.create(
            employee=emp,
            month=month,
            year=year,
            basic_salary=emp.salary,
            working_days=working_days,
            present_days=present_days,
            absent_days=absent_days,
            lop_days=lop_days,
            overtime_hours=0,
            overtime_pay=0,
            gross_salary=emp.salary,
            net_salary=emp.salary - lop_amount
        )

    print("Payroll auto generated!")