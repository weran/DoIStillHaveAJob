"""
Provides the handlers for the URLs supported by this site.
"""

from bottle import route, template, static_file, request, redirect
from os import getenv
from employees import get_employee
from datetime import date

@route('/')
def home():
    """Renders a home page with some info and a list of tasks."""
    return template(
        'home.html',
        company=getenv("COMPANY_NAME", "My Company"),
        year=date.today().year,
    )


@route('/job')
def job():
    """Renders a page indicating whether an employee still has a job."""
    try:
        employee = get_employee(request.query['employee'])
    except LookupError:
        return template('error.html', reason='No employee was specified')

    return template(
        'job.html',
        employee=employee.name,
        has_a_job=employee.has_a_job,
        company=getenv("COMPANY_NAME", "My Company"),
        year=date.today().year,
    )

@route('/fix')
def fix():
    """Handles requests to correct an employee's status, then redirects
    to their page."""
    try:
        employee = get_employee(request.query['employee'])
    except LookupError:
        return template('error.html', reason='No employee was specified')

    employee.fix()

    return redirect("/job?employee=" + employee.name)

@route('/<filename:re:.*\.css>')
@route('/static/<filename:re:.*\.css>')
def static_css(filename):
    return static_file(filename, root='static')
