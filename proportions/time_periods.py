import numpy as np
import gdal
import os
import datetime
import glob
import sys
from dateutil.rrule import rrule, MONTHLY 

import utils

def process_files(current_files, prop_dir, max_extent, current_time):
    '''
    Process files in the current time period of interest
    '''
    if current_files == []:
        return

    for i, file in enumerate(current_files):
        # open the file    
        raster, MaxGeo, rasterproj = utils.open_raster(
                file, prop_dir, max_extent)

        #TODO figure out these two and if they need to be
            # outputs from open_raster function, 
            # and if they are the same every time
        #print(MaxGeo)
        #print(rasterproj)
        #breakpoint()


        if i == 0:
            shape = raster.shape #XXX or np.shape(raster) ?
            # initialize arrays
            openSW = np.zeros(shape)
            partialSW = np.zeros(shape)
            nonwater = np.zeros(shape)

        # reclassify layer and add to previous
        openSW_new, partialSW_new, nonwater_new = utils.reclassify(raster)
        openSW += openSW_new
        partialSW += partialSW_new
        nonwater += nonwater_new

    # maximum number any given pixel can be
    total_num = len(current_files)
    
    # calculate proportions open and partial surface water
    openSW_prop = utils.calculate_proportion(openSW, total_num)
    partialSW_prop = utils.calculate_proportion(partialSW, total_num)
    nonwater_prop = utils.calculate_proportion(nonwater, total_num)

    # create output files
    prop_data = [openSW_prop, partialSW_prop, nonwater_prop]
    data_str = ['openSW', 'partialSW', 'nonwater']

    for i, data in enumerate(prop_data):
        utils.create_output_file(data, data_str[i],
                prop_dir, current_time,
                MaxGeo, rasterproj)

    return


def process_by_year(all_files, all_dates, prop_dir, max_extent):
    ''' 
    Process files yearly.
    INPUTS: 
        all_files : list of str : list of paths to all DSWE files of interest 
        all_dates : list of dates : list of dates of files of interest
        prop_dir : str : path to save output data
        max_extent : list of float : max extent of all files; 
            in form [minx, maxy, maxx, miny] 
    RETURNS: 
        processed data saved in prop_dir
    '''
    all_years = [i.year for i in all_dates]
    start_year = min(all_years)
    end_year = max(all_years)

    for current_time in range(start_year, end_year+1):
        current_files = []
        # make a list of files in the current year of interest
        for i, file in enumerate(all_files):
            file_time = all_years[i]
            if file_time == current_time:
                current_files.append(file)

        # process files in current year of interest
        process_files(current_files, prop_dir, max_extent, current_time)
        print(f'Proportions completed for {current_time}')
    return


def process_by_month(all_files, all_dates, prop_dir, max_extent):
    '''
    Process files monthly.
    INPUTS: 
        all_files : list of str : list of paths to all DSWE files of interest 
        all_dates : list of dates : list of dates of files of interest
        prop_dir : str : path to save output data
        max_extent : list of float : max extent of all files; 
            in form [minx, maxy, maxx, miny] 
    RETURNS: 
        processed data saved in prop_dir
    '''
    start_date = datetime.date(min(all_dates).year, 1, 1)
    end_date = datetime.date(max(all_dates).year+1, 1, 1)

    for current_time in rrule(freq=MONTHLY, 
            dtstart=start_date, until=end_date):
        current_files = []
        # make a list of files in the current month of interest
        for i, file in enumerate(all_files):
            file_time = all_dates[i]
            if (file_time.month == current_time.month and
                    file_time.year == current_time.year):
                current_files.append(file)

        # process files in current month of interest
        process_files(current_files, prop_dir, max_extent, current_time)
        print(f'Proportions completed for {current_time.strftime("%b %Y")}')
    return


def process_by_month_across_years(all_files, all_dates, prop_dir, max_extent):
    '''
    Process files across all months for all years 
    INPUTS: 
        all_files : list of str : list of paths to all DSWE files of interest 
        all_dates : list of dates : list of dates of files of interest
        prop_dir : str : path to save output data
        max_extent : list of float : max extent of all files; 
            in form [minx, maxy, maxx, miny] 
    RETURNS: 
        processed data saved in prop_dir
    '''
    all_months = [i.month for i in all_dates] 
    start_month = min(all_months)
    end_month = max(all_months)

    for current_time in range(start_month, end_month+1):
        current_files = []
        # make a list of files in the current month of interest
        for i, file in enumerate(all_files):
            file_time = all_months[i]
            if file_time == current_time:
                current_files.append(file)
        
        # process files in current month of interest
        process_files(current_files, prop_dir, max_extent, current_time)
        month_str = datetime.date(1800,current_time,1)
        print(f'Proportions completed for {month_str.strftime("%B")}')
    return   


def process_by_semidecade(all_files, all_dates, prop_dir, max_extent):
    '''
    Process files semi-decadally (every 5 years)
    INPUTS: 
        all_files : list of str : list of paths to all DSWE files of interest 
        all_dates : list of dates : list of dates of files of interest
        prop_dir : str : path to save output data
        max_extent : list of float : max extent of all files; 
            in form [minx, maxy, maxx, miny] 
    RETURNS: 
        processed data saved in prop_dir
    '''
    all_years = [i.year for i in all_dates]
    start_year = min(all_years)
    end_year = max(all_years)

    for current_time in range(start_year, end_year+5, 5):
        current_files = []
        # make a list of files in the current semi-decade
            # of interest
        for i, file in enumerate(all_files):
            file_time = all_years[i]
            if (file_time - file_time%5) == current_time:
                current_files.append(file)

        # process files in current range of interest
        process_files(current_files, prop_dir, max_extent, current_time)
        print(f'Proportions completed for {current_time} to {current_time+4}')
    return


def process_by_season(all_files, all_dates, prop_dir, max_extent):
    '''
    Process files seasonally;
    seasons defined meteorologically:
        N. Hemisphere | S. Hemisphere | Start Date
        Winter        | Summer        | 1 Dec
        Spring        | Autumn        | 1 March
        Summer        | Winter        | 1 June
        Autumn        | Spring        | 1 Sept
    INPUTS: 
        all_files : list of str : list of paths to all DSWE files of interest 
        all_dates : list of dates : list of dates of files of interest
        prop_dir : str : path to save output data
        max_extent : list of float : max extent of all files; 
            in form [minx, maxy, maxx, miny] 
    RETURNS: 
        processed data saved in prop_dir
    '''
    start_date = datetime.date(min(all_dates).year-1, 12, 1)
    end_date = datetime.date(max(all_dates).year+1, 1, 1)

    for current_time in rrule(freq=MONTHLY, interval=3,
            dtstart=start_date, until=end_date):
        current_files = []
        current_time_range = utils.find_season_time_range(current_time)
        # make a list of files in the current month of interest
        for i, file in enumerate(all_files):
            file_time = all_dates[i]
            if (file_time.month in current_time_range and
                    file_time.year == current_time.year):
                current_files.append(file)

        # process files in current season of interest
        process_files(current_files, prop_dir, max_extent, current_time)
        season = utils.find_season(current_time_range)
        print(f'Proportions completed for {season} {current_time.year}')
    return


