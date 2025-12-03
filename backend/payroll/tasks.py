from celery import shared_task
from datetime import date
from calendar import monthrange

from employees.models import Employee
from attendance.models import Attendance
from payroll.models import Payroll


@shared_task
def generate_monthly_payroll(year=None, month=None):
    """
    Auto-generate salary for ALL employees for the specified month.
    If no year/month provided, use previous month.
    """

    # ----------------------------
    # Auto-pick last month if empty
    # ----------------------------
    today = date.today()

    if month is None or year is None:
        if today.month == 1:
            month = 12
            year = today.year - 1
        else:
            month = today.month - 1
            year = today.year

    working_days = monthrange(year, month)[1]
    employees = Employee.objects.all()

    count = 0

    for emp in employees:
        attendance = Attendance.objects.filter(
            employee=emp,
            date__year=year,
            date__month=month
        )

        present_days = attendance.count()
        absent_days = working_days - present_days
        lop_days = absent_days

        basic_salary = emp.salary
        per_day_salary = basic_salary / working_days
        lop_amount = per_day_salary * lop_days

        gross_salary = basic_salary
        net_salary = gross_salary - lop_amount

        # ---------------------
        # Prevent duplicates
        # ---------------------
        existing = Payroll.objects.filter(employee=emp, year=year, month=month).first()
        if existing:
            continue  # Skip duplicate payroll

        Payroll.objects.create(
            employee=emp,
            month=month,
            year=year,
            basic_salary=basic_salary,
            working_days=working_days,
            present_days=present_days,
            absent_days=absent_days,
            lop_days=lop_days,
            gross_salary=gross_salary,
            net_salary=net_salary,
        )

        count += 1

    return f"Generated payroll for {count} employees for {month}/{year}"
