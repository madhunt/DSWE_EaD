'''
Example code to download all search results for DSWE datasets from Winous Point Marsh, Bay Township, OH 43452
'''
# if use_api.py is in same directory as this script, can comment out these two lines:
import sys
sys.path.insert(1, '../')
sys.path.insert(1, '../../')
from download_search import main as download_search
from untar import main as untar

# output directory for downloaded data
output_dir = '/path/to/output'

# if using DSWE datasets:
dataset = 'SP_TILE_DSWE' 
product = 'DSWE' 

# for a full list of filters, see use_api.py
latitude = 41.4626 
longitude = -82.9960 
months = [6] # e.g. limit results to June only
start_date = '1986-01-01' # e.g. limit results to these dates
end_date = '1987-01-01'
max_results = 30 

# call the function in use_api.py with the relevant parameters
download_search(output_dir, dataset, product, 
        latitude=latitude, longitude=longitude, 
        months=months, start_date=start_date, end_date=end_date, 
        max_results=max_results)

# untar the downloaded files in the same directory
untar(output_dir)
