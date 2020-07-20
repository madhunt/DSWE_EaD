'''
Functions to search scenes and download data using the EarthExplorer API
'''
import earthExplorerAPI as eeapi
import getpass
import os
import urllib.request

def search_scenes(dataset, **kwargs):
    '''
    Use EarthExplorer API to search for scenes
    INPUTS: 
        dataset : str : dataset name
    KWARGS INCLUDE: 
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
        scenes : list of dict : search results displayed in a list of dicts with metadata
    '''

    # get login information
    username = getpass.getpass(prompt='ERS Username:')
    print(f'ERS Username: {username}')
    password = getpass.getpass()

    api = eeapi.API(username, password)

    scenes = api.search(dataset, **kwargs)

    print(f'{len(scenes)} scenes found')

    api.logout()

    return scenes

def download_all_scenes(output_dir, dataset, product, **kwargs):
    '''
    Use EarthExplorer API to search and download scenes as tar files.

    '''

    # get login information
    username = getpass.getpass(prompt='ERS Username:')
    #print(f'ERS Username: {username}')
    password = getpass.getpass()

    api = eeapi.API(username, password)

    scenes = api.search(dataset, **kwargs)

    print(f'{len(scenes)} scenes found')
    
    os.makedirs(output_dir, exist_ok=True)
    
    i = 1
    for scene in scenes:
        print(f'Downloading scene {i} of {len(scenes)}')

        entity_id = scene['entityId']

        filename = os.path.join(output_dir, entity_id)

        response = api.download(dataset, product, entity_id)
        url = response[0]['url']
        
        urllib.request.urlretrieve(url, filename)

        i += 1
       
    api.logout()

    return



