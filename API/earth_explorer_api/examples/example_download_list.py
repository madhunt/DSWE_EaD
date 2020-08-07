'''
Example code to download scenes from a user-provided list
that contains a column labelled "scene_IDs".
'''
# if use_api.py is in same directory as this script, can comment out these two lines:
import sys
sys.path.insert(1, '../')

from use_api import download_list

# output directory for downloaded data
output_dir = '/home/mad/DSWE_EaD/test_data/list_scenes'

# path for list of scene IDs (csv format)
csv_path = '/home/mad/DSWE_EaD/test_data/id_list_backup.csv'


# download all datasets in the list
download_list(output_dir, csv_path, dataset=None, scene_ids=True)

