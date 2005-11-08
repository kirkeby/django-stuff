import os
from glob import glob
import doctest
import datetime

from django.conf import settings

from django.core import db
from django.core import management
from django.core import meta
from django.core.meta import fields

import yaml
from browser import Browser

def create_object(klass, kwargs):
    """create_object(class, dict) -> class-instance

    Turn a dict as returned by yaml.load into a Model-subclass instance,
    much like AddManipulator only simpler and for yaml :)."""

    obj = klass()

    for field in obj._meta.fields:
        name = field.column

        if not kwargs.has_key(name):
            if field.default:
                value = field.default
            elif field.blank:
                value = ''
            elif isinstance(field, fields.AutoField):
                continue
            elif isinstance(field, fields.DateTimeField) and (field.auto_now or field.auto_now_add):
                value = datetime.datetime.now()
            else:
                continue

        elif isinstance(field, fields.IntegerField):
            value = int(kwargs[name])

        elif isinstance(field, fields.BooleanField):
            if isinstance(kwargs[name], str) and kwargs[name].lower() == 'true':
                value = True
            elif kwargs[name] == 1 or kwargs[name] == '1':
                value = True
            else:
                value = False

        elif isinstance(field, fields.DateTimeField):
            if isinstance(kwargs[name], yaml.timestamp):
                value = datetime.datetime.fromtimestamp(kwargs[name].mktime())
            else:
                raise 'Cannot convert %r to datetime instance' % kwargs[name]

        else:
            value = kwargs[name]

        setattr(obj, name, value)

    obj.save()
    return obj

def test_app(app):
    """test_app(app)
    
    Tests the application app:
    - a clean sqlite in-memory database is create
    - the applications models are installed
    - the fixtures in path-to-app/fixtures/*.yml are created
    - settings.ROOT_URLCONF is pointed at the applications urls-module
    - the tests in the tests-module are run with doctest.testmod
      given the fixtures and a browser-instance as globals
    """

    # Import application module
    if '.' in app:
        _, app_name = app.rsplit('.', 1)
    else:
        app_name = app
    module = __import__(app, None, None, ['*'])

    # Reinitialize database
    db.db.real_close() # this is in effect a 'drop database' with a sqlite :memory: database
    management.init()

    # Install models
    for model in module.models.__all__:
        management.install(meta.get_app(model))

    # Load fixtures
    files = os.path.join(os.path.dirname(module.__file__), 'fixtures', '*.yml')
    fixtures = {}
    for yml in [ yaml.loadFile(f) for f in glob(files) ]:
        models = yml.next()
        
        for model, fixs in models.items():
            model = meta.get_module(app_name, model)
            klass = model.Klass
    
            for name, kwargs in fixs.items():
                obj = create_object(klass, kwargs)
                # Load object from database, this normalizes it.
                fixtures[name] = model.get_object(pk=obj.id)

    # Commit fixtures
    db.db.commit()

    # Munge django.conf.settings.ROOT_URLCONF to point to
    # this apps urls-module,
    settings.ROOT_URLCONF = app + '.urls'

    # Run tests
    module = __import__(app, None, None, ['tests'])
    tests = getattr(module, 'tests', None)
    if tests:
        globs = {
            'browser': Browser(app),
        }
        globs.update(fixtures)
        doctest.testmod(tests, None, globs)
