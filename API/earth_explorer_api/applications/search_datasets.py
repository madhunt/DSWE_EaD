'''
Search available datasets on EarthExplorer.
'''
import argparse
import json
from login import login

def main(**kwargs):
    '''
    Search available datasets. By passing no parameters, all 
    available datasets are returned.
    OPTIONAL INPUTS:
        dataset : str : used as a filter with wildcards at
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Search available datasets on EarthExplorer. By passing no parameters, all available datasets are returned.')

    parser.add_argument('--dataset',
            type=str,
            help='used as a filter with implied wildcards at beginning and end of supplied value')
    parser.add_argument('--public',
            type=bool, choices=[True,False], dest='public_only',
            help='if True, filter out datasets not accessible to unauthenticated users; defaults to False')
    parser.add_argument('--lat',
            type=float, dest='latitude',
            help='decimal degree coordinate in EPSG:4326')
    parser.add_argument('--long',
            type=float, dest='longitude',
            help='decimal degree coordinate in EPSG:4326')
    parser.add_argument('--bbox',
            type=tuple,
            help='(xmin, ymin, xmax, ymax) of the bounding box')
    parser.add_argument('--start',
            type=str, dest='start_date',
            help='start date; YYYY-MM-DD')
    parser.add_argument('--end',
            type=str, dest='end_date',
            help='YYYY-MM-DD; defaults to start date if not given')

    args = parser.parse_args()
    
    if args.latitude and args.bbox:
        parser.error('Either latitude/longitude or bounding box can be specified, not both.')

    main(**vars(args))
