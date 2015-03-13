from os import path

secret_key = 'this_should_be_configured'

BASE_DIRECTORY = path.abspath(path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = '{0}{1}'.format('sqlite:///',
                                    path.join(BASE_DIRECTORY, 'app.db'))
FB_APP_ID='323621904515839'
FB_APP_SECRET='3c42b3f4b82545fb7c620f46d925bb19'
FB_APP_NAME='Unilearn'
