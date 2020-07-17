

import earthExplorerAPI as eeapi
import getpass

import requests
import os
import urllib.request

#def search_scenes(dataset, **kwargs):
    # latitude=None, longitude=None, bbox=None, months=None,
    # start_date=None, end_date=None,
    # include_unknown_cloud_cover=False, min_cloud_cover=0, max_cloud_cover=100,
    # additional_criteria=None, max_results=20

    # get login information
    #username = getpass.getpass(prompt='ERS Username:')
    #print(f'ERS Username: {username}')
    #password = getpass.getpass()

    #api = eeapi.API(username, password)

    #scenes = api.search(dataset, **kwargs)

    #print(f'{len(scenes)} scenes found')

    #return scenes

def download_all_scenes(output_dir, dataset, product, **kwargs):
    download_url = 'https://earthexplorer.usgs.gov/download/{folder}/{sid}/STANDARD/EE'

    chunk_size = 1024

    #scenes = search_scenes(dataset, **kwargs)

    # get login information
    username = getpass.getpass(prompt='ERS Username:')
    print(f'ERS Username: {username}')
    password = getpass.getpass()

    api = eeapi.API(username, password)

    scenes = api.search(dataset, **kwargs)

    print(f'{len(scenes)} scenes found')

    for scene in scenes:

        print(scene)

        entity_id = scene['entityId']

        filename = os.path.join(output_dir, entity_id)

        response = api.download(dataset, product, entity_id)
        url = response[0]['url']
        
        urllib.request.urlretrieve(url, filename)
        
    return


output_dir = './data_test/'
dataset = 'SP_TILE_DSWE'
product = 'DSWE'

latitude = 41.4626 
longitude = -82.9960 
max_results = 1

os.makedirs(output_dir, exist_ok=True)



download_all_scenes(output_dir, dataset, product, latitude=latitude, longitude=longitude, max_results=max_results)


    



