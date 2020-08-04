
# if use_api.py is in same directory as this script, can comment out these two lines:
import sys
sys.path.insert(1, '../')

from use_api import *

# output directory for downloaded data
output_dir = '/home/mad/DSWE_EaD/test_data/debug'

## if using DSWE datasets, keep these two variables the same
#dataset = 'SP_TILE_DSWE' 
#download_code = None#'DSWE' 
#
## type out optional search filters here
## for a full list of filters, see use_api.py
#latitude = 41.4626 
#longitude = -82.9960 
#max_results = 10 
#
## call the function in use_api.py with the relevant parameters
#download_search(output_dir, dataset, download_code, 
#                latitude=latitude, longitude=longitude, 
#                max_results=max_results)

# path for list of scene IDs (csv format)
csv_path = '/home/mad/DSWE_EaD/test_data/id_list.csv'


# download all datasets in the list
#download_list(output_dir, csv_path, scene_ids=False, dataset=None)



# test dataset search
search_datasets()




