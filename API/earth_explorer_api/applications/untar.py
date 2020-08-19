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
    filenames = []
    # list everything in the directory
    entries = os.listdir(output_dir)

    # get a list of only tar files in the directory
    for entry in entries:
        full_path = os.path.join(output_dir, entry)
        if os.path.isfile(full_path) and tarfile.is_tarfile(full_path):
            filenames.append(full_path)

    for i, filename in enumerate(filenames):
        print(f'Extracting file {i+1} of {len(filenames)}')
        # open and extract data
        tar_file = tarfile.open(filename)
        tar_file.extractall(f'{filename}_extracted')
        
        # close and delete tar file
        tar_file.close()
        if delete_tars:
            os.remove(filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Untars downloaded data into folders of the same name.')
    parser.add_argument('output_dir',
            metavar='OUTPUT_DIR', type=str,
            help='path to directory with downloaded data')
    parser.add_argument('--delete_tars',
            dest='delete_tars',
            action='store_true',
            help='if flagged, delete tar files once data is extracted')

    args = parser.parse_args()
    main(**vars(args))
