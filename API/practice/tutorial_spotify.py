# client to use the spotify API written using tutorial: https://www.youtube.com/watch?v=xdq6Gz33khQ

import requests
import base64
import datetime

from urllib.parse import urlencode

# ids given on spotify dashboard
#client_id = '3bb85dfd7aad495b80a00fac35e3cfc8'
#client_secret = '2747ee1bf5f844e2b895b8ae5f59080c'

class SpotifyAPI(object):
    access_token = None
    access_token_expires = datetime.datetime.now()
    access_token_did_expire = True
    client_id = None
    client_secret = None
    token_url = 'https://accounts.spotify.com/api/token'

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs) # can call any class its inheriting from
        self.client_id = client_id 
        self.client_secret = client_secret
    
    def get_client_creds(self):
        '''
        Returns a base64 encoded string
        '''
        client_id = self.client_id
        client_secret = self.client_secret
        if client_id == None or client_secret == None:
            raise Exception('You have to set client_id and client_secret')
        client_creds = f'{client_id}:{client_secret}'
        client_creds_b64 = base64.b64encode(client_creds.encode())
        return client_creds_b64.decode()

    def get_token_headers(self):
        client_creds_b64 = self.get_client_creds() 
        token_headers = {'Authorization': f'Basic {client_creds_b64}'}
        return token_headers
        
    def get_token_data(self):
        token_data = {'grant_type': 'client_credentials'}
        return token_data

    def perform_auth(self):
        token_url = self.token_url
        token_data = self.get_token_data()
        token_headers = self.get_token_headers()

        response = requests.post(token_url, data=token_data, headers=token_headers)

        # make sure request has good status code
        if response.status_code not in range (200,299):
            raise Exception('Could not authenticate client')
        data = response.json()
        now = datetime.datetime.now()
        access_token = data['access_token'] 
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)

        self.access_token = access_token

        self.access_token_expires = expires
        self.access_token_did_expire = expires < now
        return True

    def get_access_token(self):
        token = self.access_token
        expires = self.access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self.perform_auth()
            return self.get_access_token()
        elif token == None:
            self.perform_auth()
            return self.get_access_token()
        return token

    def get_resource_headers(self):
        access_token = self.get_access_token()
        headers = {'Authorization': f'Bearer {access_token}'}
        return headers

    def get_resource(self, lookup_id, resource_type='albums', version='v1'):
        endpoint = f'https://api.spotify.com/{version}/{resource_type}/{lookup_id}'
        headers = self.get_resource_headers()
        response = requests.get(endpoint, headers=headers)
        if response.status_code not in range(200, 299):
            return {}
        return response.json()

    def get_album(self, _id):
        return self.get_resource(_id, resource_type='albums')

    def get_artist(self, _id):
        return self.get_resource(_id, resource_type='artists')

    def base_search(self, query_params):
        headers = self.get_resource_headers()
        endpoint = 'https://api.spotify.com/v1/search'
        lookup_url = f'{endpoint}?{query_params}'

        response = requests.get(lookup_url, headers=headers)

        if response.status_code not in range(200,299):
            return {}
        return response.json()

    def search(self, query=None, operator=None, operator_query=None, search_type='artist'):
        if query == None:
            raise Exception('A query is required')
        if isinstance(query, dict):
            # turn dictionary into list
            query = ' '.join([f'{k}:{v}' for k,v in query.items()])
        if operator != None and operator_query != None:
            if operator.lower() == 'or' or operator.lower() == 'not':
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f'{query} {operator} {operator_query}'

        query_params = urlencode({'q': query, 'type': search_type.lower()})

        return self.base_search(query_params)


#spotify = SpotifyAPI(client_id, client_secret)
#searched = spotify.search(query='Danger', operator='NOT', operator_query='Zone', search_type='track')

#print(searched)

#access_token = spotify.access_token

