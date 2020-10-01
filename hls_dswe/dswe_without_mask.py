'''
DSWE algorithm implemented to support either Harmonized Landsat
Sentinel (HLS) or Landsat data as inputs.

This version does not calculate the masked layers, and does
not rely on a global DEM as input.

The input directory for this code should have HLS data as HDF4
files, or Landsat data as tar files. The output directory does
not have to exist, it will be created by the code.

Also assumes that a threshold.json file is in the same
directory as this code.
'''
import argparse
import gdal
import numpy as np
import os
import tarfile
import utils_dswe as utils

def diagnostic_setup(band_dict, fill):
    '''
    Calculate indexes based on non-fill (valid) pixels of
    input bands for diagnostic tests.
    INPUTS:
        band_dict : dict : dictionary with keys corresponding
            to the unscaled surface reflectance bands (blue,
            green, red, nir, swir1, and swir2) and values as
            paths to those bands or files
        fill : int : value of non-data (fill) pixels in the
            above bands
    RETURNS:
        mndwi : numpy array : Modified Normalized Difference
            Wetness Index 
        mbsrv : numpy array : Multi-band Spectral Relationship
            Visible
        mbsrn : numpy array : Multi-band Spectral Relationship
            Near-Infrared
        awesh : numpy array : Automated Water Extent Shadow
        ndvi : numpy array : Normalized Difference Vegetation
            Index
    '''
    # get bands as np arrays
    blue = utils.file_to_array(band_dict['blue'])
    green = utils.file_to_array(band_dict['green'])
    red = utils.file_to_array(band_dict['red'])
    nir = utils.file_to_array(band_dict['nir'])
    swir1 = utils.file_to_array(band_dict['swir1'])
    swir2 = utils.file_to_array(band_dict['swir2'])

    # calculate indexes and account for non-data (fill) values
    mndwi = (green - swir1) / (green + swir1)
    mndwi[(green == fill) | (swir1 == fill)] = fill
    
    mbsrv = green + red
    mbsrv[(green == fill) | (red == fill)] = fill
    
    mbsrn = nir + swir1
    mbsrn[(nir == fill) | (swir1 == fill)] = fill
    
    awesh = blue + (2.5 * green) - (1.5 * mbsrn) - (0.25 * swir2)
    awesh[(blue == fill) | (green == fill) |
            (mbsrn == fill) | (swir2 == fill)] = fill
    
    ndvi = (nir - red) / (nir + red)
    ndvi[(nir == fill) | (red == fill)] = fill

    return mndwi, mbsrv, mbsrn, awesh, ndvi


