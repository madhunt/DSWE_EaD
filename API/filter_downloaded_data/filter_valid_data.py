'''
Sorts data into good and bad directories, depending if
the number of valid pixels in a raster is over a certain
percent.
'''
import argparse
import shutil
import os

from utils import *

def main(main_dir, percent):
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
    #main(sys.argv[1:])
    # get command line arguments
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('main_dir',
                metavar='DIRECTORY_PATH', type=str,
                help='main directory where DSWE data is located')
    parser.add_argument('percent',
                metavar='PERCENT', type=float,
                help='desired percentage for valid data in a given file (float, 0-100)')

    args = parser.parse_args()

    main(**vars(args))
