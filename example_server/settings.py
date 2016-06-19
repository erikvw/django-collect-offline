from example.settings import *

APP_LABEL = 'example'
EXAMPLE_APPS = [
    'example_server.apps.SyncAppConfig',
    'example.apps.DjangoCryptoFieldsApp',
    'example.apps.ExampleAppConfig',
]
INSTALLED_APPS = DEPENDENCY_APPS + EXAMPLE_APPS

SQLITE3_DBNAME = 'db.sqlite3.server'

for database in DATABASES:
    DATABASES[database]['NAME'] = os.path.join(BASE_DIR, SQLITE3_DBNAME)