def diagnostic_tests(band_dict, mndwi, mbsrv, mbsrn, awesh, ndvi):
    '''
    Perform five diagnostic tests for each pixel using indexes
    and user-defined threshold values from thresholds.json.
    INPUTS:
        band_dict : dict : dictionary with keys corresponding
            to the unscaled surface reflectance bands (blue,
            green, red, nir, swir1, and swir2) and values as
            paths to those bands or files
        mndwi : numpy array : Modified Normalized Difference
            Wetness Index 
        mbsrv : numpy array : Multi-band Spectral Relationship
            Visible
        mbsrn : numpy array : Multi-band Spectral Relationship
            Near-Infrared
        awesh : numpy array : Automated Water Extent Shadow
        ndvi : numpy array : Normalized Difference Vegetation
            Index
    RETURNS:
        diag : numpy array : (n by m by 5) boolean array;
            third dimension contains boolean results for the
            5 diagnostic tests for each pixel
    '''
    # get threshold values from json file
    thresholds_dict = utils.get_thresholds()
    wigt = thresholds_dict['WIGT']
    awgt = thresholds_dict['AWGT']
    pswt_1_mndwi = thresholds_dict['PSWT_1_MNDWI']
    pswt_1_nir = thresholds_dict['PSWT_1_NIR']
    pswt_1_swir1 = thresholds_dict['PSWT_1_SWIR1']
    pswt_1_ndvi = thresholds_dict['PSWT_1_NDVI']
    pswt_2_mndwi = thresholds_dict['PSWT_2_MNDWI']
    pswt_2_blue = thresholds_dict['PSWT_2_BLUE']
    pswt_2_nir = thresholds_dict['PSWT_2_NIR']
    pswt_2_swir1 = thresholds_dict['PSWT_2_SWIR1']
    pswt_2_swir2 = thresholds_dict['PSWT_2_SWIR2']

    # get bands as np arrays
    blue = utils.file_to_array(band_dict['blue'])
    nir = utils.file_to_array(band_dict['nir'])
    swir1 = utils.file_to_array(band_dict['swir1'])
    swir2 = utils.file_to_array(band_dict['swir2'])
    
    # all bands are the same shape
    shape = blue.shape

    # test 1 : compare MNDWI to WIGT Wetness Index threshold
    test1 = np.full(shape, False, dtype=bool)
    test1[mndwi > wigt] = True

    # test 2 : compare MBSRV and MBSRN values to each other
    test2 = np.full(shape, False, dtype=bool)
    test2[mbsrv > mbsrn] = True

    # test 3 : compare AWESH to AWGT Automated Water Extent
        # Shadow threshold
    test3 = np.full(shape, False, dtype=bool)
    test3[awesh > awgt] = True

    # test 4 : compare MNDWI and NDVI along with NIR and SWIR
        # bands to the Partial Surface Water Test 1 thresholds
    test4 = np.full(shape, False, dtype=bool)
    test4[(mndwi > pswt_1_mndwi) & 
            (swir1 < pswt_1_swir1) &
            (nir < pswt_1_nir) &
            (ndvi < pswt_1_ndvi)] = True

    # test 5 : compare the MNDWI along with Blue, NIR, SWIR1,
        # and SWIR2 bands to the Partial Surface Water Test 2
        # thresholds
    test5 = np.full(shape, False, dtype=bool)
    test5[(mndwi > pswt_2_mndwi) & 
            (blue < pswt_2_blue) &
            (swir1 < pswt_2_swir1) &
            (swir2 < pswt_2_swir2) &
            (nir < pswt_1_nir)] = True

    # stack the results together (each pixel has 5
        # corresponding bools)
    diag = np.stack((test1, test2, test3, test4, test5), axis=-1)
    return diag


def recode_to_interpreted(diag, fill_array):
    '''
    Recode results of five diagnostic tests to interpreted
    class DSWE band.
    INPUTS:
        diag : numpy array : (n by m by 5) boolean array;
            third dimension contains boolean results for the
            5 diagnostic tests for each pixel
        fill_array : numpy array : (n by m) boolean array;
            pixels are True where any input band has non-data
            (fill) values
    RETURNS:
        intr : numpy array : (n by m) integer array; elements
            correspond to DSWE interpreted classifications
            Pixel Value | Interpretation
                0       | Not Water
                1       | Water, High Confidence
                2       | Water, Moderate Confidence
                3       | Potential Wetland
                4       | Low Confidence Water or Wetland
                255     | Fill (no data)
    '''
    # get shape of input bands and initialize intr array
    shape = diag.shape[0:2]
    intr = np.empty(shape, dtype=int)
    
    # sum tests for each pixel; this is equivalent to total
        # number of tests passed (since True=1, False=0)
    sum_passed = np.sum(diag, axis=-1)

    # not water : 0 tests passed, or only 1 of the last four
        # tests passed
    sum_last_four = np.delete(diag, np.s_[0], -1)
    sum_last_four = np.sum(sum_last_four, axis=-1)
    intr[(sum_passed == 0) | 
            ((sum_passed == 1) & (sum_last_four == 1))] = 0

    # water, high confidence : 4 or 5 tests passed
    intr[(sum_passed == 4) | (sum_passed == 5)] = 1

    # water, moderate confidence : 3 tests passed
    intr[sum_passed == 3] = 2

    # potential wetland : both of the first two tests passed,
        # but no other tests passed (T, T, F, F, F)
    sum_first_two = np.delete(diag, np.s_[2:], -1)
    sum_first_two = np.sum(sum_first_two, axis=-1)
    intr[(sum_first_two == 2) & (sum_passed == 2)] = 3

    # low confidence water or wetland : 2 tests passed (but
        # not the first two) or only first test passed
    intr[((sum_passed == 2) & (sum_first_two != 2)) |
            ((sum_passed == 1) & (sum_last_four == 0))] = 4

    # take care of no data values
    intr[fill_array == True] = 255

    return intr


