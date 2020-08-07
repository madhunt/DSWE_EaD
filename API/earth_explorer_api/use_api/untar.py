import sys
sys.path.insert(1, '../')

import tarfile
import os


from utils import login

def untar(output_dir):
    '''
    Untars downloaded data and deletes tar files, leaving an
    untar-ed folder of the same name.
    INPUTS:
        output_dir : str : path to directory with tar files
    RETURNS:
        untar-ed data in same directory
    '''
    for (dirpath, dirnames, filenames) in os.walk(output_dir):
        for filename in filenames:
            # get path to tar files
            full_path = os.path.join(dirpath, filename)
            
            # open and extract data
            tar_file = tarfile.open(full_path)
            tar_file.extractall(f'{full_path}_extracted')
            
            # close and delete tar file
            tar_file.close()
            os.remove(full_path)


