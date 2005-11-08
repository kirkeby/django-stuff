def munge_settings():
    """Munges Djangos settings-module for running tests.

    BEWARE -- this must happen before django.conf.settings is imported
    to guarantee that the changes have any effect."""
    
    import sys
    if sys.modules.has_key('django.conf.settings'):
        raise AssertionError, 'django.conf.settings already imported'

    from django.conf import settings

    # Use in-memory sqlite database
    settings.DATABASE_NAME = ':memory:'
    settings.DATABASE_ENGINE = 'sqlite3'

    # Use only templates from applications
    settings.TEMPLATE_LOADERS = ('django.core.template.loaders.app_directories.load_template_source',)

    # No funky middleware
    settings.MIDDLEWARE_CLASSES = ()

def munge_db_db():
    """Munges django.core.db.db for running tests.

    - db.db.close is replaced by db.db.rollback, so more than one fake-request
      can happen in the same in-memory sqlite database.
    """
    from django.core import db
    db.db.real_close = db.db.close
    db.db.close = db.db.rollback
