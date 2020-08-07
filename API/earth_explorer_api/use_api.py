'''
Functions to search scenes and download data 
using the EarthExplorer API
'''
import earthExplorerAPI as eeapi
import getpass
import json
import os
import urllib.request
import tarfile
import csv
import re

def login():
    '''
    Call API and login.
    If environment variables EROS_USERNAME and EROS_PASSWORD exist,
    do not prompt for username and password.
    '''
    # get login information
    username = os.environ.get('EROS_USERNAME','')
    if username == '':
        username = input('EROS Username:')

    password = os.environ.get('EROS_PASSWORD', '')
    if password == '':
        password = getpass.getpass()
    
    # login to EROS account
    api = eeapi.API(username, password)
    return api


def search_datasets(**kwargs):
    '''
    Search available datasets. By passing no parameters, all 
    available datasets are returned.
    OPTIONAL INPUTS:
        dataset_str : str : used as a filter with wildcards at
            beginning and end of supplied value
        public_only : bool : if True, filter out datasets not 
            accessible to unauthenticated users; defaults to False
        latitude : float : decimal degree coordinate in EPSG:4326
            projection
        longitude : float : decimal degree coordinate in EPSG:4326
            projection
        bbox : tuple : (xmin, ymin, xmax, ymax) of the bounding box
        start_date : str : YYYY-MM-DD
        end_date : str : YYYY-MM-DD; defaults to start_date if
            not given
    RETURNS:
        search_results : list of dict : results of the search; 
            also printed to screen
    '''
    # login to EROS account
    api = login()
    search_results = api.dataset_search(**kwargs)
    print(json.dumps(search_results, indent=4))
    
    # logout of EROS account
    api.logout()

    return search_results


def search(dataset, **kwargs):
    '''
    Use EarthExplorer API to search for scenes
    INPUTS: 
        dataset : str : dataset name
    OPTIONAL INPUTS: 
        latitude : float : decimal degree coordinate in EPSG:4326
            projection
        longitude : float : decimal degree coordinate in EPSG:4326
            projection
        bbox : tuple : (xmin, ymin, xmax, ymax) of the bounding box
        months : list of int : limit results to specific months (1-12)
        start_date : str : YYYY-MM-DD
        end_date : str : YYYY-MM-DD; defaults to start_date if not given
        include_unknown_cloud_cover : bool : defaults to False
        min_cloud_cover : int : min cloud cover percentage (0-100);
            defaults to 0
        max_cloud_cover : int : max cloud cover percentage (0-100);
            defaults to 100
        additional_criteria : list : currently not supported
        max_results : int : max number of results displayed;
            defaults to 20
    RETURNS: 
        scenes : list of dict : search results with metadata
    '''
    api = login()

    # search all scenes
    scenes = api.search(dataset, **kwargs)
    print(f'{len(scenes)} scenes found')
    
    # logout of EROS account
    api.logout()
    return scenes


def download_search(output_dir, dataset, download_code=None, **kwargs):
    '''
    Use EarthExplorer API to search and download scenes as tar files.
    INPUTS: 
        output_dir : str : output directory for downloaded data
        dataset : str : name to identify dataset
    OPTIONAL INPUTS:
        download_code : str : download code to identify product; 
            key 'downloadCode' in download_options() response
        latitude : float : decimal degree coordinate in EPSG:4326
            projection
        longitude : float : decimal degree coordinate in EPSG:4326
            projection
        bbox : tuple : (xmin, ymin, xmax, ymax) of the bounding box
        months : list of int : limit results to specific months (1-12)
        start_date : str : YYYY-MM-DD
        end_date : str : YYYY-MM-DD; defaults to start_date if
            not given
        include_unknown_cloud_cover : bool : defaults to False
        min_cloud_cover : int : min cloud cover percentage (0-100);
            defaults to 0
        max_cloud_cover : int : max cloud cover percentage (0-100);
            defaults to 100
        additional_criteria : list : currently not supported
        max_results : int : max number of results displayed;
            defaults to 20
    RETURNS: 
        downloads search results as tar files to output directory
    '''
    api = login()
    
    # search all scenes
    scenes = api.search(dataset, **kwargs)
    print(f'{len(scenes)} scenes found')
    
    # make output directory (if doesn't yet exist)
    os.makedirs(output_dir, exist_ok=True)
    
    for i, scene in enumerate(scenes, start=1):
        print(f'Downloading scene {i} of {len(scenes)}')

        # get scene identifier
        entity_id = scene['entityId']
        # use scene identifier as filename 
        filename = os.path.join(output_dir, entity_id)
        
        # get download code if unknown
        if download_code == None:
            download_code, _ = api.download_options(dataset, entity_id)

        # get download information
        response = api.download(dataset, download_code, entity_id)
        url = response[0]['url']
        
        # download dataset
        urllib.request.urlretrieve(url, filename)

    # logout of EROS account
    api.logout()


