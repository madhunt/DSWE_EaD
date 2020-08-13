'''
Utility functions for proportions.py
'''
import datetime
import getopt
import os
import sys
import gdal
import numpy as np
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta


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


def get_files(main_dir, dswe_layer):
    '''
    Creates list of DSWE files with the layer of interest
    and list of file dates.
    INPUTS:
        main_dir : str : main directory where data is located
        dswe_layer : str : DSWE layer to be used in calculations
    RETURNS:
        all_files : list of str : list of all relevant DSWE file paths
        all_dates : list of dates : list of all file dates
    '''
    all_files = []
    all_dates = []
    # look through all directories and subdirectories
    for dirpath, _, filenames in os.walk(main_dir):
        # find all files in tree
        for filename in filenames:
            # if the file is the layer of interest
            if dswe_layer in filename:
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


def get_corner(file):
    '''
    Get coordinates of top left corner of raster.
    INPUTS:
        file : str : filename of interest
    RETURNS:
        top_left : tuple : coordinates of corner (x_min, y_max)
            and filename of interest
    '''
    raster = gdal.Open(os.path.abspath(file))
    geo_transform = raster.GetGeoTransform()
    
    x_size = raster.RasterXSize
    y_size = raster.RasterYSize
    x_res = geo_transform[1]
    y_res = geo_transform[5]

    x_min = geo_transform[0]
    y_max = geo_transform[3]

    top_left = (x_min, y_max, file)

    return top_left


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
    #XXX is this correct? appears to be decreasing every time
        # (finding minimum instead of maximum extent)
    if minx < extent_0[0]:
        extent_0[0] = minx
    if maxy > extent_0[1]:
        extent_0[1] = maxy
    if maxx > extent_0[2]:
        extent_0[2] = maxx
    if miny < extent_0[3]:
        extent_0[3] = miny
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
        file : str : path to current file to open
        prop_dir : str : path to directory to temporarially save raster
        max_extent : list of float : max extent of all files;
            in form [minx, maxy, maxx, miny]
    RETURNS:
        raster : numpy array : array form of raster image
        geo_transform : tuple : raster positions related to
            georeferences coordinates by affine transform
        projection : list : GDAL projection metadata
    '''
    # open the current file
    raster = gdal.Open(os.path.abspath(file))

    # expand layer to max extent of all data for the path/row
    raster_max_extent = os.path.join(prop_dir, 'raster_temp.tif')
    raster = gdal.Translate(raster_max_extent, raster, projWin=max_extent)
    
    geo_transform = raster.GetGeoTransform()
    projection = raster.GetProjection()
    raster = raster.GetRasterBand(1).ReadAsArray()

    # remove temp file
    os.remove(raster_max_extent)
    return raster, geo_transform, projection


def reclassify(raster):
    '''
    Reclassify the layer with observations of interest
    as 1 and observations not of interest as 0;
    invalid observations are mapped to -1e12
    INPUTS:
        raster : numpy array : array of image raster
    RETURNS:
        open_sw : numpy array : open surface water pixels
        partial_sw : numpy array : partial surface water pixels
        nonwater : numpy array : non-water pixels
    DSWE CLASSIFICATION: for INTR and INWM layers
        Pixel Value | rasterretation
            0       |   not open_sw
            1       |   open_sw, high confidence
            2       |   open_sw, mod confidence
            3       |   potential wetland
            4       |   open_sw/wetland, low confidence
            9       |   cloud/snow (INWM only)
            255     |   no data
    REFERENCES:
        LANDSAT DSWE Product Guide, pg. 10
    '''
    # VALID observations: NOT no data or cloud/snow
    valid = np.ones(np.shape(raster))
    valid[(raster == 9)|(raster == 255)] = 0

    # NO INUNDATION: nonwater
    nonwater = (raster == 0).astype(float)

    # OPEN SURFACE WATER: water, high/mod confidence
    open_sw = ((raster == 1)|(raster == 2)).astype(float)

    # PARTIAL SURFACE WATER: wetland, water low confidence
    partial_sw = ((raster == 3)|(raster == 4)).astype(float)
    return open_sw, partial_sw, nonwater, valid


def calculate_proportion(data, total):
    '''
    Calculate proportion of time each pixel in data is spent
    in that state, out of 100%.
    '''
    # taking advantage of the fact that array([0])/array([0])=nan
        # so silence the invalid value warnings
    with np.errstate(divide='ignore', invalid='ignore'):
        proportion = data / total * 100.

    # now set those nans we took advantage of to 255
        # as these are invalid pixels
    proportion[np.isnan(proportion)] = 255
    return proportion


def create_output_file(data, data_str, prop_dir, time_str, geo_transform, projection):
    '''
    Creates output file for data in designated directory
    INPUTS:
        data : numpy array : processed raster data
        data_str : str : string corresponding with type of data
        prop_dir : str : path to output directory
        time_str : str : time period for filename
        geo_transform : tuple : raster positions related to
            georeferences coordinates by affine transform
        projection : list : GDAL projection metadata
    RETURNS:
        output file in output_dir
    '''
    # create output filename
    filename = time_str + '_' + data_str + '_proportion.tif'
    file_path = os.path.join(prop_dir, filename)

    i = 1
    while os.path.isfile(file_path):
        # file already exists
        filename = time_str + '_' + data_str + f'_proportion({i})' + '.tif'
        file_path = os.path.join(prop_dir, filename)
        i += 1

    shape = data.shape

    # create output file
    driver = gdal.GetDriverByName('GTiff') # save as geotiff
    outdata = driver.Create(file_path, shape[1], shape[0], 1, gdal.GDT_Byte)
    outdata.SetGeoTransform(geo_transform)
    outdata.SetProjection(projection)
    outdata.GetRasterBand(1).SetNoDataValue(255)
    outdata.GetRasterBand(1).WriteArray(data)
    outdata.FlushCache()
