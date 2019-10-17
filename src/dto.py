from marshmallow import Schema, fields


class BaseSchema:

    def _build_expanded(self, field, function):
        return fields.Nested(field) if field else fields.Function(function)

    def build(self):
        return type(self.__class__.__name__, (Schema,), self._schema_fields())


class EmployeeSchema(BaseSchema):

    def __init__(self, manager=None, department=None, office=None):

        def a(obj, attr):
            if type(obj) == int:
                return obj
            if type(getattr(obj, attr)) == int:
                return getattr(obj, attr)
            if hasattr(getattr(obj, attr), 'id'):
                return getattr(obj, attr).id
            return None

        self._manager = self._build_expanded(manager, lambda obj: a(obj, 'manager'))
        self._department = self._build_expanded(department, lambda obj: a(obj, 'department'))
        self._office = self._build_expanded(office, lambda obj: a(obj, 'office'))

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


class Visitor:

    def accept_expanded_department(self, expanded):
        pass

    def accept_expanded_office(self, expanded):
        pass

    def accept_expanded_employee(self, expanded):
        pass

    def build_schema(self, expand=[], visit=None):
        pass

    @staticmethod
    def _get_builder(name):

        expandables = {
            'manager': EmployeeSchemaBuilder(),
            'office': OfficeSchemaBuilder(),
            'department': DepartmentSchemaBuilder(),
            'superdepartment': DepartmentSchemaBuilder(),
        }

        return expandables[name]

    def _expand(self, expand):
        for e in expand:
            first = e.split('.')[0]
            last = '.'.join(e.split('.')[1:])
            if first and first in self._allowed_expands():
                schema_builder = self._get_builder(first)
                schema_builder.build_schema([last], self)


class DepartmentSchemaBuilder(Visitor):

    def __init__(self):
        self._department_expanded = None

    def get_expanded(self):
        return self._department_expanded

    def accept_expanded_department(self, expanded):
        self._department_expanded = expanded

    def _allowed_expands(self):
        return ['superdepartment']

    def build_schema(self, expand=[], visit=None):
        self._expand(expand)
        schema = DepartmentSchema(self._department_expanded).build()
        visit.accept_expanded_department(schema)


class OfficeSchemaBuilder(Visitor):

    def __init__(self):
        self._office_expanded = None

    def get_expanded(self):
        return self._office_expanded

    def accept_expanded_office(self, expanded):
        self._office_expanded = expanded

    def build_schema(self, expand=[], visit=None):
        schema = OfficeSchema().build()
        visit.accept_expanded_office(schema)


class EmployeeSchemaBuilder(Visitor):

    def __init__(self):
        self._department_expanded = None
        self._office_expanded = None
        self._manager_expanded = None

    def get_expanded(self):
        return self._manager_expanded

    def _allowed_expands(self):
        return ['superdepartment', 'department', 'manager', 'office']

    def accept_expanded_department(self, expanded):
        self._department_expanded = expanded

    def accept_expanded_office(self, expanded):
        self._office_expanded = expanded

    def accept_expanded_manager(self, expanded):
        self._manager_expanded = expanded

    def build_schema(self, expand=[], visit=None):
        self._expand(expand)
        schema = EmployeeSchema(self._manager_expanded, self._department_expanded, self._office_expanded).build()
        visit.accept_expanded_manager(schema)


def build(builder, expand=None):
    builder.build_schema(expand, builder)
    return builder.get_expanded()


def build_department(expand=[]):
    return build(DepartmentSchemaBuilder(), expand)


def build_office():
    return build(OfficeSchemaBuilder())


def build_employee(expand=[]):
    return build(EmployeeSchemaBuilder(), expand)
