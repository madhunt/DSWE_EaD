'''
Utility functions for filter_valid_data.py
'''
import getopt
import os
import gdal
import numpy as np

def get_files(main_dir):
    '''
    Make a list of all INTR files in the directory.
    INPUTS:
        main_dir : str : path to directory containing data
    RETURNS:
        all_files : list of str : list of paths to all INTR files
    '''
    all_files = []
    for dirpath, _, filenames in os.walk(main_dir):
        for filename in filenames:
            if 'INTR' in filename:
                all_files.append(os.path.join(dirpath, filename))
    return all_files


def open_raster(file):
    '''
    Open raster from a given file.
    INPUTS:
        file : str : path to TIF file
    RETURNS:
        raster : numpy array : array of raster data
    '''
    raster = gdal.Open(os.path.abspath(file))
    raster = raster.GetRasterBand(1).ReadAsArray()
    return raster


def percent_valid(raster):
    '''
    Calculates percent of valid (non-255) pixels in a given raster.
    INPUTS:
        raster : numpy array : array of raster data
    RETURNS:
        percent : float : percent of valid data in the raster
    '''
    # replace valid pixels with 1 and invalid (255) pixels with 0
    valid_data = np.where(raster == 255, 0, 1)

    # count the number of valid pixels
    n = np.count_nonzero(valid_data)
    
    # calculate the percentage of valid pixels out of all pixels
    total = raster.shape[0] * raster.shape[1]
    percent = n / total * 100
    return percent
