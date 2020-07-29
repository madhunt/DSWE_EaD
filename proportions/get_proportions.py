
import os
import sys
import proportions_utils as utils
from time_periods import *


def main(main_dir, DSWE_layer, time_period):
    
    # move to main directory
    os.chdir(main_dir)

    # make a list of DSWE files of interest and their dates
    all_files = []
    all_dates = []
    # look through all directories and subdirectories
    for dirpath, dirnames, filenames in os.walk(main_dir):
        # find all files in tree
        for filename in filenames:
            # if the file is the layer of interest
            if DSWE_layer in filename:
                all_files.append(os.path.join(dirpath, filename))
                file_date = utils.get_file_date(filename)
                all_dates.append(file_date)

    # make output directories
    #TODO is there any need for a processing dir anymore?
    prop_dir = utils.make_dirs(main_dir)

    num_files = len(all_files)
    print(f'Processing {num_files} Total Scenes')

    # initialize extent to be overwritten 
    extent_0 = [1e12, -1e12, -1e12, 1e12]

    # loop through all files to calculate max extent
    for file in all_files:
        extent_0 = utils.find_max_extent(file, extent_0)
    max_extent = extent_0

    # gather and process files depending on time period
    if time_period == 'year':
        process_by_year(all_files, all_dates, prop_dir, max_extent)
    elif time_period == 'month':
        process_by_month(all_files, all_dates, prop_dir, max_extent)
    elif time_period == 'month_across_years':
        process_by_month_across_years(all_files, all_dates, prop_dir, max_extent)
    elif time_period == 'season':
        process_by_season(all_files, all_dates, prop_dir, max_extent)
    elif time_period == 'semidecade':
        process_by_semidecade(all_files, all_dates, prop_dir, max_extent)

    else:
        raise Exception(f'{time_period} is not a valid time period!')

    print('Processing done!!')

    return



main_dir = '/home/mad/DSWE_EaD/proportions/test_data/20yrspan_take2'
DSWE_layer = 'INWM' #or 'INTR'
time_period = 'month'


main(main_dir, DSWE_layer, time_period)

