'''
Download all data from /path/to/mycsv.csv, which contains a column of Landsat scene IDs. Save this data in /path/to/output.
'''
import sys
sys.path.insert(1, '../')
sys.path.insert(1, '../../')
from download_list import main

# output directory for downloaded data
output_dir = '/path/to/output'

# path for list of scene IDs (csv format)
csv_path = '/path/to/mycsv.csv'

# download all datasets in the list
main(output_dir, csv_path, scene_ids=True, dataset=False, landsat=True)
