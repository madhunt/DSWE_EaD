'''

'''
import sys
import os
import utils
from time_periods import *

def main(argv):
    # set up command line arguments
    main_dir, DSWE_layer, time_period = utils.command_line_args(argv)
    
    # move to main directory
    os.chdir(main_dir)

    # make a list of DSWE files of interest and their dates
    all_files, all_dates = utils.get_files(main_dir, DSWE_layer)
    num_files = len(all_files)
    print(f'Processing {num_files} total scenes from {min(all_dates)} to {max(all_dates)}')

    # make output directory
    prop_dir = utils.make_output_dir(main_dir, time_period)

    # initialize extent to be overwritten 
    extent_0 = [1e12, -1e12, -1e12, 1e12]

    # loop through all files to calculate max extent
    #TODO is this the correct way of calculating this??
    for file in all_files:
        extent_0 = utils.find_max_extent(file, extent_0)
    max_extent = extent_0

    # gather and process files depending on time period chosen
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
        raise Exception(f'{time_period} is not a valid time period')

    print('Processing done!')

    return


if __name__ == '__main__':
    main(sys.argv[1:])


