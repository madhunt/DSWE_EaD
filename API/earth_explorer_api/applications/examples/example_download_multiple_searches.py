'''
Example code to download all search results for DSWE datasets from the Delaware River Basin

This code submits multiple download requests.
To prevent having to re-logging before every request, 
use the following to call this example in your terminal:
    EROS_USERNAME='<username>' EROS_PASSWORD='<password>' python3 example_download_multiple_searches.py
'''
import sys
sys.path.insert(1, '../')
sys.path.insert(1, '../../')
import numpy as np
from download_search import main as download_search
from untar import main as untar

# output directory for downloaded data
output_dir = '/home/mad/DSWE_EaD/test_data/cape_cod'

# if using DSWE datasets:
dataset = 'SP_TILE_DSWE' 
product = 'DSWE' 

# type out optional search filters here
#bbox = (38.679, -76.396, 42.462, -74.374) # DRB
bbox = (41.5, -70.75, 42.42, -69.75) # Cape Cod

#max_cloud_cover = 50

# download 5 files from each year for 30 years
years = np.arange(1980, 2020)
for year in years:
    start_date = str(year) + '-01-01'
    end_date = str(year+1) + '-01-01'
    max_results = 1000
    download_search(output_dir, dataset, download_code=product,
            bbox=bbox,
            start_date=start_date, end_date=end_date,
            max_results=max_results)

# untar the downloaded files in the same directory
untar(output_dir)
