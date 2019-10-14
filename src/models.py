from collections import namedtuple
from typing import NamedTuple, Any
import json

Department = namedtuple('Department', ['id', 'name', 'superdepartment'])
Office = namedtuple('Office', ['id', 'city', 'country', 'address'])
Employee = namedtuple('Employee', ['id', 'first', 'last', 'manager', 'department', 'office'])


class Collection(dict):

    def __init__(self):
        self._data = {}

    def add(self, elem):
        self._data[elem.id] = elem

    def adds(self, elems):
        self._data.update([(e.id, e) for e in elems])

    def get(self, limit=100, offset=1):
        max = len(self._data) if limit + offset - 1 > len(self._data) else limit + offset
        data = [self._data.get(k) for k in range(offset, max)]
        return data

    def get_by_id(self, id):
        return self._data.get(id)



def load_data_from_files():
    departments = Collection()
    offices = Collection()
    employees = Collection()

    with open('data/departments.json') as file:
        for d in json.load(file):
            superdepartment = departments.get_by_id(d['superdepartment'])
            new_department = Department(d['id'], d['name'], superdepartment)
            departments.add(new_department)

    with open('data/offices.json') as file:
        offices.adds(json.load(file, object_hook=lambda o: Office(**o)))

    with open('data/employees.json') as file:
        for e in json.load(file):
            department = departments.get_by_id(e['department'])
            office = offices.get_by_id(e['office'])
            manager = employees.get_by_id(e['manager'])
            new_employee = Employee(e['id'], e['first'], e['last'], manager, department, office)
            employees.add(new_employee)

    return departments, offices, employees


Departments, Offices, Employees = load_data_from_files()

