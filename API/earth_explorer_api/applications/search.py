'''
Search for scenes using the EarthExplorer API.
'''

import sys
import argparse
import json
from login import login



def main(dataset, **kwargs):
    '''
    Search for scenes using the EarthExplorer API.
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

    print(json.dumps(scenes, indent=4))
    
    # logout of EROS account
    api.logout()
    return scenes


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search for scenes using the EarthExplorer API.')

    parser.add_argument('dataset',
            metavar='DATASET', type=str,
            help='name to identify dataset')
    
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
            help='YYY-MM-DD')
    parser.add_argument('--end',
            dest='end_date', type=str,
            help='YYY-MM-DD; defaults to start date if not given')
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


