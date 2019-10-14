import datetime
from flask import request
from flask_restplus import Resource, Api
from webargs import fields, validate
from webargs.flaskparser import use_kwargs


from src import blueprint
from src.dto import *
from src.models import *


api = Api(blueprint,
          title='Big Corp API',
          version='1.0'
          )

args = {
    'limit': fields.Int(missing=100, validate=[validate.Range(min=1, max=10000)]),
    'offset': fields.Int(missing=1),
}

class BaseResource(Resource):

    def store_expanded_department(self, expanded):
        self._department_expanded = expanded

    def store_expanded_office(self, expanded):
        self._office_expanded = expanded

    def store_expanded_manager(self, expanded):
        self._manager_expanded = expanded

    def _build_schema(self, expand):
        self._schema_builder = self._get_schema_builder()
        self._schema_builder.build_schema(expand, self)

    def _return_detail(self, id):
        expand = request.values.getlist('expand')
        self._build_schema(expand)
        schema = self._get_expanded_schema()
        obj = self._get_collection().get_by_id(id)
        return schema().dump(obj)

    def _return_list(self, limit, offset):
        expand = request.values.getlist('expand')
        self._build_schema(expand)
        objs = self._get_collection().get(limit, offset)
        schema = self._get_expanded_schema()
        return schema(many=True).dump(objs)


class DepartmentBase:

    def _get_collection(self):
        return Departments

    def _get_schema_builder(self):
        return DepartmentSchemaBuilder()

    def _get_expanded_schema(self):
        return self._department_expanded


class OfficeBase:

    def _get_collection(self):
        return Offices

    def _get_expanded_schema(self):
        return self._office_expanded

    def _get_schema_builder(self):
        return OfficeSchemaBuilder()


class EmployeeBase:

    def _get_collection(self):
        return Employees

    def _get_schema_builder(self):
        return EmployeeSchemaBuilder()

    def _get_expanded_schema(self):
        return self._employee_expanded


@api.route('/offices/<int:id>')
class OfficeDetail(BaseResource, OfficeBase):

    def get(self, id):
        return self._return_detail(id)


@api.route('/offices')
class OfficeList(BaseResource, OfficeBase):

    @use_kwargs(args)
    def get(self, limit, offset):
        return self._return_list(limit, offset)


@api.route('/departments/<int:id>')
class DepartmentDetail(BaseResource, DepartmentBase):

    def get(self, id):
        return self._return_detail(id)


@api.route('/departments')
class DepartmentList(BaseResource, DepartmentBase):

    @use_kwargs(args)
    def get(self, limit, offset):
        return self._return_list(limit, offset)


@api.route('/employees/<int:id>')
class EmployeeDetail(BaseResource, EmployeeBase):

    def get(self, id):
        return self._return_detail(id)


@api.route('/employees')
class EmployeeList(BaseResource, EmployeeBase):

    @use_kwargs(args)
    def get(self, limit, offset):
        return self._return_list(limit, offset)

