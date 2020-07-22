'''
EarthExplorer API
Large parts of this code are based on:
    https://github.com/yannforget/landsatxplore
    MIT License
'''

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
        '''
        Base function to perform a get request on the EarthExplorer site.
        INPUTS:
            request_code : str : all request codes given at
                https://earthexplorer.usgs.gov/inventory/documentation/json-api?version=1.4.0#downloadoptions
            kwargs : dict, optional : parameters to use with given request code
        RETURNS:
            data : dict : response data in json format
        '''
        url = self.endpoint + request_code

        if 'apiKey' not in kwargs:
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
        Authenticate by logging in to EROS account and get an API key
        RETURNS:
            key : API key
        '''
        data = json_request_format(username=username, password=password, catalogID='EE')
        
        url = self.endpoint + 'login?'
        response = requests.post(url, data=data).json()

        error = response['error']
        if error:
            raise Exception(f'Error raised by EarthExplorer API: {error}')

        key = response['data']
        return key

    def logout(self):
        '''
        Log out of EROS account and invalidate API key
        '''
        self.request('logout')

    def search(self, dataset, latitude=None, longitude=None, bbox=None, 
                start_date=None, end_date=None, months=None,
                include_unknown_cloud_cover=True, min_cloud_cover=0, max_cloud_cover=100,
                additional_criteria=None, max_results=20):
        '''
        Search for scenes based on various criteria
        INPUTS: 
            dataset : str : dataset name
            latitude : float, optional : decimal degree coordinate in EPSG:4326 projection
            longitude : float, optional : decimal degree coordinate in EPSG:4326 projection
            bbox : tuple, optional : (xmin, ymin, xmax, ymax) of the bounding box
            months : list of int, optional : limit results to specific months (1-12)
            start_date : str, optional : YYYY-MM-DD
            end_date : str, optional : YYYY-MM-DD; defaults to start_date if not given
            include_unknown_cloud_cover : bool, optional : defaults to False
            min_cloud_cover : int, optional : min cloud cover percentage (0-100); defaults to 0
            max_cloud_cover : int, optional : max cloud cover percentage (0-100); defaults to 100
            additional_criteria : list, optional : currently not supported
            max_results : int, optional : max number of results displayed; defaults to 20
        RETURNS: 
            search_results : dict : search results as a dictionary
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
        search_results = response['results'] 

        return search_results 

    def id_lookup(self, dataset, id_list, input_field='entityId'):
        '''
        Translate between entity ID (scene identifiers) and display ID (product identifiers)
        INPUTS: 
            dataset : str : dataset name
            id_list : list of str : list of scene (entity) IDs or product (display) IDs
            input_field : str : 'entityId' if id_list is scenes or 'displayId' if given list is products
        RETURNS:
            new_id_list : list of str : list of translated IDs
        '''
        input_options = ['entityId', 'displayId']
        if input_field not in input_options:
            raise Exception(f'{input_field} is not a valid input_field; choose entityId or displayId')

        params = {'datasetName': dataset,
                    'idList': id_list,
                    'inputField': input_field}
        response = self.request('idlookup', **params)
        new_id_list = list(response.values())
        return new_id_list

    def metadata(self, dataset, id_list):
        '''
        Get metadata for a scene or list of scenes.
        INPUTS: 
            dataset : str : dataset name
            id_list : list of str : list of scene (entityIds) or product (displayIds)
        RETURNS:
            results : dict : results of the search as a dictionary
        '''
        if len(id_list[0]) == 40:
            # this is a product identifier
            id_list = self.id_lookup(dataset, id_list, input_field='displayId')

        params = {'datasetName': dataset,
                    'entityIds': id_list}
        response = self.request('metadata', **params)

        results = response['data']
        return results

    def dataset_search(self, dataset=None, latitude=None, longitude=None, bbox=None, 
                start_date=None, end_date=None):
        '''
        Search available datasets. By passing no parameters, all available datasets are returned.
        INPUTS:
            dataset : str, optional : dataset name; 
                limit results against public dataset name with wildcards at beginning and end
            latitude : float, optional : decimal degree coordinate in EPSG:4326 projection
            longitude : float, optional : decimal degree coordinate in EPSG:4326 projection
            bbox : tuple, optional : (xmin, ymin, xmax, ymax) of the bounding box
            start_date : str, optional : YYYY-MM-DD
            end_date : str, optional : YYYY-MM-DD; defaults to start_date if not given
        RETURNS:
            results : dict : results of the search as a dictionary
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

    def download(self, dataset, download_code, entity_ids):
        '''
        INPUTS:
            dataset : str : dataset name
            download_code : str : this is the download code given by download_options 
            entity_ids : str or list of str : identifies scene or scenes to get downloads for
        RETURNS: 
            response : dict : response including the download URL
        '''
        params = {'datasetName': dataset,
                    'products': download_code,
                    'entityIds': entity_ids}

        response = self.request('download', **params)
        return response

    def download_options(self ):
        '''
        This function will provide download options metadata, including the "downloadCode" needed to put in as the "product" when downloading files
                download_code used to download scenes is (response['data']['downloadOptions']['downloadCode'])
        '''
        return





