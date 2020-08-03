'''
Example code to download scenes from a user-provided list
that contains a column labelled "scene_IDs" and a column
labelled "product_IDs"
'''
# if use_api.py is in same directory as this script, can comment out these two lines:
import sys
sys.path.insert(1, '../')

from use_api import download_list, untar

# output directory for downloaded data
output_dir = '/home/mad/DSWE_EaD/test_data/list_scenes'

# path for list of scene IDs (csv format)
csv_path = '/home/mad/DSWE_EaD/test_data/id_list.csv'

# if using DSWE datasets, keep these two variables the same
#dataset = 'SP_TILE_DSWE'
#product = 'DSWE'
#dataset = 'LSR_LANDSAT_TM_C1'
dataset = 'LANDSAT_TM_C1'
product = 'poop'


# download all datasets in the list
download_list(output_dir, dataset, product, csv_path)

# untar the downloaded files
untar(output_dir)








