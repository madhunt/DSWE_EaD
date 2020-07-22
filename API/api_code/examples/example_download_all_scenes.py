'''
Example code to download all search results for DSWE datasets from Winous Point Marsh, Bay Township, OH 43452
'''
# if use_api.py is in same directory as this script, can comment out these two lines:
import sys
sys.path.insert(1, '../')

from use_api import download_all_scenes, untar

# output directory for downloaded data
output_dir = '../../../proportions/data_test/DSWE_out/'

# if using DSWE datasets, keep these two variables the saem
dataset = 'SP_TILE_DSWE' 
product = 'DSWE' 

# type out optional search filters here
# for a full list of filters, see use_api.py
latitude = 41.4626 
longitude = -82.9960 
months = [5,6,7,8] # e.g. limit results to summer months
start_date = '1990-01-01' # e.g. limit results to these dates
end_date = '2000-01-01'
max_results = 20 # e.g. only give the first 20 search results

# call the function in use_api.py with the relevant parameters
download_all_scenes(output_dir, dataset, product, latitude=latitude, longitude=longitude, months=months, start_date=start_date, end_date=end_date, max_results=max_results)

# untar the downloaded files in the same directory
untar(output_dir)


