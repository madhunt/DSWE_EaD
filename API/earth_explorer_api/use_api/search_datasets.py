


import sys
sys.path.insert(1, '../')


from utils import login


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










