'''
Example code to download all search results for DSWE datasets from Winous Point Marsh, Bay Township, OH 43452
'''
# if use_api.py is in same directory as this script, can comment out these two lines:
import sys
sys.path.insert(1, '../')

import numpy as np
from use_api import download_all_scenes, untar

# output directory for downloaded data
output_dir = '/home/mad/DSWE_EaD/proportions/test_data/20yrspan'

# if using DSWE datasets, keep these two variables the saem
dataset = 'SP_TILE_DSWE' 
product = 'DSWE' 

# type out optional search filters here
# for a full list of filters, see use_api.py
latitude = 41.4626 
longitude = -82.9960 

# download 5 files from each year for 10 years
years = np.arange(1985, 1996)
for year in years:
    start_date = str(year) + '-01-01'
    end_date = str(year+1) + '-01-01'
    max_results = 5
    download_all_scenes(output_dir, dataset, product, latitude=latitude, longitude=longitude, months=months, start_date=start_date, end_date=end_date, max_results=max_results)

# untar the downloaded files in the same directory
untar(output_dir)


