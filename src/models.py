import itertools
import json
import logging
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

    def get(self, limit, offset, expand=None):
        self._validate_params(limit, offset)
        max = len(self._data) if limit > len(self._data) else limit
        return [self._data.get(k) for k in range(offset + 1, max + 1)]

    def get_by_id(self, id, expand=None):
        return self._data.get(id)

    def _validate_params(self, limit, offset):
        if offset < 0:
            raise RuntimeError('Offset must be a positive number')
        if limit < 1 or limit > 1000:
            raise RuntimeError('Limit must be higher than 0 and less than 1000')


class EmployeesCollection(Collection):

    _URL = 'https://rfy56yfcwk.execute-api.us-west-1.amazonaws.com/bigcorp/employees'

    _IDS_PER_REQUEST = 100

    def __init__(self):
        super().__init__()
        self._pending_managers = set([])

    def _chunked_iterable(self, iterable, size):
        """Iterates iterable in chunks of size"""
        i = iter(iterable)
        while True:
            chunk = tuple(itertools.islice(i, size))
            if not chunk:
                break
            yield chunk

    def _get(self, params):
        return requests.get(self._URL, params).json()

    def _get_by_id(self, params):
        logging.info('Retrieving: {}'.format(str(['id={}'.format(p) for i, p in params])))
        return self._get(params)

    def _build_employee(self, json):
        office = Offices.get_by_id(json['office'])
        department = Departments.get_by_id(json['department'])
        return Employee(json['id'], json['first'], json['last'], json['manager'], department, office)

    def _process_employees(self, employees):
        """Build employees objects from json dict and store them"""
        for e in employees:
            employee = self._build_employee(e)
            manager = super().get_by_id(e['manager'])
            if e['manager'] and not manager:
                logging.info('Manager {} not found in collection'.format(e['manager']))
                self._pending_managers.add(e['manager'])
            else:
                employee.manager = manager
            super().add(employee)

    def _clear_collection(self):
        self._data = {}
        self._pending_managers = set([])

    def _process_response(self, data, expand):
        """Store the employees from json dict and retrieve pending managers"""
        self._clear_collection()
        self._process_employees(data)
        manager_count = max([sum(1 for m in e.split('.') if m == 'manager') for e in expand], default=0)
        self._retrieve_pending(manager_count+1)

    def get(self, limit, offset, expand=[]):
        self._validate_params(limit, offset)
        data = self._get({'limit': limit, 'offset': offset})
        self._process_response(data, expand)
        max = len(self._data) if limit > len(self._data) else limit + offset
        return [self._data.get(k) for k in range(offset + 1, max + 1)]

    def get_by_id(self, id, expand=[]):
        data = self._get_by_id([('id', id)])
        self._process_response(data, expand)
        return super().get_by_id(id)

    def _update_pending_managers(self, managers):
        """Update manager objects on stored employees"""
        for manager in managers:
            obj = super().get_by_id(manager)
            for k, v in self._data.items():
                if v.manager == manager:
                    v.manager = obj

    def _retrieve_pending(self, levels=0):
        """Retrieve pending managers using _pending_managers"""
        if levels:
            pending_managers = list(self._pending_managers)
            logging.info('Pending managers to retrieve: {} - level {}'.format(len(pending_managers), levels))
            self._pending_managers = set([])
            for chunks in self._chunked_iterable(pending_managers, self._IDS_PER_REQUEST):
                params = [('id', manager) for manager in chunks]
                data = self._get_by_id(params)
                self._process_employees(data)
                self._update_pending_managers(chunks)

            if self._pending_managers and levels > 0:
                self._retrieve_pending(levels-1)


def _load_data_from_files():
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


Departments, Offices = _load_data_from_files()
Employees = EmployeesCollection()
