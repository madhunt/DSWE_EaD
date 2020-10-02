'''
DSWE algorithm implemented to support either Harmonized Landsat
Sentinel (HLS) or Landsat data as inputs.

The input directory for this code should have HLS data as HDF4
files, or Landsat data as TAR files. The output directory does
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

def clip_dem(dem_path, output_dir, geo_transform, shape):
    '''
    Clip user-provided DEM to extent of study area.
    '''
    dem_user = gdal.Open(dem_path)
    n_row, n_col = shape
    
    min_x = geo_transform[0]
    max_y = geo_transform[3]
    max_x = min_x + geo_transform[1] * n_col
    min_y = max_y + geo_transform[5] * n_row
    band_extent = [min_x, max_y, max_x, min_y]
    
    # clip DEM to specific scene extent
    dem_out = os.path.join(output_dir, 'DEM.tif')
    dem_clip = gdal.Translate(dem_out, dem_user, projWin=band_extent)
    if not dem_clip:
        raise Exception('The DEM provided does not cover the extent of the study area. See https://github.com/OSGeo/gdal/issues/2601 and https://gis.stackexchange.com/questions/233094/cropping-a-large-geotiff-in-qgis.')

    return dem_clip, dem_out


def percent_slope(dem_clip, output_subdir, use_zeven_thorne):
    '''
    Calculates percent slope using Horn's algorithm (default), 
    or Zevenbergen and Thorne's algorithm (optional).
    '''
    #TODO test this function with proper data
    slope_alg = 'Horn'
    if use_zeven_thorne:
        slope_alg = 'ZevenbergenThorne'
    
    slope_out = os.path.join(output_subdir, 'SLOPE.tif')
    slope = gdal.DEMProcessing(slope_out, dem_clip, 'slope',
            slopeFormat='percent', alg=slope_alg, format='GTiff')
    return slope


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


def diagnostic_tests(band_dict, fill):
    '''
    Perform five diagnostic tests for each pixel using indexes
    and user-defined threshold values from thresholds.json.
    INPUTS:
        band_dict : dict : dictionary with keys corresponding
            to the unscaled surface reflectance bands (blue,
            green, red, nir, swir1, and swir2) and values as
            paths to those bands or files
        fill : int : value of non-data (fill) pixels in the
            above bands
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
    
    mndwi, mbsrv, mbsrn, awesh, ndvi = diagnostic_setup(band_dict, fill)
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
    
    # test 5 : compare the MNDWI and Blue, NIR, SWIR1, and SWIR2
        # bands to Partial Surface Water Test 2 thresholds
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


def mask_interpreted(intr, slope, shade, band_dict):
    '''
    Filter the interpreted band results with the percent slope,
    hillshade, and pixel QA bands.
    INPUTS:
        intr : numpy array : (n by m) integer array; elements
            correspond to DSWE interpreted classifications
        slope : 
        shade : 
        band_dict : dict : dictionary with keys corresponding
            to the unscaled surface reflectance bands and QA band
            and values as paths to those bands or files
    RETURNS:
        inwm : numpy array : 
        mask : numpy array :  
    '''
    # initialize arrays
    inwm = intr.copy()
    shape = intr.shape
    mask = np.zeros(shape)
    
    # get pixel qa band
    pixel_qa = utils.file_to_array(band_dict['pixel_qa'])
    
    # get threshold values needed for calculations
    thresholds_dict = utils.get_thresholds()
    slope_high = thresholds_dict['PERCENT_SLOPE_HIGH']
    slope_moderate = thresholds_dict['PERCENT_SLOPE_MODERATE']
    slope_wetland = thresholds_dict['PERCENT_SLOPE_WETLAND']
    slope_low = thresholds_dict['PERCENT_SLOPE_LOW']
    shade_threshold = thresholds_dict['HILLSHADE']
    
    # test 1 : compare percent slope band to thresholds;
        # remove terrain too sloped to hold water
    check_high = (slope >= slope_high) & (intr == 1)
    check_mod = (slope >= slope_moderate) & (intr == 2)
    check_wetland = (slope >= slope_wetland) & (intr == 3)
    check_low = (slope >= slope_low) & (intr == 4)
        
    inwm[check_high | check_mod | check_wetland | check_low] = 0
    mask[check_high | check_mod | check_wetland | check_low] = 3
    
    # test 2 : compare hillshade band to threshold
    check_shade = (shade <= shade_threshold)
    inwm[check_shade] = 0
    mask[check_shade] = 4
    
    # test 3 : check if cloud (bit 1), cloud shadow (bit 3),
        # and/or snow (bit 4) are set
    check_cloud = (pixel_qa & (1 << 1)) != 0
    check_shadow = (pixel_qa & (1 << 3)) != 0
    check_snow = (pixel_qa & (1 << 4)) != 0
    
    inwm[check_cloud | check_shadow | check_snow] = 9
    mask[check_shadow] = 0
    mask[check_snow] = 1
    mask[check_cloud] = 2
    
    return inwm, mask


def hillshade(dem_clip, output_subdir, altitude, azimuth):
    '''
    Calculate hillshade using clipped DEM and solar geometry.
    INPUTS:
        dem_clip : 
        output_subdir : 
        altitude : 
        azimuth : 
    RETURNS:
        shade : 
    '''
    shade_out = os.path.join(output_subdir, 'SHADE.tif')
    shade = gdal.DEMProcessing(shade_out, dem_clip, 'hillshade',
            format='GTiff', azimuth=azimuth, altitude=altitude)
    return shade


