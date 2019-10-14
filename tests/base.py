from flask import url_for
from flask_testing import TestCase
import json

from main import app


class BaseTestCase(TestCase):
    """ Base Tests """


    def create_app(self):
        app.config.from_object('src.config.TestingConfig')
        return app

    def setUp(self):
        pass
        #self._messages_url = url_for('api.messages')


    def tearDown(self):
        pass

    def _get(self, route, params):
        return self.client.get(
            route,
            query_string=params,
            content_type='application/json',
        )
    '''
    def _create_user(self, data=None):
        data = {'username': 'John', 'password': '123456'} if not data else data
        return self._post(url_for('api.users'), data)

    def _login(self, data=None):
        data = {'username': 'John', 'password': '123456'} if not data else data
        return self._post(url_for('api.login'), data)

    def _logout(self, token, data=None):
        data = {'username': 'John', 'password': '123456'} if not data else data
        return self._post(url_for('api.logout'), data, token)


    '''