def download_list(output_dir, csv_path, dataset=None, scene_ids=True):
    '''
    Download scenes from a given list of scene or product IDs.
    INPUTS:
        output_dir: str : directory to download data in
        csv_path : str : path to CSV containing scene or product IDs
    OPTIONAL INPUTS:
        dataset : str : name to identify dataset (if all ids are 
            from the same dataset); if None, will assign Landsat
            datasets
        scene_ids : bool : if True, CSV contains scene IDs; 
            if False, CSV contains product IDs
    RETURNS:
        tar files downloaded in output_dir
    '''
    # login to EROS account
    api = login()

    print('Converting CSV to list')
    if scene_ids == True:
        # csv contains scene IDs
        scene_ids = csv_to_list(csv_path, 'scene')

        if dataset == None:
            # need to assign Landsat datasets
            datasets = []
            scene_ids_real = []
            for i, scene_id in enumerate(scene_ids):
                # find dataset
                dataset = landsat_dataset(scene_id)
                if dataset == '':
                    # CSV did not contain an ID
                    continue
                datasets.append(dataset)
                scene_ids_real.append(scene_id)
            scene_ids = scene_ids_real

    elif scene_ids == False:
        # csv contains product IDs
        product_ids = csv_to_list(csv_path, 'product')

        if dataset == None:
            # need to assign Landsat datasets
            datasets = []
            scene_ids = []
            for i, product_id in enumerate(product_ids):
                print(f'Finding scene ID and dataset {i+1} of {len(product_ids)}')
                # find dataset
                dataset = landsat_dataset(product_id)
                if dataset == '':
                    # CSV did not contain an ID
                    continue
                datasets.append(dataset)

                # find scene ID
                try:
                    scene_id = api.id_lookup(dataset, product_id,
                                                input_field='displayId')
                except Exception:
                    # invalid product ID
                    continue
                scene_ids.append(scene_id[0])
        else:
            # given dataset
            scene_ids = api.id_lookup(dataset, product_ids,
                                        input_field='displayId')
    
    # download data
    for i, entity_id in enumerate(scene_ids):
        print(f'Downloading scene {i+1} of {len(scene_ids)}')
        if datasets:
            dataset = datasets[i]
        
        # create output filename
        filename = os.path.join(output_dir, entity_id)

        # get download code
        try:
            download_code, _ = api.download_options(dataset, entity_id)
        except Exception:
            print('no download code :(')
            print(download_code)
            continue

        # get download information
        response = api.download(dataset, download_code, entity_id)
        if response == []:
            raise Exception('No dataset matches the inputs provided')
            continue
        
        # download dataset
        url = response[0]['url']
        urllib.request.urlretrieve(url, filename)
    
    # logout of EROS account
    api.logout()


def landsat_dataset(data_id):
    '''
    INPUTS:
        data_id : str : either scene or product ID
    RETURNS:
        dataset : str : corresponding Landsat dataset string
    '''
    info = data_id[0:4]
    if ('LT05' in info) or ('LT5' in info):
        # Landsat 4-5 thematic mapper collection 1 level 1
        dataset = 'LANDSAT_TM_C1'
    elif('LE07' in info) or ('LE7' in info):
        # Landsat 7 ETM plus collection 1
        dataset = 'LANDSAT_ETM_C1'
    elif ('LC08' in info) or ('LC8' in info):
        # Landsat 8 operational land images plus thermal infrared
        dataset = 'LANDSAT_8_C1'
    else:
        return ''
    return dataset


def csv_to_list(csv_path, header_str):
    '''
    Convert csv file column to list.
    INPUTS: 
        csv_path : str : path to csv document
        header_str : str : string to search for in column headers
    RETURNS:
        col_list : list : list of data in specified column
    '''
    col_list = []

    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)

        for row in reader:
            for cols in row.items():
                header = cols[0]
                col_list_search = re.compile(f'{header_str}[ _]id',
                                                flags=re.IGNORECASE)

                if col_list_search.search(header):
                    col_list.append(cols[1])
    if col_list == []:
        raise Exception(f'No column called {header_str} in CSV')

    return col_list 


def untar(output_dir):
    '''
    Untars downloaded data and deletes tar files, leaving an
    untar-ed folder of the same name.
    INPUTS:
        output_dir : str : path to directory with tar files
    RETURNS:
        untar-ed data in same directory
    '''
    for (dirpath, dirnames, filenames) in os.walk(output_dir):
        for filename in filenames:
            # get path to tar files
            full_path = os.path.join(dirpath, filename)
            
            # open and extract data
            tar_file = tarfile.open(full_path)
            tar_file.extractall(f'{full_path}_extracted')
            
            # close and delete tar file
            tar_file.close()
            os.remove(full_path)

