import datetime
from flask import request
from flask_restplus import Resource, Api
from webargs import fields, validate
from webargs.flaskparser import use_kwargs


from src import blueprint
from src.dto import *
from src.models import Offices, Departments


api = Api(blueprint,
          title='Big Corp API',
          version='1.0'
          )

args = {
    'limit': fields.Int(missing=100, validate=[validate.Range(min=1, max=10000)]),
    'offset': fields.Int(missing=1),
}

class BaseResource(Resource):

    pass

@api.route('/offices/<int:id>')
class OfficeDetail(Resource):

    def get(self, id):
        print(Offices.get_by_id(id))

@api.route('/offices')
class OfficeList(Resource):

    def get(self):
        print('list')


@api.route('/departments/<int:id>')
class DepartmentDetail(Resource):

    def get(self, id):
        expand = request.values.getlist('expand')[0]
        department = Departments.get_by_id(id)
        return dump(department, expand)


@api.route('/departments')
class DepartmentList(Resource):

    @use_kwargs(args)
    def get(self, limit, offset):
        expand = request.values.getlist('expand')[0]
        department = Departments.get(limit, offset)
        return dump(department, expand)


