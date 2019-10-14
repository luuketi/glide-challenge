#!/usr/bin/env python3

import os
import unittest

from src import create_app
from src.controllers import blueprint
import src.models as models

app, manager = create_app(os.getenv('APP_ENV') or 'dev')

@manager.command
def run():
    app.run(port=8080)


@manager.command
def test():
    tests = unittest.TestLoader().discover('tests', pattern='*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


if __name__ == '__main__':
    manager.run()
