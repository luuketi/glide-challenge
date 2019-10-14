from collections import namedtuple
from typing import NamedTuple, Any
import json

Department = namedtuple('Department', ['id', 'name', 'superdepartment'])
Office = namedtuple('Office', ['id', 'city', 'country', 'address'])
#Employee = namedtuple('Employee', ['id', 'first', 'last', 'manager', 'department', 'office'])
class Employee(NamedTuple):
    id: int
    first: str
    last: str
    manager: Any
    department: Department
    office: Office

    def __repr__(self):
        return '<Employee {} {} {}, ' \
               'manager: {}, ' \
               'department: {}, ' \
               'office: {}>'.format(self.id, self.first, self.last,
                                    self.manager.id if self.manager else None,
                                    self.department.id if self.department else None,
                                    self.office.id if self.office else None)

class Offices:

    def __init__(self, offices):
        self._offices = {o.id: o for o in offices}

    def get_by_id(self, id):
        return self._offices.get(id)


class Departments:

    def __init__(self, departments):
        self._departments = {d.id: d for d in departments}

    def get_by_id(self, id):
        return self._departments.get(id)


class Employees:

    def __init__(self, employees):
        self._employees = {e.id: e for e in employees}

    def get_by_id(self, id):
        return self._employees.get(id)


def load_data_from_files():
    departments = []
    with open('data/departments.json') as file:
        for d in json.load(file):
            superdepartment = d['superdepartment']
            for dep in departments:
                if dep.id == superdepartment:
                    superdepartment = dep

            departments += [Department(d['id'], d['name'], superdepartment)]

    with open('data/offices.json') as file:
        offices = json.load(file, object_hook=lambda o: Office(**o))

    departments = Departments(departments)
    offices = Offices(offices)

    employees = []
    with open('data/employees.json') as file:
        for e in json.load(file):
            department = departments.get_by_id(e['department'])
            office = offices.get_by_id(e['office'])
            manager = e['manager']
            for employee in employees:
                if employee.id == manager:
                    manager = employee
                    break

            employees += [Employee(e['id'], e['first'], e['last'], manager, department, office)]
    return departments, offices, Employees(employees)


Departments, Offices, Employees = load_data_from_files()


