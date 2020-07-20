# example code to download the first 20 search results for DSWE datasets from Winous Point Marsh, Bay Twonship, OH 43452
output_dir = './data_test1/'
dataset = 'SP_TILE_DSWE' # this magic string is for DSWE datasets
product = 'DSWE' # this magic string is also for DSWE datasets

#TODO add function to API class to enable searching for dataset and product (downloadCode) strings

latitude = 41.4626 
longitude = -82.9960 
max_results = 20

download_all_scenes(output_dir, dataset, product, latitude=latitude, longitude=longitude, max_results=max_results)


#TODO automate untar-ing files (note to windows users: 7-zip should support untar-ing files until I add this feature)

