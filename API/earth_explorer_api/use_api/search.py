

import sys
sys.path.insert(1, '../')


from utils import login



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



