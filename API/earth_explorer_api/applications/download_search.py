'''
Download all scenes from a search on EarthExplorer.
'''
import argparse
import os
import sys
import urllib.request
from login import login


def main(output_dir, dataset, download_code=None, **kwargs):
    '''
    Download all scenes from a search on EarthExplorer.
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download all scenes from a search on EarthExplorer.')

    parser.add_argument('output_dir',
            metavar='OUTPUT_DIR', type=str,
            help='directory to download data to')
    parser.add_argument('dataset',
            metavar='DATASET', type=str,
            help='name to identify dataset')
    
    parser.add_argument('--download_code',
            default=None, type=str,
            help='download code to identify product; downloadCode in download_options() response')
    
    parser.add_argument('--lat',
            dest='latitude', type=float,
            help='decimal degree coordinate in ESPG:4326')
    parser.add_argument('--long',
            dest='longitude', type=float,
            help='decimal degree coordinate in ESPG:4326')
    parser.add_argument('--bbox',
            type=tuple,
            help='(xmin, ymin, xmax, ymax) of the bounding box')
    parser.add_argument('--months',
            type=list,
            help='list of int to limit results to specific months (1-12)')
    parser.add_argument('--start',
            dest='start_date', type=str,
            help='start date; YYYY-MM-DD')
    parser.add_argument('--end',
            dest='end_date', type=str,
            help='YYYY-MM-DD; defaults to start date if not given')
    parser.add_argument('--unknown_cloud',
            dest='include_unknown_cloud_cover', type=bool,
            choices=[True,False],
            help='include unknown cloud cover; defaults to False')
    parser.add_argument('--min_cloud',
            dest='min_cloud_cover', type=int,
            help='minimum cloud cover percentage (0-100); defaults to 0')
    parser.add_argument('--max_cloud',
            dest='max_cloud_cover', type=int,
            help='maximum cloud cover percentage (0-100); defaults to 100')
    parser.add_argument('--max_results',
            type=int,
            help='maximum number of results per search; defaults to 20')
 
    args = parser.parse_args()

    if args.latitude and args.bbox:
        parser.error('Either latitude/longitude or bounding box can be specified, not both.')

    main(**vars(args))
