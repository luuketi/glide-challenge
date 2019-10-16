import json
from tests.base import BaseTestCase

from src.dto import build_department, build_office, build_employee
from src.models import Departments, Offices, Employees


class OfficeSchemaTest(BaseTestCase):

    def test_office(self):
        o = Offices.get_by_id(1)
        dumped = build_office().dump(o)
        self.assertDictEqual(dumped, dict(o._asdict()))


class DepartmentSchemaTest(BaseTestCase):

    def test_department(self):
        o = Departments.get_by_id(1)
        dumped = build_department().dump(o)
        self.assertDictEqual(dumped, dict(o._asdict()))

    def test_department_expanded(self):
        o = Departments.get_by_id(9)
        dumped = build_department(['superdepartment.superdepartment']).dump(o)
        expected = '{"id": 9, "name": "Sales Development", "superdepartment": ' \
                   '{"id": 6, "name": "Outbound Sales", "superdepartment": ' \
                   '{"id": 1, "name": "Sales", "superdepartment": null}}} '
        self.assertEqual(dumped, json.loads(expected))


class EmployeeSchemaTest(BaseTestCase):

    def setUp(self):
        employees = '[{"first": "Patricia","last": "Diaz","id": 1,"manager": null,"department": 5,"office": 2},'
        ' {"first": "Daniel","last": "Smith","id": 2,"manager": 1,"department": 5,"office": 2},'
        '   {"first": "Thomas","last": "Parker","id": 3,"manager": 1,"department": 4,"office": null},'
        '  {"first": "Thdfomfas","last": "Pardfddfker","id": 4,"manager": 2,"department": 9,"office": null}]'


    def test_employee(self):
        o = Employees.get_by_id(1)
        dumped = build_employee([]).dump(o)
        expected = '{"id": 1, "department": 5, "manager": null, "last": "Diaz", "office": 2, "first": "Patricia"}'
        self.assertEqual(dumped, json.loads(expected))

    def test_employee_expanded(self):
        o = Employees.get_by_id(1)
        dumped = build_employee(['office', 'department.superdepartment']).dump(o)
        expected = '{"manager": null, "id": 1, "first": "Patricia", "last": "Diaz", ' \
                   '"department": {"superdepartment": ' \
                   '{"superdepartment": null, "id": 1, "name": "Sales"}, ' \
                   '                "id": 5, "name": "Inbound Sales"}, ' \
                   '"office": {"id": 2, "address": "20 W 34th St", "country": "United States", "city": "New York"}}'
        self.assertEqual(dumped, json.loads(expected))

    def test_employee_manager_expanded(self):
        o = Employees.get_by_id(4)
        dumped = build_employee(['office', 'department', 'manager.manager.department.superdepartment']).dump(o)
        expected = '{"department": {"id": 9, "name": "Sales Development", "superdepartment": 6},' \
                   ' "first": "Thdfomfas", "id": 4, "last": "Pardfddfker", "office": null,' \
                   ' "manager": {"department": 5, "first": "Daniel", "id": 2, "last": "Smith", "office": 2,' \
                   '             "manager": {"department":' \
                   '                          {"id": 5, "name": "Inbound Sales",' \
                   '                           "superdepartment": {"id": 1, "name": "Sales", "superdepartment": null}' \
                   '                          }, "first": "Patricia", "id": 1, "last": "Diaz", "office": 2, ' \
                   '                          "manager": null}}}'
        self.assertEqual(dumped, json.loads(expected))



