'''
Sorts data into good and bad directories, depending if
the number of valid pixels in a raster is over a certain
percent.
'''
import argparse
import gdal
import numpy as np
import shutil
import os

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


def main(main_dir, percent_good):
    '''
    Takes a directory of DSWE data and sorts files into
    good or bad folders, depending if the percentage of 
    valid pixels in the data is over a certain percent.
    '''

    # make good and bad directories
    good_data = os.path.join(main_dir, 'good_data')
    bad_data = os.path.join(main_dir, 'bad_data')
    os.makedirs(good_data, exist_ok=True)
    os.makedirs(bad_data, exist_ok=True)
    
    # get all INTR files
    all_files = get_files(main_dir)

    for i, file in enumerate(all_files, start=1):
        # open raster and calculate percent valid data
        raster = open_raster(file)
        percent = percent_valid(raster)
        
        filedir, _ = os.path.split(file)
        _, dirname = os.path.split(filedir)

        if percent >= percent_good:
            # this is good data
            path_to = os.path.join(good_data, dirname)
        else:
            # this is bad data
            path_to = os.path.join(bad_data, dirname)
        
        # move data to good or bad folder
        shutil.move(filedir, path_to)

        print(f'{i} out of {len(all_files)} files sorted')

if __name__ == '__main__':
    # get command line arguments
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('main_dir',
                metavar='DIRECTORY_PATH', type=str,
                help='main directory where DSWE data is located')
    parser.add_argument('percent_good',
                metavar='PERCENT', type=float,
                help='desired percentage for valid data in a given file (float, 0-100)')

    args = parser.parse_args()

    main(**vars(args))
