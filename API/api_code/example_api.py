

from use_api import download_all_scenes



# example code to download all search results for DSWE datasets from Winous Point Marsh, Bay Twonship, OH 43452
output_dir = './data_test1/'
dataset = 'SP_TILE_DSWE' # this magic string is for DSWE datasets
product = 'DSWE' # this magic string is also for DSWE datasets



latitude = 41.4626 
longitude = -82.9960 
max_results = 40000

include_unknown_cloud_cover = True



download_all_scenes(output_dir, dataset, product, latitude=latitude, longitude=longitude, min_cloud_cover=0, max_cloud_cover=70, max_results=max_results)



