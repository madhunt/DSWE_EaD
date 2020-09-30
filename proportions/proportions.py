'''
Main code to calculate proportions.
'''
import argparse
import os
import utils_proportions as utils
import time_periods as tp

def main(main_dir, dswe_layer, time_period, multiyear=None):
    '''
    Calculate proportions of pixels inundated with open or 
    partial surface water over time.
    INPUTS:
        main_dir : str : main directory where DSWE data is located
        dswe_layer : str : DSWE layer to be used in calculations ;
            INWM or INTR
        time_period : str : time period to process files by;
            year, month, month_across_years, season, multiyear 
        multiyear : int : integer number of years to process files by;
            only required if timeperiod=multiyear
    RETURNS:
        processes and saves data
    '''
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

    # initialize extent to be overwritten
    extent_0 = [1e12, -1e12, -1e12, 1e12]

    # loop through all files to calculate max extent
    #XXX is this the correct way of calculating this??
    for file in all_files:
        extent_0 = utils.find_max_extent(file, extent_0)
    max_extent = extent_0

    # gather and process files depending on time period chosen
    if time_period == 'year':
        tp.process_by_year(all_files, all_dates, prop_dir, max_extent)
    elif time_period == 'month':
        tp.process_by_month(all_files, all_dates, prop_dir, max_extent)
    elif time_period == 'month_across_years':
        tp.process_by_month_across_years(all_files, all_dates, prop_dir, max_extent)
    elif time_period == 'season':
        tp.process_by_season(all_files, all_dates, prop_dir, max_extent)
    elif 'multiyear' in time_period:
        tp.process_by_multiyear(all_files, all_dates, prop_dir, max_extent, multiyear)

    print('Processing done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate proportions of pixels inundated with open or partial surface water over time.')

    parser.add_argument('main_dir', 
            metavar='DIRECTORY_PATH', type=str,
            help='main directory where DSWE data is located')
    parser.add_argument('dswe_layer', 
            type=str.upper, 
            choices=['INWM', 'INTR'], 
            help='DSWE layer to be used in calculations' )
    parser.add_argument('time_period',
            type=str.lower, 
            choices=['year', 'month', 'month_across_years', 'season', 'multiyear'], 
            help='time period to process files by')
    parser.add_argument('-y', 
            metavar='NUM_YEARS', dest='multiyear',
            type=int, required=False, 
            help='integer number of years to process files by; only required if timeperiod=multiyear')

    args = parser.parse_args()

    if args.time_period == 'multiyear' and args.multiyear == None:
        parser.error('for multiyear time period, must specify number of years with -m NUM_YEARS')
    
    main(**vars(args))