def main(input_dir, output_dir, include_tests, verbose):
    '''
    DSWE algorithm implemented to support either Harmonized
    Landsat Sentinel (HLS) or Landsat data as inputs.
    This version does not calculate the masked layers, and
    does not rely on a global DEM as input.
    INPUTS:
        input_dir : str : path to directory with input data,
            containing either HLS data in HDF4 format, or
            Landsat data in TAR format
        output_dir : str : output directory to save files
    OPTIONAL INPUTS:
        include_tests : bool : if true, save results of
            diagnostic tests to a file
        verbose : bool : if true, show print messages while
            code runs
    RETURNS:
        Interpreted (INTR) layer, and optionally diagnostic
        (DIAG) layer, saved as TIFF files to subdirectories
        within the output directory.
    '''
    # make a list of all files (HLS or Landsat) in main dir
    files = [f.path for f in os.scandir(input_dir)
                if os.path.isfile(f)]

    for i, filename in enumerate(files):
        if verbose:
            print(f'Processing file {i+1} of {len(files)}')

        # create output subdirectory (same name as input file)
        subdir_name = os.path.splitext(filename)[0] # remove extension
        subdir_name = os.path.split(subdir_name)[1] # remove path
        output_subdir = os.path.join(output_dir, subdir_name)
        os.makedirs(output_subdir, exist_ok=True)

        # check if file is HDF4 (or tar.gz)
        with open(filename, 'rb') as f:
            magic_string = f.read(4)
        if magic_string == b'\x0e\x03\x13\x01':
            # this is a HDF4 file
            all_bands = utils.hdf_bands(filename)
        elif tarfile.is_tarfile(filename):
            # this is a tar file
            all_bands = utils.tar_bands(filename, output_subdir)
        else:
            raise Exception('Unknown file format. Make sure input files are either HDF4 or TAR files.')

        if verbose:
            print('Assigning DSWE bands')
        # assign each DSWE band
        band_dict, geo_transform, projection = utils.assign_bands(all_bands)

        # get no-data (fill) value of bands and make fill
            # array for all bands
        fill, fill_array = utils.get_fill_array(band_dict)

        if verbose:
            print('Performing diagnostic tests')
        # calculate indexes for diagnostic tests
        mndwi, mbsrv, mbsrn, awesh, ndvi = diagnostic_setup(band_dict, fill)
        # perform diagnostic tests
        diag = diagnostic_tests(band_dict, mndwi, mbsrv,
                                    mbsrn, awesh, ndvi)

        if include_tests: # save diagnostic tests
            if verbose:
                print('Saving diagnostic layer')
            # convert bools to int (does not preserve leading zeros)
            diag_list = diag.astype(int).tolist()
            diag_int = [sum(d*10**i for i, d in enumerate(lst[::-1]))
                            for row in diag_list for lst in row]
            diag_save = np.reshape(np.array(diag_int), diag.shape[0:2])

            # account for non-data (fill) pixels
            diag_save[fill_array == True] = 255

            print(output_subdir)
            diag_filename = os.path.join(output_subdir, subdir_name + '_DIAG.tif')
            utils.save_output_tiff(diag_save, diag_filename,
                                        geo_transform, projection)

        if verbose:
            print('Recoding diagnostic layer to interpreted DSWE')

        # recode to interpreted DSWE
        intr = recode_to_interpreted(diag, fill_array)

        if verbose:
            print('Saving interpreted layer')
        # save interpreted layer
        intr_filename = os.path.join(output_subdir, subdir_name + '_INTR.tif')
        utils.save_output_tiff(intr, intr_filename,
                                    geo_transform, projection)

    if verbose:
        print('Done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description=('DSWE algorithm implemented to '
                'support either Harmonized Landsat Sentinel '
                '(HLS) or Landsat data as inputs. This version '
                'does not calculate the masked layers, and does '
                'not rely on a global DEM as input.'))
    parser.add_argument('input_dir',
            metavar='INPUT_DIRECTORY',
            type=str,
            help=('path to directory with input data, containing '
                    'either HLS data in HDF4 format, or Landsat '
                    'data in TAR format'))
    parser.add_argument('output_dir',
            metavar='OUTPUT_DIRECTORY',
            type=str,
            help='output directory to save files')
    # options from documentation
    parser.add_argument('--include_tests',
            dest='include_tests',
            action='store_true',
            help='if flagged, save results of diagnostic tests to a file')
    parser.add_argument('--verbose',
            dest='verbose',
            action='store_true',
            help='if flagged, show print messages while code runs')

    args = parser.parse_args()
    main(**vars(args))