def main(input_dir, output_dir, dem_path, include_tests, 
            include_ps, include_hs, use_zeven_thorne, verbose):
    '''
    DSWE algorithm implemented to support either Harmonized
    Landsat Sentinel (HLS) or Landsat data as inputs.
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
        log(f'Processing file {i+1} of {len(files)}')

        # create output subdirectory (same name as input file)
        subdir_name = os.path.splitext(filename)[0] # remove extension
        subdir_name = os.path.split(subdir_name)[1] # remove path
        output_subdir = os.path.join(output_dir, subdir_name)
        os.makedirs(output_subdir, exist_ok=True)

        # check if file is HDF4 or TAR
        with open(filename, 'rb') as f:
            magic_string = f.read(4)
        if magic_string == b'\x0e\x03\x13\x01':
            # this is a HDF4 file
            all_bands, metadata = utils.hdf_bands(filename)
            altitude, azimuth = utils.hdf_solar(metadata)
        elif tarfile.is_tarfile(filename):
            # this is a tar file
            unpack_subdir = os.path.join(input_dir, subdir_name)
            os.makedirs(unpack_subdir, exist_ok=True)
            all_bands = utils.tar_bands(filename, unpack_subdir)
        else:
            raise Exception('Unknown file format. Make sure input files are either HDF4 or TAR files.')

        log('Assigning DSWE bands')
        band_dict, geo_transform, projection = utils.assign_bands(all_bands)
        fill, fill_array = utils.get_fill_array(band_dict)

        log('Performing diagnostic tests')
        diag = diagnostic_tests(band_dict, fill)

        if include_tests:
            log('Saving diagnostic layer')
            # convert bools to int (does not preserve leading zeros)
            diag_list = diag.astype(int).tolist()
            diag_int = [sum(d*10**i for i, d in enumerate(lst[::-1]))
                            for row in diag_list for lst in row]
            diag_save = np.reshape(np.array(diag_int), diag.shape[0:2])

            # account for non-data (fill) pixels
            diag_save[fill_array == True] = 255

            diag_filename = os.path.join(output_subdir, subdir_name + '_DIAG.tif')
            utils.save_output_tiff(diag_save, diag_filename,
                                        geo_transform, projection)

        log('Recoding diagnostic layer to interpreted DSWE')
        intr = recode_to_interpreted(diag, fill_array)

        log('Saving interpreted layer')
        intr_filename = os.path.join(output_subdir, subdir_name + '_INTR.tif')
        utils.save_output_tiff(intr, intr_filename,
                                    geo_transform, projection)

        # only calculate masked layers if DEM is provided by user
        if dem_path:
            if i == 0:
                log('Clipping DEM to study area')
                shape = fill_array.shape
                dem_clip, dem_out = clip_dem(dem_path, output_dir, geo_transform, shape)
            else:
                dem_clip = gdal.Open(dem_out)

            log('Calculating percent slope')
            slope = percent_slope(dem_clip, output_subdir, use_zeven_thorne)
        if include_ps:
            log('Saving percent slope')
            slope_filename = os.path.join(output_subdir, subdir_name + '_SLOPE.tif')
            utils.save_output_tiff(slope, slope_filename, geo_transform, projection)

            log('Calculating hillshade')
            shade = hillshade(dem_clip, output_subdir, altitude, azimuth)
            if include_hs:
                log('Saving hillshade')
                shade_filename = os.path.join(output_subdir, subdir_name + '_SHADE.tif')
                utils.save_output_tiff(shade, shade_filename, geo_transform, projection)

            log('Calculating mask and masked interpreted layer')
            inwm, mask = mask_interpreted(intr, slope, shade, band_dict)

            log('Saving masked interpreted layer')
            inwm_filename = os.path.join(output_subdir, subdir_name + '_INWM.tif')
            utils.save_output_tiff(inwm, inwm_filename, geo_transform, projection)

            log('Saving mask')
            mask_filename = os.path.join(output_subdir, subdir_name + '_MASK.tif')
            utils.save_output_tiff(mask, mask_filename, geo_transform, projection)
    log('Done')

verbose = False
def log(print_str):
    global verbose
    if verbose:
        print(print_str)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                description=('DSWE algorithm implemented to '
                'support either Harmonized Landsat Sentinel '
                '(HLS) or Landsat data as inputs. If no DEM is '
                'provided by the user, masked DSWE layers will '
                'not be calculated.'))
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
    parser.add_argument('--dem',
            dest='dem_path',
            type=str,
            help=('path to DEM, which must be larger than and '
            'cover the study area; if not supplied, masked '
            'DSWE layers will not be calculated'))
    parser.add_argument('--include_tests',
            dest='include_tests',
            action='store_true',
            help=('if flagged, save results of diagnostic '
                    'tests to a file'))
    parser.add_argument('--include_ps',
            dest='include_ps',
            action='store_true',
            help='if flagged, save percent slope to a file')
    parser.add_argument('--include_hs',
            dest='include_hs',
            action='store_true',
            help=('if flagged, save hillshade (shaded relief) '
                    'to a file'))
    parser.add_argument('--use_zeven_thorne',
            dest='use_zeven_thorne',
            action='store_true',
            help=('if flagged, use Zevenbergen and Thorne\'s '
                    'slope algorithm; otherwise, defaults to '
                    'Horn\'s slope algorithm'))
    parser.add_argument('--verbose',
            dest='verbose', 
            action='store_true',
            help=('if flagged, show print messages while '
                    'code runs'))

    args = parser.parse_args()
    verbose = args.verbose
    main(**vars(args))
