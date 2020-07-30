'''
Functions to sort files by time period and process data.
'''
import datetime
import numpy as np
from dateutil.rrule import rrule, MONTHLY
import utils

def process_files(current_files, prop_dir, max_extent, time_str):
    '''
    Process files in the current time period of interest.
    INPUTS:
        current_files : list of str : list of paths to current file
        prop_dir : str : path to directory to store processed data
        max_extent : list of float : max extent of all files;
            in form [minx, maxy, maxx, miny]
        time_str : str : time period for filename
    RETURNS:
       saves processed data in prop_dir
    '''
    if current_files == []:
        # no file to be processed for this time period
        return

    for i, file in enumerate(current_files):
        # open the file
        raster, geo_transform, projection = utils.open_raster(
            file, prop_dir, max_extent)

        if i == 0:
            shape = raster.shape
            # initialize arrays
            open_sw = np.zeros(shape)
            partial_sw = np.zeros(shape)
            nonwater = np.zeros(shape)
        else:
            # ensure that geo_transform and projection stay the same
            #XXX unsure if they would ever change
            assert geo_transform_0 == geo_transform
            assert projection_0 == projection
        geo_transform_0 = geo_transform
        projection_0 = projection

        # reclassify layer and add to previous
        open_sw_new, partial_sw_new, nonwater_new = utils.reclassify(raster)
        open_sw += open_sw_new
        partial_sw += partial_sw_new
        nonwater += nonwater_new

    # maximum number any given pixel can be
    total_num = len(current_files)

    # calculate proportions open and partial surface water
    open_sw_prop = utils.calculate_proportion(open_sw, total_num)
    partial_sw_prop = utils.calculate_proportion(partial_sw, total_num)
    nonwater_prop = utils.calculate_proportion(nonwater, total_num)

    # create output files
    prop_data = [open_sw_prop, partial_sw_prop, nonwater_prop]
    data_str = ['open_sw', 'partial_sw', 'nonwater']

    for i, data in enumerate(prop_data):
        utils.create_output_file(data, data_str[i],
                prop_dir, time_str,
                geo_transform, projection)


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
        time_str = str(current_time)
        process_files(current_files, prop_dir, max_extent, time_str)
        print(f'Proportions completed for {time_str}')


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
        time_str = current_time.strftime("%b_%Y")
        process_files(current_files, prop_dir, max_extent, time_str)
        print(f'Proportions completed for {time_str}')


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
        month_str = datetime.date(1800, current_time, 1)
        time_str = month_str.strftime("%B")
        process_files(current_files, prop_dir, max_extent, time_str)
        print(f'Proportions completed for {time_str}')


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
        time_str = str(current_time) + '_' + str(current_time+4)
        process_files(current_files, prop_dir, max_extent, time_str)
        print(f'Proportions completed for {time_str}')


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
        season = utils.find_season(current_time_range)
        time_str = season + '_' + str(current_time.year)
        process_files(current_files, prop_dir, max_extent, time_str)
        print(f'Proportions completed for {time_str}')
