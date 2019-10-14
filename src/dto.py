from marshmallow import Schema, fields, post_load, validate

from src.models import Department, Office, Employee, Employees, Departments


class BaseSchema:

    def _build_expanded(self, field, function):
        return fields.Nested(field) if field else fields.Function(function)

    def build(self):
        return type(self.__class__.__name__, (Schema,), self._schema_fields())


class EmployeeSchema(BaseSchema):

    def __init__(self, manager=None, department=None, office=None):
        self._manager = self._build_expanded(manager, lambda obj: obj.manager.id if obj.manager else None)
        self._department = self._build_expanded(department, lambda obj: obj.department.id if obj.department else None)
        self._office = self._build_expanded(office, lambda obj: obj.office.id if obj.office else None)

    def _schema_fields(self):
        return {
            'id': fields.Integer(),
            'first': fields.String(),
            'last': fields.String(),
            'manager': self._manager,
            'department': self._department,
            'office': self._office,
        }


class OfficeSchema(BaseSchema):

    def _schema_fields(self):
        return {
            'id': fields.Integer(),
            'city': fields.String(),
            'country': fields.String(),
            'address': fields.String(),
        }


class DepartmentSchema(BaseSchema):

    def __init__(self, superdepartment=None):
        self._superdepartment = self._build_expanded(superdepartment,
                                                     lambda obj: obj.superdepartment.id if obj.superdepartment else None)

    def _schema_fields(self):
        return {
            'id': fields.Integer(),
            'name': fields.String(),
            'superdepartment': self._superdepartment,
        }

class ListSchema(BaseSchema):

    def _schema_fields(self):
        return {

        }


def build_employee(manager=None, department=None, office=None):
    return EmployeeSchema(manager, department, office).build()


def build_office():
    return OfficeSchema().build()


def build_department(superdepartment=None):
    return DepartmentSchema(superdepartment).build()


def dump(data, expands='department'):
    _data = data
    is_list = False
    if type(data).__name__ == 'list':
        is_list = True
        data = data[0]
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
    return expanded(many=is_list).dump(_data)


print(dump(Department(1, 'sdf', Department(2, 'aaa', None)), expands='superdepartment.superdepartment'))
print(dump(Office(1, 'asdfsf', 'asdfsddd', 'ss')))
print(dump(Employees.get_by_id(4), expands='manager.manager.office'))




