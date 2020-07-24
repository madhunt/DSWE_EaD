'''
Utility functions for get_proportions.py
Includes making directories and output files, 
basic calculations, and reclassifying layers.

'''
import numpy as np
import gdal
import os

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
    # move to working directory in current sub-folder
    #wdir = os.path.join(main_dir, folder)
    #os.chdir(wdir)
    # create output directories (subfolders in main_dir)
    process_dir = os.path.join(main_dir, 'processing')
    prop_dir = os.path.join(main_dir, 'Proportions')
    dec_prop_dir = os.path.join(main_dir, 'DecadalProportions')
    
    os.makedirs(process_dir, exist_ok=True)
    os.makedirs(prop_dir, exist_ok=True)
    os.makedirs(dec_prop_dir, exist_ok=True)
    
    return process_dir, prop_dir, dec_prop_dir


def find_max_extent(raster, extent_0):
    '''
    Determine the maximum extent of all rasters;
    ensures that no images are cropped and that 
    extent/georeferencing remains consistent
    INPUTS:
        raster : current raster being processed
        extent_0 : list : initial extent values to be 
            overwritten; in order [minx, maxy, maxx, miny]
    RETURNS:
        extent_0 : list : updated extent values 
    '''
    # calculate extent of current raster
    interp = gdal.Open(os.path.abspath(raster))
    interpgeo=interp.GetGeoTransform()
    interpproj=interp.GetProjection()
    
    minx = interpgeo[0]
    maxy = interpgeo[3]
    maxx = minx + interpgeo[1] * interp.RasterXSize
    miny = maxy + interpgeo[5] * interp.RasterYSize

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


def open_interp(raster, process_dir, max_extent):
    '''
    Open file and get out data.
    INPUTS:
        raster : 
        process_dir : 
        max_extent : 
    RETURNS:
        interp : 
        MaxGeo : 
        shape : 
    '''
    #TODO figure out exactly what all of these variables are
    #TODO document this function

    interp = gdal.Open(os.path.abspath(raster))
    print("Opened:", raster)
    interpmaxextent_out= process_dir + "/interp.tif"
    #Expand every interpreted layer to the maximum extent of all data for the path/row
    interp=gdal.Translate(interpmaxextent_out, interp, projWin = max_extent)
    MaxGeo=interp.GetGeoTransform()
    interpproj = interp.GetProjection()
    interp=interp.GetRasterBand(1).ReadAsArray()
    shape=interp.shape
    return interp, MaxGeo, shape, interpproj


def reclassify_interp_layer(interp):
    '''
    Reclassify the interpreted layer with observations 
    of interst as '1' and observations not of interest as '0'
    INPUTS:
        interp : 
    RETURNS:
        openSW : 
        partialSW : 
        nonwater : 
    DSWE CLASSIFICATION: for INTR and INWM layers
        Pixel Value | Interpretation
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
    # no data or cloud/snow
    interp[np.where((interp==255) | (interp==9))] = 0

        #TODO ask if this is what Dr. Jones meant by 'valid observations' -- are ones with 255 invalid?
        # so are invalid results already accounted for in this line, since this is removed from everything
        # (and thus also from containsdata further down)?
    
    openSW=interp.copy()
    # high/moderate confidence openSW
    openSW[np.where((openSW==1) | (openSW==2))] = 1
    openSW[np.where((openSW==4) | (openSW==3))] = 0

    partialSW=interp.copy()
    # potential wetland
    partialSW[np.where((partialSW==3))] = 1
    partialSW[np.where((partialSW==1) | (partialSW==2) | (partialSW==4))] = 0
    
    nonwater=interp.copy()
    #TODO why is not openSW 4 and low confidence 1?
    nonwater[np.where((nonwater==0))] = 4
    nonwater[np.where((nonwater==4))] = 1
    nonwater[np.where((nonwater==1) | (nonwater==2) | (nonwater==3))] = 0
    return openSW, partialSW, nonwater


def create_output_file(data, data_str, output_dir, PathRow, year, shape, MaxGeo, interpproj):
    '''
    Creates output file for data in designated directory
    INPUTS:
        data : 
        data_str : str : 
        output_dir : str : 
        PathRow : str : 
        year : str OR list of str : 
        shape : 
        MaxGeo : 
        interpproj : 
    RETURNS:
        output file in output_dir
    '''
    # create output filename
    if 'DecadalProportions' in output_dir:
        filename = 'DSWE_V2_P1_' + PathRow + '_' + year[0] + '_' + year[1] + '_openSW_Proportion.tif'
    elif 'processing' in output_dir:
        filename = '/DSWE_V2_P1_' + PathRow + '_' + year + '_' + data_str + 'sum.tif'
    elif 'Proportions' in output_dir:
        filename = '/DSWE_V2_P1_' + PathRow + '_' + year + '_' + data_str + '_Proportion.tif'
    # output file path
    file_path = os.path.join(output_dir, filename)
    
    # create output file
    driver = gdal.GetDriverByName("GTiff")
    data_out = driver.Create(file_path, shape[1], shape[0], 1, gdal.GDT_Byte)
    data_out.SetGeoTransform(MaxGeo)
    data_out.SetProjection(interpproj)
    data_out.GetRasterBand(1).WriteArray(data)
    return


def calculate_proportion(data, total):
    '''
    Calculate proportion of data in total; 
    rounded to nearest integer and out of 100
    '''
    proportion = data / np.float32(total) * 100
    np.rint(proportion)
    return proportion


def years_to_process(rasters):
    year_rasters = []
    for raster in rasters:
        raster_year = int(raster[18:22])
        print('CHECK year should be', raster_year)
        if raster_year >= Active_yr and raster_year <= Range_yr:
            year_rasters.append(raster)
    return year_rasters

def sum_annual_rasters(year_rasters, shape):
    data = np.zeros(shape)
    for raster in year_rasters:
        new_data = gdal.Open(os.path.abspath(raster))
        new_data = new_data.GetRasterBand(1).ReadAsArray()
        data += new_data
    return data




