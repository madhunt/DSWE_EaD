'''
Functions to search scenes and download data using the EarthExplorer API
'''
import earthExplorerAPI as eeapi
import getpass
import os
import urllib.request
#import time
import tarfile
import csv

def login():
    '''
    Call API and login
    '''
    # get login information
    username = getpass.getpass(prompt='EROS Username:')
    print(f'EROS Username: {username}')
    password = getpass.getpass()
    
    # login to EROS account
    api = eeapi.API(username, password)
    return api


def search(dataset, **kwargs):
    '''
    Use EarthExplorer API to search for scenes
    INPUTS: 
        dataset : str : dataset name
    KWARGS INCLUDE: 
        latitude : float, optional : decimal degree 
            coordinate in EPSG:4326 projection
        longitude : float, optional : decimal degree 
            coordinate in EPSG:4326 projection
        bbox : tuple, optional : (xmin, ymin, xmax, ymax) 
            of the bounding box
        months : list of int, optional : limit results to 
            specific months (1-12)
        start_date : str, optional : YYYY-MM-DD
        end_date : str, optional : YYYY-MM-DD; defaults 
            to start_date if not given
        include_unknown_cloud_cover : bool, optional : defaults
            to False
        min_cloud_cover : int, optional : min cloud cover 
            percentage (0-100); defaults to 0
        max_cloud_cover : int, optional : max cloud cover 
            percentage (0-100); defaults to 100
        additional_criteria : list, optional : 
            currently not supported
        max_results : int, optional : max number of results 
            displayed; defaults to 20
    RETURNS: 
        scenes : list of dict : search results displayed 
            in a list of dicts with metadata
    '''
    api = login()

    # search all scenes
    scenes = api.search(dataset, **kwargs)
    print(f'{len(scenes)} scenes found')
    
    # logout of EROS account
    api.logout()
    return scenes


def download_search(output_dir, dataset, product, **kwargs):
    '''
    Use EarthExplorer API to search and download scenes 
    as tar files.
    INPUTS: 
        output_dir : str : output directory for downloaded data
        dataset : str : name to identify dataset
        product : str : string to identify the product; 
            called 'downloadCode' in download_options response
    KWARGS INCLUDE: 
         latitude : float, optional : decimal degree 
            coordinate in EPSG:4326 projection
        longitude : float, optional : decimal degree 
            coordinate in EPSG:4326 projection
        bbox : tuple, optional : (xmin, ymin, xmax, ymax)
            of the bounding box
        months : list of int, optional : limit results to 
            specific months (1-12)
        start_date : str, optional : YYYY-MM-DD
        end_date : str, optional : YYYY-MM-DD; defaults 
            to start_date if not given
        include_unknown_cloud_cover : bool, optional : 
            defaults to False
        min_cloud_cover : int, optional : min cloud cover 
            percentage (0-100); defaults to 0
        max_cloud_cover : int, optional : max cloud cover 
            percentage (0-100); defaults to 100
        additional_criteria : list, optional : 
            currently not supported
        max_results : int, optional : max number of results 
            displayed; defaults to 20
    RETURNS: 
        downloads all search results as tar files to 
        output directory
    '''
    api = login()
    
    # search all scenes
    scenes = api.search(dataset, **kwargs)
    print(f'{len(scenes)} scenes found')
    
    # make output directory (if doesn't yet exist)
    os.makedirs(output_dir, exist_ok=True)
    
    for i, scene in enumerate(scenesi, start=1):
        print(f'downloading scene {i} of {len(scenes)}')
        
        # get scene identifier
        entity_id = scene['entityid']
        # use scene identifier as filename 
        filename = os.path.join(output_dir, entity_id)
        
        # get download information
        response = api.download(dataset, product, entity_id)
        url = response[0]['url']
        
        # download dataset
        urllib.request.urlretrieve(url, filename)

    # logout of EROS account
    api.logout()
    return


def download_list(output_dir, dataset, product, sceneids_path):
    '''
    Download scenes from a given list of scene IDs.
    INPUTS:
        output_dir: str : path to directory for downloaded data
        dataset : str : name to identify dataset
        product : str or list of str : string (or list the 
            same length as scene_ids) to identify the 
            product(s); called 'downloadCode' in
            download_options response
        scene_ids_path : str : path to list of scene ids 
            (csv file)
    RETURNS:
        tar files downloaded in output_dir
    '''
    api = login()

    scene_ids = csv_to_list(sceneids_path)
    
    for i, row in enumerate(scene_ids, start=1):
        print(f'downloading scene {i} of {len(scene_ids)}')
        
        if isinstance(row, list):
            # if there are multiple columns in the csv
            # assume scene ID is in first column
            scene = row[0]
        else:
            scene = row

        # create output filename
        filename = os.path.join(output_dir, scene)

        if isinstance(product, list):
            # if given a list of product strings
            product_str = product[i-1]
        else: 
            # if given a single product for all scenes
            product_str = product
        
        # get download information
        response = api.download(dataset, product_str, scene)
        url = response[0]['url']
        
        # download dataset
        urllib.request.urlretrieve(url, filename)

    # logout of EROS account
    api.logout()
    
    return


def csv_to_list(csv_path):
    '''
    Convert csv file to list
    INPUTS: 
        csv_path : str : path to csv document
    RETURNS:
        data_list : list : csv data in list format
    '''
    with open(csv_path, newline='') as f:
        reader = csv.reader(f)
        data_list = list(reader)
    return data_list


def untar(output_dir):
    '''
    Untars downloaded data and deletes tar files,
    leaving an untar-ed folder of the same name.
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
    return

