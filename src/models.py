from collections import namedtuple
from typing import NamedTuple, Any
import json

Department = namedtuple('Department', ['id', 'name', 'superdepartment'])
Office = namedtuple('Office', ['id', 'city', 'country', 'address'])
Employee = namedtuple('Employee', ['id', 'first', 'last', 'manager', 'department', 'office'])


class Collection(dict):

    def add(self, elem):
        super().__setitem__(elem.id, elem)

    def adds(self, elems):
        super().update([(e.id, e) for e in elems])

    def get_by_id(self, id):
        return super().get(id)


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

