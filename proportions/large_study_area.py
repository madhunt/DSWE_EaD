'''
Main code to calculate proportions.
'''
import argparse
import os
import utils
import time_periods as tp

import gdal
import osr
import itertools
import operator

main_dir = '/home/mad/DSWE_EaD/test_data/DRB_test/data/good_data'
dswe_layer = 'INWM'
time_period = 'year'



# move to main directory
os.chdir(main_dir)

# make a list of DSWE files of interest and their dates
all_files, all_dates = utils.get_files(main_dir, dswe_layer)
num_files = len(all_files)
print(f'Processing {num_files} total scenes from {min(all_dates)} to {max(all_dates)}')

# make output directory
if time_period == 'multiyear':
    time_period = time_period + '_' + str(multiyear)
prop_dir = utils.make_output_dir(main_dir, time_period)

# get corners of each file

all_top_left = []
#all_bot_right = []

for file in all_files:
    
    def get_corners(file):
        raster = gdal.Open(os.path.abspath(file))
        geo_transform = raster.GetGeoTransform()
        
        x_size = raster.RasterXSize
        y_size = raster.RasterYSize
        x_res = geo_transform[1]
        y_res = geo_transform[5]

        x_min = geo_transform[0]
        y_max = geo_transform[3]
        #x_max = x_min + x_res * x_size
        #y_min = y_max + y_res * y_size

        top_left = (x_min, y_max, file)
        #bot_right = (x_max, y_min, file)

        return top_left#, bot_right

    top_left = get_corners(file)

    all_top_left.append(top_left)
    #all_bot_right.append(bot_right)

# now we have lists of all top left and bottom right corners


# sort top left from small to large x val
all_top_left.sort(key=lambda t:t[0])

for key, group in itertools.groupby(all_top_left, operator.itemgetter(1)):
    group = list(group)
    group_files = [i[2] for i in group]
    group_dates = []

    # get group dates
    for file in group_files:
        _, filename = os.path.split(file)
        file_date = utils.get_file_date(filename)
        group_dates.append(file_date)



    # initialize extent to be overwritten
    extent_0 = [1e12, -1e12, -1e12, 1e12]

    # loop through all files to calculate max extent
    #XXX is this the correct way of calculating this??
    for file in group_files:
        extent_0 = utils.find_max_extent(file, extent_0)
        print(extent_0)
    max_extent = extent_0

    # now we need to process each group with proportions code
    

    if time_period == 'year':
        tp.process_by_year(group_files, group_dates, prop_dir, max_extent)
    elif time_period == 'month':
        tp.process_by_month(group_files, group_dates, prop_dir, max_extent)
    elif time_period == 'month_across_years':
        tp.process_by_month_across_years(group_files, group_dates, prop_dir, max_extent)
    elif time_period == 'season':
        tp.process_by_season(group_files, group_dates, prop_dir, max_extent)
    elif 'multiyear' in time_period:
        tp.process_by_multiyear(group_files, group_dates, prop_dir, max_extent, multiyear)

    # make sure you aren't writing over files that exist!!!!

    # NOW have to combine final results



