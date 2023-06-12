# import packages
import time as time
import requests
import base64


class Auth:
    """
    Class object getting the authorization token and start/end sessions
    """

    def __init__(self, settings):
        self.settings = settings
        self.auth_response = None
        self.access_token_expiration = Expiration()
        self.refresh_token_expiration = Expiration()
        self.basic_authorization = base64.b64encode(
            f"{self.settings['clientId']}:{self.settings['clientSecret']}".encode()).decode()

    def get_access_token(self):
        # At the initial acquire of an access token or when the refresh token has expired:
        # - prepare parameters to acquire an access token with user credentials (grant_type=password)
        # - set the authorization header to contain the client id and client secret, encoded for basic authorization
        if self.refresh_token_expiration.has_expired():
            parameters = {
                'grant_type': 'password',
                'username': self.settings['userName'],
                'password': self.settings['passWord']
            }
            print('Using credentials to get new access token.')
        # When access token has expired:
        # - prepare parameters to acquire an access token with a refresh token (grant_type=refresh_token)
        # - set the authorization header to contain the client id and client secret, encoded for basic authorization
        elif self.access_token_expiration.has_expired():
            parameters = {
                'grant_type': 'refresh_token',
                'refresh_token': self.auth_response['refresh_token']
            }
            print('Using refresh token to renew expired access token.')
        # When the existing acces token is still valid:
        # - just return it
        else:
            print('Using the existing access token.')
            print(f"Access token expires in: {self.access_token_expiration.time_to_expiration()}")
            print(f"Refresh token expires in: {self.refresh_token_expiration.time_to_expiration()}")
            return self.auth_response['access_token']
        # Send a POST request to the token end point with the prepared parameters and authorization header
        authorization = {'Authorization': f"Basic {self.basic_authorization}",
                         'Content-Type': 'application/x-www-form-urlencoded'}

        res = requests.post(f"https://{self.settings['authServer']}{self.settings['tokenEndPointPath']}",
                            data=parameters,
                            headers=authorization)
        # If the request was successful, update the auth_response, access_token_expiration, and refresh_token_expiration properties with the values from the response
        if res.status_code == 200:
            self.auth_response = res.json()
            self.access_token_expiration.set_expiration_time(self.auth_response['expires_in'])
            self.refresh_token_expiration.set_expiration_time(self.auth_response['refresh_expires_in'])
            return self.auth_response['access_token']

    def end_session(self):
        if not hasattr(self, 'authResponse'):
            return "Never logged in"
        res = requests.post(f'https://{self.settings["authServer"]}{self.settings["logoutEndPointPath"]}',
                            data=f'refresh_token={self.authResponse["refresh_token"]}',
                            headers={'Authorization': f'Basic {self.basicAuthorization}',
                                     'Content-Type': 'application/x-www-form-urlencoded'})
        return res.status_code


class Expiration:
    """
    Class representing the query expiration feature
    """
    def __init__(self):
        self.expiration_time = 0
        self.network_latency = 5000 # to allow for some network latency between calls to the authorization server and the NTMCalc web service

    def set_expiration_time(self, expires_in_seconds):
        self.expiration_time = int(time.time() * 1000) + (expires_in_seconds * 1000) - self.network_latency

    def has_expired(self):
        return int(time.time() * 1000) >= self.expiration_time

    def time_to_expiration(self):
        return (self.expiration_time - int(time.time() * 1000)) / 1000
