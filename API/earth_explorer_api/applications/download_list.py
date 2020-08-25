'''
Download scenes from a given CSV list of scene IDs or product IDs.
'''
import argparse
import csv
import os
import re
import urllib.request
from login import login

def main(output_dir, csv_path, scene_ids, dataset, landsat):
    '''
    Download scenes from a given list of scene IDs or product IDs.
    INPUTS:
        output_dir: str : directory to download data in
        csv_path : str : path to CSV containing scene or product IDs
        scene_ids : bool : if True, CSV contains scene IDs; 
            if False, CSV contains product IDs
    OPTIONAL INPUTS:
        dataset : str : name to identify dataset (if all ids are 
            from the same dataset)
        landsat : bool : if True, IDs in CSV are all from Landsat datasets
    RETURNS:
        tar files downloaded in output_dir
    '''
    # login to EROS account
    api = login()

    print('Converting CSV to list')
    if scene_ids == True:
        # csv contains scene IDs
        scene_ids = csv_to_list(csv_path, 'scene')

        if dataset == False and landsat == True:
            # assign datasets to scenes
            datasets, scene_ids = assign_datasets(scene_ids)

        elif dataset == False and landsat == False:
            # datasets are unknown but NOT landsat
            raise Exception('Must supply dataset name; this option is currently not supported')

        elif dataset == True:
            # csv contains datasets
            datasets = csv_to_list(csv_path, 'dataset')

            
    elif scene_ids == False:
        # csv contains product IDs
        product_ids = csv_to_list(csv_path, 'product')

        if dataset == False and landsat == True:
            # assign datasets and scenes to products
            datasets, scene_ids = assign_datasets_and_scenes(product_ids, api)

        if dataset == False and landsat == False:
            # datasets are unknown but NOT landsat
            raise Exception('Must supply dataset name; this option is currently not supported')

        elif dataset == True:
            # csv contains datasets
            datasets, scene_ids = assign_scenes(product_ids, api)

    # download data
    os.makedirs(output_dir, exist_ok=True)

    print(scene_ids)
    print(datasets)

    for i, entity_id in enumerate(scene_ids):
        print(f'Downloading scene {i+1} of {len(scene_ids)}')
        
        dataset = datasets[i]
        # create output filename
        filename = os.path.join(output_dir, entity_id)

        # get download code
        try:
            download_opts = api.download_options(dataset, entity_id)
            download_opts_list = download_opts[0]['downloadOptions']
            if len(download_opts_list) > 1:
                download_code = 'STANDARD'
            else:
                download_code = download_opts_list[0]['downloadCode']

        except Exception:
            print('No download code found for this scene.')
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


def assign_datasets(scene_ids):
    '''
    Assign datasets to scene IDs.
    '''
    datasets = []
    scene_ids_real = []
    for i, scene_id in enumerate(scene_ids):
        # find dataset
        dataset = landsat_dataset(scene_id, scene_id=True)
        if dataset == '':
            # CSV did not contain an ID
            continue
        datasets.append(dataset)
        scene_ids_real.append(scene_id)
    scene_ids = scene_ids_real
    return datasets, scene_ids_real


def assign_datasets_and_scenes(product_ids, api):
    '''
    Assign datasets and scene IDs to product IDs.
    '''
    datasets = []
    scene_ids = []
    for i, product_id in enumerate(product_ids):
        print(f'Finding scene ID and dataset {i+1} of {len(product_ids)}')
        # find dataset
        dataset = landsat_dataset(product_id, scene_id=False)
        if dataset == '':
            # CSV did not contain an ID
            continue
        datasets.append(dataset)

        # find scene ID
        try:
            scene_id = api.id_lookup(dataset, product_id,
                                        input_field='displayId')
        except Exception:
            print('Invalid product ID')
            # invalid product ID
            continue
        scene_ids.append(scene_id[0])
    return datasets, scene_ids


def assign_scenes(product_ids, api):
    '''
    Assign scenes to product IDs with known datasets.
    '''
    datasets = csv_to_list(csv_path, 'dataset')
    scene_ids = []
    for i, product_id in enumerate(product_ids):
        print(f'Finding scene ID {i+1} of {len(product_ids)}')
        dataset = datasets[i]
        try:
            scene_id = api.id_lookup(dataset, product_id,
                                        input_field='displayId')
        except Exception:
            print('Invalid product ID or dataset')
            # invalid product ID or dataset
            continue
        scene_ids.append(scene_id[0])
    return datasets, scene_ids


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
                col_list_search = re.compile(f'{header_str}',
                                                flags=re.IGNORECASE)

                if col_list_search.search(header):
                    col_list.append(cols[1])
    if col_list == []:
        raise Exception(f'No column called {header_str} in CSV')

    return col_list 


def landsat_dataset(data_id, scene_id=True):
    '''
    INPUTS:
        data_id : str : either scene or product ID
        scene_id : bool : if True, the data_id is a scene ID;
            if False, data_id is a product ID
    RETURNS:
        dataset : str : corresponding Landsat dataset string
    '''
    
    if scene_id == True:
        info = data_id[0:3]
    if scene_id == False:
        info = data_id[0:4]

    MSS_choices = ['LM01', 'LM02', 'LM03', 'LM04', 'LM05',
                    'LM1', 'LM2', 'LM3', 'LM4', 'LM5']
    TM_choices = ['LT04', 'LT05', 'LT4', 'LT5']
    ETM_choices = ['LE07', 'LE7']
    L8_choices = ['LC08', 'LC8']

    if info in MSS_choices:
        dataset = 'LANDSAT_MSS_C1'
    elif info in TM_choices:
        dataset = 'LANDSAT_TM_C1'
    elif info in ETM_choices:
        dataset = 'LANDSAT_ETM_C1'
    elif info in L8_choices:
        dataset = 'LANDSAT_8_C1'
    else:
        return ''
    return dataset


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download scenes from a given CSV list of scene IDs or product IDs (specify with --scene_ids or --product_ids).')

    parser.add_argument('output_dir',
            metavar='OUTPUT_DIR', type=str,
            help='directory to download data to')
    parser.add_argument('csv_path',
            metavar='CSV_PATH', type=str,
            help='path to CSV containing scene or product IDs')
    parser.add_argument('--dataset',
            dest='dataset',
            action='store_true',
            help='if flagged, CSV contains a column with dataset names')
    parser.add_argument('--landsat',
            dest='landsat',
            action='store_true',
            help='if flagged, IDs in CSV are all from Landsat datasets')

    id_type = parser.add_mutually_exclusive_group(required=True)
    id_type.add_argument('--scene_ids',
            dest='scene_ids',
            action='store_true',
            help='if flagged, CSV contains scene IDs')
    id_type.add_argument('--product_ids',
            dest='scene_ids',
            action='store_false',
            help='if flagged, CSV contains product IDs')

    args = parser.parse_args()

    main(**vars(args))
