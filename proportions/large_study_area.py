'''
Main code to calculate proportions.
'''
import argparse
import os
import utils
import time_periods as tp

import itertools
import operator
import gdal_merge


main_dir = '/home/mad/DSWE_EaD/test_data/DRB_test/data/good_data'
dswe_layer = 'INWM'
time_period = 'year'


def main(main_dir, dswe_layer, time_period, multiyear):
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
    for file in all_files:
        # get top left corner of each file
        top_left = utils.get_corner(file)
        all_top_left.append(top_left)

    # now we have lists of all top left and bottom right corners


    # sort top left from small to large x val
    key_func = lambda t: (t[0], t[1])
    all_top_left.sort(key=key_func)

    total_len = sum(1 for key,_ in itertools.groupby(all_top_left, operator.itemgetter(1)))
    i = 1

    for key, g in itertools.groupby(all_top_left, operator.itemgetter(1)):
        print(f'Processing group {i} of {total_len}')
        i += 1

        group = list(g)
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


    #
    # NOW have to combine final results

    # all files with same time_str and date_str need to be combined
    
    # list all files in prop_dir
    os.chdir(prop_dir)
    filenames = []
    for root, dirs, files in os.walk(prop_dir):
        for file in files:
            filenames.append(os.path.join(root, file))

    # splits filename at the '.tif' and 
        # the '(#)' if there are musltiple in the same time period
    key_func = lambda t: t.split('.')[0].split('(')[0]

    # sort filenames by time_str and proportion type 
    filenames.sort(key=key_func)

    # for printing purposes, find total length of files to merge
    total_len = sum(1 for key,_ in itertools.groupby(filenames, key=key_func))

    i = 1
    group = []
    for key, g in itertools.groupby(filenames, key=key_func):
        print(f'Merging group {i} of {total_len}: {os.path.split(key)[1]}')
        i += 1

        group = list(g)
        out_filename = key + '_merged.tif'

        # arguments to use in gdal_merge
        args = ['', '-o', out_filename, 
                    '-of', 'gtiff'] + group
        
        # use gdal_merge to combine images spatially
        gdal_merge.main(args)

        # delete files once merged
        for file in group:
            os.remove(file)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate proportions of pixels inundated with water over time, for a large study area composed of multiple DSWE tiles.')

    parser.add_argument('main_dir', 
            metavar='DIRECTORY_PATH', type=str,
            help='main directory where DSWE data is located (does not need to be sorted by lat/long)')
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
