from os import path

secret_key = 'this_should_be_configured'

BASE_DIRECTORY = path.abspath(path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = '{0}{1}'.format('sqlite:///',
                                    path.join(BASE_DIRECTORY, 'app.db'))
FB_APP_ID='323621904515839'
FB_APP_SECRET='3c42b3f4b82545fb7c620f46d925bb19'
FB_APP_NAME='Unilearn'
secret_key = 'Unilearn-SMS-YouWillNeverGuess'
SQLALCHEMY_DATABASE_URI = "postgres://dojilftyeldmte:SzQMKPagyO3-Iil7PQF7zXWgM8@ec2-23-21-183-70.compute-1.amazonaws.com:5432/d4h8bjpkso4a3l"
appName = "Unilearn"
version = "0.0.2"
versionName = "Bulbasaur"
