# This sheet contains the authentification parameters for the NTM Advanced Calculation Tool and the Google Maps API
# The identification settings must be updated by each new user.

NTM_authentification_settings = {
    'userName': "",  # user name - INSERT OWN USERNAME
    'passWord': "",  # user password - INSERT OWN PASSWORD
    'clientId': "",  # client id - INSERT OWN CLIENTID
    'clientSecret': "",  # client secret - INSERT OWN CLIENT SECRET

    'authServer': 'auth.transportmeasures.org',  # test-auth # authorization server host
    'tokenEndPointPath': '/auth/realms/ntm/protocol/openid-connect/token',  # path to the token end point
    'logoutEndPointPath': '/auth/realms/ntm/protocol/openid-connect/logout'  # path to the logout end point
    }

# Google Maps API Key
API_KEY = "" # INSERT OWN KEY
