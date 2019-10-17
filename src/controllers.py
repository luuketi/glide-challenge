from flask import request
from flask_restplus import Resource, Api
from webargs import fields, validate
from webargs.flaskparser import use_kwargs

from src import blueprint
from src.dto import build_department, build_office, build_employee
from src.models import Departments, Offices, Employees


api = Api(blueprint,
          title='Big Corp API',
          version='1.0'
          )

args = {
    'limit': fields.Int(missing=100, validate=[validate.Range(min=1, max=10000)]),
    'offset': fields.Int(missing=1, validate=[validate.Range(min=1)]),
}


class BaseResource(Resource):

    def _return_detail(self, id):
        schema = self._get_expanded_schema(request.values.getlist('expand'))
        obj = self._get_collection().get_by_id(id)
        return schema().dump(obj)

    def _return_list(self, limit, offset):
        schema = self._get_expanded_schema(request.values.getlist('expand'))
        objs = self._get_collection().get(limit, offset)
        return schema(many=True).dump(objs)


class DepartmentBase:

    def _get_collection(self):
        return Departments

    def _get_expanded_schema(self, expand):
        return build_department(expand)


class OfficeBase:

    def _get_collection(self):
        return Offices

    def _get_expanded_schema(self, expand):
        return build_office()


class EmployeeBase:

    def _get_collection(self):
        return Employees

    def _get_expanded_schema(self, expand):
        return build_employee(expand)


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

