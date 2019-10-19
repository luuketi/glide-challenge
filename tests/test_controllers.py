from tests.base import BaseTestCase
from unittest.mock import patch


class ListControllerTest(BaseTestCase):

    @patch('src.models.EmployeesCollection._get')
    def test_limit(self, _get):

        def get(params):
            return [{"first": "Patricia", "last": "Diaz", "id": x, "manager": None, "department": 5, "office": 2}
                     for x in range(1, params['limit']+1)]

        _get.side_effect = get

        params = {'limit': 1000}

        response = self._get(self._office_url, params)
        self.assertEqual(len(response.json), 5)

        response = self._get(self._department_url, params)
        self.assertEqual(len(response.json), 10)

        response = self._get(self._employee_url, params)
        self.assertEqual(len(response.json), 1000)

    @patch('src.models.EmployeesCollection._get')
    def test_offset(self, _get):

        def get(params):
            return [{"first": "Patricia", "last": "Diaz", "id": x, "manager": None, "department": 5, "office": 2}
                    for x in range(1, params['limit'] + 1)]

        _get.side_effect = get

        params = {'offset': 4}

        response = self._get(self._office_url, params)
        self.assertEqual(len(response.json), 1)

        response = self._get(self._department_url, params)
        self.assertEqual(len(response.json), 6)

        response = self._get(self._employee_url, params)
        self.assertEqual(len(response.json), 96)

    def test_limits(self):
        for url in [self._office_url, self._department_url, self._employee_url]:
            self.assert_status(self._get(url, {'offset': -1}), 422)
            self.assert_status(self._get(url, {'limit': -1}), 422)
            self.assert_status(self._get(url, {'limit': 1001}), 422)


class OfficeControllerTest(BaseTestCase):


    def test_office_detail(self):
        response = self._get_detail(self._office_url, 1)
        expected = {'city': 'San Francisco', 'id': 1, 'country': 'United States', 'address': '450 Market St'}
        self.assertDictEqual(response.json, expected)

    def test_office_detail_expanded(self):
        params = (('expand', 'department'), ('expand', 'manager.manager'), ('expand', 'office'))
        response = self._get_detail(self._office_url, 1, params)
        expected = {'city': 'San Francisco', 'id': 1, 'country': 'United States', 'address': '450 Market St'}
        self.assertDictEqual(response.json, expected)


class DepartmentControllerTest(BaseTestCase):

    def test_department_detail(self):
        response = self._get_detail(self._department_url, 1)
        expected = {"id": 1, "name": "Sales", "superdepartment": None}
        self.assertDictEqual(response.json, expected)

    def test_department_detail_expanded(self):
        params = (('expand', 'superdepartment.superdepartment'), ('expand', 'manager.manager'), ('expand', 'office'))
        response = self._get_detail(self._department_url, 9, params)
        self.assertEqual(response.json['superdepartment']['superdepartment']['id'], 1)


class EmployeeControllerTest(BaseTestCase):

    @patch('src.models.EmployeesCollection._get')
    def test_employee_detail(self, _get):

        def get(params):
            return [{"first": "Patricia", "last": "Diaz", "id": 1, "manager": None, "department": 5, "office": 2}]

        _get.side_effect = get

        response = self._get_detail(self._employee_url, 1)
        expected = {"first": "Patricia", "last": "Diaz", "id": 1, "manager": None, "department": 5, "office": 2}
        self.assertDictEqual(response.json, expected)

    @patch('src.models.EmployeesCollection._get')
    def test_department_detail_expanded(self, _get):

        def get(params):
            for param in params:
                if param[0] == 'id':
                    return [{"first": "Patricia", "last": "Diaz", "id": param[1], "manager": param[1]-1,
                             "department": 9, "office": 2}]

        _get.side_effect = get

        params = (('expand', 'superdepartment.superdepartment'),
                  ('expand', 'manager.manager.manager'),
                  ('expand', 'office'))
        response = self._get_detail(self._employee_url, 88, params)
        self.assertEqual(response.json['id'], 88)
        self.assertEqual(response.json['manager']['id'], 87)
        self.assertEqual(response.json['manager']['manager']['id'], 86)
        self.assertEqual(response.json['manager']['manager']['manager']['id'], 85)
        self.assertEqual(response.json['office']['id'], 2)
        self.assertEqual(response.json['department']['superdepartment']['superdepartment'], 1)


