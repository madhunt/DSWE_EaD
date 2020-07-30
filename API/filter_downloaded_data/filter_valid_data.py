'''
Sorts data into good and bad directories, depending if
the number of valid pixels in a raster is over a certain
percent.
'''
import shutil
import sys
import os

from utils import *

def main(argv):
    '''
    Takes a directory of DSWE data and sorts files into
    good or bad folders, depending if the percentage of 
    valid pixels in the data is over a certain percent.
    '''
    # get command line arguments
    main_dir, percent_good = command_line_args(argv)

    # make good and bad directories
    good_data = os.path.join(main_dir, 'good_data')
    bad_data = os.path.join(main_dir, 'bad_data')
    os.makedirs(good_data, exist_ok=True)
    os.makedirs(bad_data, exist_ok=True)
    
    # get all INTR files
    all_files = get_files(main_dir)

    for file in all_files:
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

if __name__ == '__main__':
    main(sys.argv[1:])
