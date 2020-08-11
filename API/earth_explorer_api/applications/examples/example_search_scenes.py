'''
Example code to search results for DSWE datasets from Winous Point Marsh, Bay Township, OH 43452
'''
import sys
sys.path.insert(1, '../')
sys.path.insert(1, '../../')
from search import main as search

# if using DSWE datasets:
dataset = 'SP_TILE_DSWE' 

# type out optional search filters here
latitude = 41.4626 
longitude = -82.9960 
months = [5,6,7,8] # e.g. limit results to summer months
start_date = '1990-01-01' # e.g. limit results to these dates
end_date = '2000-01-01'
max_results = 20 # e.g. only give the first 20 search results

# call the function in use_api.py with the relevant parameters
scenes = search(dataset, 
        latitude=latitude, longitude=longitude,
        months=months, start_date=start_date, end_date=end_date,
        max_results=max_results)
