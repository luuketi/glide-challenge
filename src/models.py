import itertools
import json
from recordtype import recordtype
import requests

Department = recordtype('Department', ['id', 'name', 'superdepartment'])
Office = recordtype('Office', ['id', 'city', 'country', 'address'])
Employee = recordtype('Employee', ['id', 'first', 'last', 'manager', 'department', 'office'])


class Collection:

    def __init__(self):
        self._data = {}

    def add(self, elem):
        self._data[elem.id] = elem

    def adds(self, elems):
        self._data.update([(e.id, e) for e in elems])

    def get(self, limit=100, offset=1):
        max = len(self._data) if limit + offset - 1 > len(self._data) else limit + offset
        return [self._data.get(k) for k in range(offset, max)]

    def get_by_id(self, id):
        return self._data.get(id)


class EmployeesCollection(Collection):

    _url = 'https://rfy56yfcwk.execute-api.us-west-1.amazonaws.com/bigcorp/employees'

    def __init__(self):
        super().__init__()
        self._pendings = []

    def _chunked_iterable(self, iterable, size):
        while True:
            chunk = tuple(itertools.islice(iter(iterable), size))
            if not chunk:
                break
            yield chunk

    def _get(self, params):
        print('Retrieving: {}'.format(str(['id={} '.format(p) for i, p in params])))
        return requests.get(self._url, params).json()

    def _process_employees(self, employees):
        for e in employees:
            office = Offices.get_by_id(e['office'])
            department = Departments.get_by_id(e['department'])
            manager = super().get_by_id(e['manager'])
            if not e['manager'] or manager:
                new_employee = Employee(e['id'], e['first'], e['last'], manager, department, office)
                super().add(new_employee)
            else:
                print('Employee {} not found in collection'.format(e['id']))
                new_employee = Employee(e['id'], e['first'], e['last'], e['manager'], department, office)
                self._pendings.append(new_employee)

    def _retrieve_by_id(self, id, expand=[]):
        data = self._get([('id', id)])
        self._process_employees(data)
        manager_count = max([sum(m for m in e.split('.') if m == 'manager') for e in expand], default=0)
        self._retrieve_pending(manager_count)

    def get(self, limit=100, offset=1):
        data = requests.get(self._url, {'limit': limit, 'offset': offset}).json()[0]
        for d in data:
            pass

    def get_by_id(self, id, expand=[]):
        if id not in self._data:
            self._retrieve_by_id(id, expand)
        return super().get_by_id(id)

    def _retrieve_pending(self, levels=0):
        pending_managers = list(set([pending.manager for pending in self._pendings]))
        print('Pending managers to retrieve: {} - level {}'.format(len(pending_managers), levels))
        for chunks in self._chunked_iterable(self._pendings, 50):
            params = [('id', employee.manager) for employee in chunks]
            data = self._get(params)
            self._process_employees(data)

            for employee in chunks:
                #fix this
                manager = Employees.get_by_id(employee.manager)
                if manager:
                    employee.manager = manager
                    Employees.add(employee)
                    self._pendings.remove(employee)

        if self._pendings and levels > 0:
            self._retrieve_pending(levels-1)


def load_data_from_files():
    departments = Collection()
    offices = Collection()

    with open('data/departments.json') as file:
        for d in json.load(file):
            superdepartment = departments.get_by_id(d['superdepartment'])
            new_department = Department(d['id'], d['name'], superdepartment)
            departments.add(new_department)

    with open('data/offices.json') as file:
        offices.adds(json.load(file, object_hook=lambda o: Office(**o)))

    return departments, offices


Departments, Offices = load_data_from_files()
Employees = EmployeesCollection()
Employees.get_by_id(10)
from pprint import pprint
pprint(Employees._data.keys())
