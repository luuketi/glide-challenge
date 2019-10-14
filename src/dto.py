from marshmallow import Schema, fields


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


class Visitor:

    def store_expanded_department(self, expanded):
        pass

    def store_expanded_office(self, expanded):
        pass

    def store_expanded_employee(self, expanded):
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


class DepartmentSchemaBuilder(Visitor):

    def __init__(self):
        self._department_expanded = None

    def get_expanded(self):
        return self._department_expanded

    def store_expanded_department(self, expanded):
        self._department_expanded = expanded

    def build_schema(self, expand=[], visit=None):
        for e in expand:
            last = '.'.join(e.split('.')[1:])
            if e:
                DepartmentSchemaBuilder().build_schema([last], self)
        schema = DepartmentSchema(self._department_expanded).build()
        visit.store_expanded_department(schema)


class OfficeSchemaBuilder(Visitor):

    def __init__(self):
        self._office_expanded = None

    def get_expanded(self):
        return self._office_expanded

    def store_expanded_office(self, expanded):
        self._office_expanded = expanded

    def build_schema(self, expand=[], visit=None):
        schema = OfficeSchema().build()
        visit.store_expanded_office(schema)


class EmployeeSchemaBuilder(Visitor):

    def __init__(self):
        self._department_expanded = None
        self._office_expanded = None
        self._manager_expanded = None

    def get_expanded(self):
        return self._manager_expanded

    def store_expanded_department(self, expanded):
        self._department_expanded = expanded

    def store_expanded_office(self, expanded):
        self._office_expanded = expanded

    def store_expanded_manager(self, expanded):
        self._manager_expanded = expanded

    def build_schema(self, expand=[], visit=None):
        for e in expand:
            first = e.split('.')[0]
            last = '.'.join(e.split('.')[1:])
            if first:
                schema_builder = self._get_builder(first)
                schema_builder.build_schema([last], self)
        schema = EmployeeSchema(self._manager_expanded, self._department_expanded, self._office_expanded).build()
        visit.store_expanded_manager(schema)

def build(builder, expand=None):
    builder.build_schema(expand, builder)
    return builder.get_expanded()()


def build_department(expand=[]):
    return build(DepartmentSchemaBuilder(), expand)


def build_office():
    return build(OfficeSchemaBuilder())


def build_employee(expand=[]):
    return build(EmployeeSchemaBuilder(), expand)
