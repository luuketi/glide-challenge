import random
import string
from marshmallow import Schema, fields, post_load, validate

from src.models import Department, Office, Employee, Employees, Departments

def build_employee(manager=None, department=None, office=None):

    if manager:
        manager = fields.Nested(manager)
    else:
        manager = fields.Function(lambda obj: obj.manager.id if obj.manager else None)

    if department:
        department = fields.Nested(department)
    else:
        department = fields.Function(lambda obj: obj.department.id if obj.department else None)

    if office:
        office = fields.Nested(office)
    else:
        office = fields.Function(lambda obj: obj.office.id if obj.office else None)

    employee_schema = {
        'id': fields.Integer(),
        'first': fields.String(),
        'last': fields.String(),
        'manager': manager,
        'department': department,
        'office': office,
    }
    schema_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return type(schema_name, (Schema,), employee_schema)



def build_office():
    office_schema = {
        'id': fields.Integer(),
        'city': fields.String(),
        'country': fields.String(),
        'address': fields.String(),
    }
    schema_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return type(schema_name, (Schema,), office_schema)


def build_department(superdepartment=None):

    if superdepartment:
        superdepartment = fields.Nested(superdepartment)
    else:
        superdepartment = fields.Function(lambda obj: obj.superdepartment.id if obj.superdepartment else None)

    department_schema = {
        'id': fields.Integer(),
        'name': fields.String(),
        'superdepartment': superdepartment,
    }
    schema_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return type(schema_name, (Schema,), department_schema)


def dump(data, expands='department'):

    expanded = None
    if type(data).__name__ == 'Department':
        for e in reversed(expands.split('.')):
            expanded = build_department(expanded)
    elif type(data).__name__ == 'Office':
        expanded = build_office()
    elif type(data).__name__ == 'Employee':
        first = expands.split('.')[0]
        department_expanded = None
        manager_expanded = None
        office_expanded = None

        if first == 'manager':
            man_expanded = None
            dep_expanded = None
            off_expanded = None
            for e in reversed(expands.split('.')[1:]):
                if e == 'department' or e == 'superdepartment':
                    dep_expanded = build_department(dep_expanded)
                if e == 'office':
                    off_expanded = build_office()
                if e == 'manager':
                    man_expanded = build_employee(man_expanded, dep_expanded, off_expanded)
            manager_expanded = build_employee(man_expanded, dep_expanded, off_expanded)
        if first == 'department':
            for e in reversed(expands.split('.')):
                department_expanded = build_department(department_expanded)
        if first == 'office':
            office_expanded = build_office()
        expanded = build_employee(manager=manager_expanded, department=department_expanded, office=office_expanded)

    return expanded().dump(data)


print(dump(Department(1, 'sdf', Department(2, 'aaa', None)), expands='superdepartment.superdepartment'))
print(dump(Office(1, 'asdfsf', 'asdfsddd', 'ss')))
print(dump(Employees.get_by_id(4), expands='manager.manager'))




