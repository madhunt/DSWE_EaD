'''
Utility functions for proportions.py
'''
import numpy as np
import sys, getopt
import gdal
import os
import datetime
from dateutil.rrule import rrule, MONTHLY 
from dateutil.relativedelta import relativedelta

def command_line_args(argv):
    '''
    Handle command line arguments.
    INPUTS: 
        argv : list of str : options and arguments from command line
    RETURNS:
        main_dir : str : main directory where data is located
        DSWE_layer : str : DSWE layer to be used in calculations
        time_period : str : time period to perform calculations over
    '''
    main_dir = ''
    DSWE_layer = ''
    time_period = ''
    try:
        options, remainder = getopt.getopt(argv, 'hd:l:t:', ['help','directory=', 'layer=', 'timeperiod='])
    except getopt.GetoptError:
        help_message()
        sys.exit(2)
    if options == []:
        help_message()
        sys.exit()
    for opt, arg in options:
        if opt in ('-h', '--help'):
            help_message()
            sys.exit()
        elif opt in ('-d', '--directory'):
            main_dir = arg
        elif opt in ('-l', '--layer'):
            DSWE_layer = arg
        elif opt in ('-t', '--timeperiod'):
            time_period = arg

    return main_dir, DSWE_layer, time_period


def help_message():
    '''
    Help message to print for usage and options of 
    command line arguments.
    '''
    print('usage: proportions.py -d <directory> -l <layer> -t <timeperiod>')
    print('\t-d, --directory\t\t<directory>\tmain directory where data is located')
    print('\t-l, --layer\t\t<layer>\t\tDSWE layer to be used in calculations')
    print('\t\t\t\t{\'INWM\'|\'INTR\'}')
    print('\t-t, --timeperiod\t<timeperiod>\ttime period to perform calculations over')
    print('\t\t\t\t{\'year\'|\'month\'|\'month_across_years\'|\'semidecade\'|\'season\'}')
    print('\t-h, --help\t\tprint help message')
    return


def get_file_date(filename):
    '''
    Gets date that file data was collected; 
    uses convention of scene_id (entity_id) as filename.
    '''
    file_year = int(filename[15:19])
    file_month = int(filename[19:21])
    file_day = int(filename[21:23])
    file_date = datetime.date(file_year, file_month, file_day)
    return file_date


def get_files(main_dir, DSWE_layer):
    '''
    Creates list of DSWE files with the layer of interest
    and list of file dates.
    INPUTS: 
        main_dir : str : main directory where data is located
        DSWE_layer : str : DSWE layer to be used in calculations
    RETURNS:
        all_files : list of str : list of all relevant DSWE file paths
        all_dates : list of dates : list of all file dates
    '''
    all_files = []
    all_dates = []
    # look through all directories and subdirectories
    for dirpath, dirnames, filenames in os.walk(main_dir):
        # find all files in tree
        for filename in filenames:
            # if the file is the layer of interest
            if DSWE_layer in filename:
                all_files.append(os.path.join(dirpath, filename))
                file_date = get_file_date(filename)
                all_dates.append(file_date)
    return all_files, all_dates


def make_output_dir(main_dir, time_period):
    '''
    Create directory to store results in.
    INPUTS:
        main_dir : str : main directory where data is located
    RETURNS:
        prop_dir : str : path to directory where results will be stored 
    '''
    prop_dir = os.path.join(main_dir, f'proportions_{time_period}')
    os.makedirs(prop_dir, exist_ok=True)
    return prop_dir


def find_max_extent(file, extent_0):
    '''
    Determine the maximum extent of all files;
    ensures that no images are cropped and that 
    extent/georeferencing remains consistent
    INPUTS:
        file : str : path to current file being processed
        extent_0 : list : initial extent values to be overwritten; 
            in order [minx, maxy, maxx, miny]
    RETURNS:
        extent_0 : list : updated extent values 
    '''
    # calculate extent of current file
    raster = gdal.Open(os.path.abspath(file))
    geo_transform = raster.GetGeoTransform()

    minx = geo_transform[0]
    maxy = geo_transform[3]
    maxx = minx + geo_transform[1] * raster.RasterXSize
    miny = maxy + geo_transform[5] * raster.RasterYSize
    
    # rewrite extent with larger values
    #TODO check if this is correct -- appears to be decreasing every time (finding minimum instead of maximum extent)
    if minx < extent_0[0]:
        extent_0[0] = minx
    if maxy > extent_0[1]:
        extent_0[1]=maxy
    if maxx > extent_0[2]:
        extent_0[2]=maxx
    if miny < extent_0[3]:
        extent_0[3]=miny
    return extent_0


