from flask import url_for
from flask_testing import TestCase

from main import app


class BaseTestCase(TestCase):
    """ Base Tests """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._office_url = url_for('api.office_list')
        self._department_url = url_for('api.department_list')
        self._employee_url = url_for('api.employee_list')

    def _get_detail(self, url, id, params=None):
        url = '{}/{}'.format(url, id)
        return self._get(url, params)

    def create_app(self):
        app.config.from_object('src.config.TestingConfig')
        return app

    def _get(self, route, params=None):
        return self.client.get(
            route,
            query_string=params,
            content_type='application/json',
        )
