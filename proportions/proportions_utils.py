'''
Utility functions for get_proportions.py
Includes making directories and output files, 
basic calculations, and reclassifying layers.

'''
import numpy as np
import gdal
import os
import datetime


def get_file_date(filename):
    '''
    Uses convention of scene_id (entity_id) as filename.
    '''
    file_year = int(filename[15:19])
    file_month = int(filename[19:21])
    file_day = int(filename[21:23])
    file_date = datetime.date(file_year, file_month, file_day)
    return file_date


def make_dirs(main_dir):
    '''
    Creates directories to process data and store results in.
    INPUTS:
        main_dir : str : path to main directory 
            with input data in subfolders
    RETURNS:
        process_dir : str : path to processing directory
        prop_dir : str : path to annual proprtions directory
        dec_prop_dir : str : path to semi-decadal proportions directory
    '''
    # create output directories (subfolders in main_dir)
    prop_dir = os.path.join(main_dir, 'proportions')
    
    os.makedirs(prop_dir, exist_ok=True)
    
    return prop_dir


def find_max_extent(file, extent_0):
    '''
    Determine the maximum extent of all files;
    ensures that no images are cropped and that 
    extent/georeferencing remains consistent
    INPUTS:
        file : current file being processed
        extent_0 : list : initial extent values to be 
            overwritten; in order [minx, maxy, maxx, miny]
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
    print("Opened:", file)
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




