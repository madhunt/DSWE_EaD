

import requests
import json

from datamodels import spatial_filter, temporal_filter


def json_request_format(**kwargs):
    return {'jsonRequest': json.dumps(kwargs)}


class API(object):

    def __init__(self, username, password, version='1.4.1'):
        self.version = version
        self.endpoint = f'https://earthexplorer.usgs.gov/inventory/json/v/{version}/'
        self.key = self.login(username, password)

    def request(self, request_code, **kwargs):
        url = self.endpoint + request_code

        if 'apiKey' is not in kwargs:
            kwargs.update(apiKey=self.key)

        params = json_request_format(**kwargs)
        response = requests.get(url, params=params).json()
        
        error = response['error']
        if error:
            raise Exception(f'Error raised by EarthExplorer API: {error}')
        
        data = response['data']
        return data

    def login(self, username, password):
        '''
        Login to EROS account and get an API key
        '''
        data = json_request_format(username=username, password=password, catalogID='EE')
        
        url = self.endpoint + 'login?'
        response = requests.post(url, data=data).json()

        error = response['error']
        if error:
            raise Exception(f'Error raised by EarthExplorer API: {error}')

        return reponse['data']

    def logout(self):
        self.request('logout')


    def search(self, dataset, latitude=None, longitude=None, bbox=None, 
                start_date=None, end_date=None, months=None,
                include_unknown_cloud_cover=True, min_cloud_cover=0, max_cloud_cover=100,
                additional_criteria=None, max_results=20):
        '''
        '''
        params = {'datasetName': dataset,
                'includeUnknownCloudCover': include_unknown_cloud_cover,
                'minCloudCover': min_cloud_cover,
                'maxCloudCover': max_cloud_cover,
                'maxResults': max_results}
        if latitude and longitude:
            params.update(spatialFilter=spatial_filter(latitude, longitude))
        if bbox: 
            params.update(spatialFilter=spatial_filter(*bbox))
        if start_date:
            params.update(temporalFilter=temporal_filter(start_date, end_date))
        if months:
            params.update(months=months)
        if additional_criteria:
            params.update(additionalCriteria=search_filter(additional_criteria)) #TODO make search filter function

        response = self.request('search', **params)

        return response['results']

    def lookup(self, dataset, id_list, input_field='entityId'):
        '''
        '''
        params = {'datasetName': dataset,
                    'idList': id_list,
                    'inputField': input_field}
        response = self.request('idlookup', **params)
        new_id_list = list(response.values())
        return new_id_list

    def metadata(self, dataset, id_list):
        '''
        '''
        if len(id_list[0]) == 40:
            # this is a product identifier
            id_list = self.lookup(dataset, id_list, input_field='displayId')

        params = {'datasetName': dataset,
                    'entityIds': id_list}
        response = self.request('metadata', **params)

        results = response['data']
        return results

    def dataset_search(self, dataset, latitude=None, longitude=None, bbox=None, 
                start_date=None, end_date=None):
        '''
        '''
        params = {'datasetName': dataset}
        if latitude and longitude:
            params.update(spatialFilter=spatial_filter(latitude, longitude))
        if bbox: 
            params.update(spatialFilter=spatial_filter(*bbox))
        if start_date:
            params.update(temporalFilter=temporal_filter(start_date, end_date))

        response = self.request('datasets', **params)

        results = response['data']
        return results












