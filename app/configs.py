#from os import path


secret_key = 'this_should_be_configured'

#BASE_DIRECTORY = path.abspath(path.dirname(__file__))
#SQLALCHEMY_DATABASE_URI = '{0}{1}'.format('sqlite:///',
#                                          path.join(BASE_DIRECTORY, 'app.db'))

fb = {
    'id': '323621904515839',
    'secret': '3c42b3f4b82545fb7c620f46d925bb19',
    'name': 'Unilearn',
    'acces_token_url': '/oauth/access_token',
    'authorize_url': 'https://www.facebook.com/dialog/oauth'
}
tw = {
    'ID': 'KrNjfb7GjQXYPPVZzwrz6Eytd',
    'SECRET': 'g3w93jzSNK0cwIRMTQTHxJafNd7UWcfCJpH2NDSrIKF3AP0mhh',
    'NAME': 'Unilearn',
    'base_url': 'https://api.twitter.com/1.1/',
    'request_token_url': 'https://api.twitter.com/oauth/request_token',
    'access_token_url': 'https://api.twitter.com/oauth/access_token',
    'authorize_utl': 'https://api.twitter.com/oauth/authenticate'

}
gl = {
    'id': '280015471056-nh44m1ds0au70mff2s21nder0akaa7ph.apps.googleusercontent.com',
    'secret': 'MHoaxOe-cxcdu9vVPgdhqzED',
    'name': 'Unilearn'
}

secret_key = 'Unilearn-SMS-YouWillNeverGuess'
SQLALCHEMY_DATABASE_URI = "postgres://uumeqpfnmvqyou:3_qL1AEWBrHC8XCmp5PG2bfJqF@ec2-23-21-96-129.compute-1.amazonaws.com:5432/dbtla9hjh2jsa8"
appName = "Unilearn"
version = "0.0.2"
versionName = "Bulbasaur"