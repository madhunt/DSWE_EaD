'''
Example code to download scenes from a user-provided list
'''
# if use_api.py is in same directory as this script, can comment out these two lines:
import sys
sys.path.insert(1, '../')

from use_api import download_list

# output directory for downloaded data
output_dir = '/home/mad/DSWE_EaD/test_data/scenes'

# path for list of scene IDs (csv format)
sceneids_path = '/home/mad/DSWE_EaD/test_data/id_list.csv'

# if using DSWE datasets, keep these two variables the same
dataset = 'SP_TILE_DSWE'
product = 'DSWE'

# download all datasets in the list
download_list(output_dir, dataset, product, sceneids_path)

# untar the downloaded files
untar(output_dir)