def find_season_time_range(current_time):
    '''   
    Find time range of a particular season.
    INPUTS:
        current_time : date : current time (beginning of season)
    RETURNS:
        current_time_range : list of int : list of months in season
    '''
    until_time = current_time + relativedelta(months=2)
    
    current_time_range = list(rrule(freq=MONTHLY,
            dtstart=current_time, until=until_time))
    current_time_range = [i.month for i in current_time_range]
    return current_time_range


def find_season(current_time_range):
    '''
    Assign a string to the season in the N. Hemisphere.
    INPUTS:
        current_time_range : list of int : list of months in the season
    RETURNS:    
        season : str : season in N. Hemisphere
    '''
    if 12 in current_time_range:
        season = 'Winter'
    if 3 in current_time_range:
        season = 'Spring'
    if 6 in current_time_range:
        season = 'Summer'
    if 9 in current_time_range:
        season = 'Autumn'
    return season


def open_raster(file, prop_dir, max_extent):
    '''
    Open file and read as array.
    INPUTS:
        file : 
        process_dir : 
        max_extent : 
    RETURNS:
        raster : 
        MaxGeo : 
        shape : 
    '''
    #TODO document this function

    raster = gdal.Open(os.path.abspath(file))
    #print("Opened:", file)
    rastermaxextent_out= prop_dir + "/raster.tif"
    #TODO is the above needed anymore
    #Expand every rasterreted layer to the maximum extent of all data for the path/row
    raster=gdal.Translate(rastermaxextent_out, raster, projWin = max_extent)
    MaxGeo=raster.GetGeoTransform()
    rasterproj = raster.GetProjection()
    raster=raster.GetRasterBand(1).ReadAsArray()
    return raster, MaxGeo, rasterproj


def reclassify(raster):
    '''
    Reclassify the layer with observations of interest 
    as 1 and observations not of interest as 0; 
    invalid observations are mapped to -1e12
    INPUTS:
        raster : 
    RETURNS:
        openSW : 
        partialSW : 
        nonwater : 
    DSWE CLASSIFICATION: for INTR and INWM layers
        Pixel Value | rasterretation
            0       |   not openSW
            1       |   openSW, high confidence
            2       |   openSW, mod confidence
            3       |   potential wetland
            4       |   openSW/wetland, low confidence
            9       |   cloud/snow (INWM only)
            255     |   no data
    REFERENCES:
        LANDSAT DSWE Product Guide, pg. 10

    '''
    # INVALID observations: no data or cloud/snow
    invalid = np.zeros(np.shape(raster))
    invalid[(raster==9) | (raster==255)] = float('nan')

    # NO INUNDATION: nonwater
    nonwater = (raster==0).astype(float) + invalid
    
    # OPEN SURFACE WATER: water, high/mod confidence
    openSW = ((raster==1) | (raster==2)).astype(float) + invalid

    # PARTIAL SURFACE WATER: wetland, water low confidence
    partialSW = ((raster==3) | (raster==4)).astype(float) + invalid
    
    return openSW, partialSW, nonwater


def calculate_proportion(data, total_num):
    '''
    Calculate proportion of time each pixel in data is spent
    in that state, out of 1.0
    '''
    proportion = data / total_num

    return proportion


def create_output_file(data, data_str, output_dir, current_time, MaxGeo, rasterproj):
    '''
    Creates output file for data in designated directory
    INPUTS:
        data : 
        data_str : str : 
        output_dir : str : 
        year : 
        shape : 
        MaxGeo : 
        rasterproj : 
    RETURNS:
        output file in output_dir
    '''
    
    # create output filename
    #TODO neaten these up
    filename = 'DSWE_V2_P1_' + str(current_time) + '_' + data_str + '_Proportion.tif'
    # output file path
    file_path = os.path.join(output_dir, filename)

    shape = data.shape
    # create output file

    driver = gdal.GetDriverByName('GTiff') # save as geotiff
    outdata = driver.Create(file_path, shape[1], shape[0], 1, gdal.GDT_Byte)
    outdata.SetGeoTransform(MaxGeo)
    outdata.SetProjection(rasterproj)
    outdata.GetRasterBand(1).WriteArray(data)
    outdata.FlushCache()

    return


def years_to_process(files):
    year_files = []
    for file in files:
        file_year = int(file[18:22])
        print('CHECK year should be', file_year)
        if file_year >= Active_yr and file_year <= Range_yr:
            year_files.append(file)
    return year_files

def sum_annual_files(year_files, shape):
    data = np.zeros(shape)
    for file in year_files:
        new_data = gdal.Open(os.path.abspath(file))
        new_data = new_data.GetfileBand(1).ReadAsArray()
        data += new_data
    return data




