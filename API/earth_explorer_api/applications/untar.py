'''
Untars downloaded data into folders of the same name.
'''
import argparse
import os
import tarfile

from login import login

def main(output_dir, delete_tars):
    '''
    Untars downloaded data into folders of the same name.
    INPUTS:
        output_dir : str : path to directory with tar files
    OPTIONAL INPUTS:
        delete_tars : bool : if True, delete tar files once data is downloaded
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
            if delete_tars:
                os.remove(full_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Untars downloaded data into folders of the same name.')
    parser.add_argument('output_dir',
            metavar='OUTPUT_DIR', type=str,
            help='path to directory with downloaded data')
    parser.add_argument('delete_tars',
            choices=[True,False], type=bool,
            default=True,
            help='if True, delete tar files once data is extracted')

    args = parser.parse_args()
    main(**vars(args))
