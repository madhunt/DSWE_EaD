'''
Example code to download all search results for DSWE datasets from Winous Point Marsh, Bay Township, OH 43452

This code submits multiple download requests.
To prevent having to re-logging before every request, 
use the following to call this example in your terminal:
    EROS_USERNAME='<username>' EROS_PASSWORD='<password>' python3 example_download_multiple_searches.py
'''
# if use_api.py is in same directory as this script, can comment out these two lines:
import sys
sys.path.insert(1, '../')
sys.path.insert(1, '../../')
import numpy as np
from download_search import main as download_search
from untar import main as untar

# output directory for downloaded data
output_dir = '/path/to/output'

# if using DSWE datasets:
dataset = 'SP_TILE_DSWE' 
product = 'DSWE' 

# type out optional search filters here
latitude = 41.4626 
longitude = -82.9960
min_cloud_cover = 0
max_cloud_cover = 50

# download 5 files from each year for 30 years
years = np.arange(1980, 2019)
for year in years:
    start_date = str(year) + '-01-01'
    end_date = str(year+1) + '-01-01'
    max_results = 5
    download_search(output_dir, dataset, product, 
            latitude=latitude, longitude=longitude, 
            start_date=start_date, end_date=end_date,
            min_cloud_cover=min_cloud_cover, max_cloud_cover=max_cloud_cover,
            max_results=max_results)

# untar the downloaded files in the same directory
untar(output_dir)
