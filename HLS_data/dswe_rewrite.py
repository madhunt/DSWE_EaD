import argparse
import gdal
import numpy as np
import os
import utils


def diagnostic_setup(blue, green, red, nir, swir1, swir2):
    '''
    Calculate indexes based on non-fill (valid) pixels of
    input bands for diagnostic tests.
    INPUTS:
        Unscaled Surface Reflectance bands (blue, green,
        red, NIR, SWIR1, and SWIR2 wavelengths) as numpy
        arrays.
    RETURNS:
        Five indexes for non-fill pixel values as numpy
        arrays.
    '''
    # Modified Normalized Difference Wetness Index
    mndwi = (green - swir1) / (green + swir1)
    
    # Multi-band Spectral Relationship Visible
    mbsrv = green + red
    
    # Multi-band Spectral Relationship Near-Infrared
    mbsrn = nir + swir1
    
    # Automated Water Extent Shadow
    awesh = blue + (2.5 * green) - (1.5 * mbsrn) - (0.25 * swir2)
    
    # Normalized Difference Vegetation Index
    ndvi = (nir - red) / (nir + red)

    return mndwi, mbsrv, mbsrn, awesh, ndvi


def diagnostic_tests(mndwi, mbsrv, mbsrn, awesh, ndvi):
    '''
    Perform five diagnostic tests on indexes calculated from the
    input bands.
    INPUTS:
        Indexes calculated in diagnostic_setup() from the input bands,
        as numpy arrays.
    RETURNS:
        diag : 3D numpy array : array with boolean array of test
            results for each pixel; shape is shape of input bands
            by 5 (n, m, 5)
    '''
    # get threshold values to perform tests
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

    # we've already asserted that shapes are the same, so this is safe
    shape = mndwi.shape

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

    # test 4 : compare MNDWI and NDVI along with NIR and SWIR bands
        # to the Partial Surface Water Test 1 thresholds
    test4 = np.full(shape, False, dtype=bool)
    test4[(mndwi > pswt_1_mndwi) & 
            (swir1 < pswt_1_swir1) &
            (nir < pswt_1_nir) &
            (ndvi < pswt_1_ndvi)] = True

    # test 5 : compare the MNDWI along with Blue, NIR, SWIR1, and
        # SWIR2 bands to the Partial Surface Water Test 2 thresholds
    test5 = np.full(shape, False, dtype=bool)
    test4[(mndwi > pswt_2_mndwi) & 
            (blue < pswt_2_blue) &
            (swir1 < pswt_2_swir1) &
            (swir2 < pswt_2_swir2) &
            (nir < pswt_1_nir)] = True

    # stack the results together (each pixel has 5 corresponding bools)
    diag = np.stack((test1, test2, test3, test4, test5), axis=-1)
    return diag


def recode_to_interpreted(diag):
    '''
    Recode results of five diagnostic tests to interpreted class
    DSWE band.
    INPUTS:
        diag : 3D numpy array : n by m array with results of
            diagnostic tests as 5-element list in 3rd dimension;
            shape (n, m, 5)
    RETURNS:
        intr : 2D numpy array : n by m array with integer elements of
            DSWE interpreted classifications
            Pixel Value | Interpretation
                0       | Not Water
                1       | Water, High Confidence
                2       | Water, Moderate Confidence
                3       | Potential Wetland
                4       | Low Confidence Water or Wetland
                255     | Fill (no data)
    '''
    # get shape of input bands, or first two elements of diag shape
    shape = diag.shape[0:2]
    intr = np.empty(shape, dtype=int)
    
    # get the sum of the tests passed for each pixel
        # True = 1, False = 0, so this is equivalent to the number 
        # of tests passed
    sum_passed = np.sum(diag, axis=-1)

    # not water : 0 or 1 total tests passed
    intr[(sum_passed == 0) | (sum_passed == 1)] = 0

    # water, high confidence : 4 or 5 total tests passed
    intr[(sum_passed == 4) | (sum_passed == 5)] = 1

    # water, moderate confidence : 3 total tests passed
    intr[sum_passed == 3] = 2

    # potential wetland : only first two tests passed
    # delete all but first 2 tests for each pixel and sum them
    sum_first_two = np.delete(diag, np.s_[2:], -1)
    sum_first_two = np.sum(sum_1_2, axis=-1)
    intr[(sum_first_two == 2) & (sum_passed == 2)] = 3

    # low confidence water or wetland : 2 total tests passed 
        # (but not both of the first two tests)
    intr[(sum_passed == 2) & (sum_first_two != 2)] = 4

    return intr


def mask_interpreted(intr, percent_slope, hillshade, pixel_qa):
    '''
    Filter the interpreted band results with the percent slope,
    hillshade, and pixel QA bands.
    INPUTS:
        intr : 
        percent_slope : 
        hillshade : 
        pixel_qa :
    RETURNS:
        inwm : numpy array : 
        mask : numpy array :  
    '''
    # initialize arrays
    inwm = intr.copy()
    shape = intr.shape
    mask = np.zeros(shape)

    # get threshold values needed for calculations
    thresholds_dict = utils.get_thresholds()
    percent_slope_high = thresholds_dict['PERCENT_SLOPE_HIGH']
    percent_slope_moderate = thresholds_dict['PERCENT_SLOPE_MODERATE']
    percent_slope_wetland = thresholds_dict['PERCENT_SLOPE_WETLAND']
    percent_slope_low = thresholds_dict['PERCENT_SLOPE_LOW']
    hillshade_threshold = thresholds_dict['HILLSHADE']

    # test 1 : compare percent slope band to percent slope thresholds;
        # remove locations where terrain is too sloped to hold water
    check_high = (percent_slope >= percent_slope_high) & (intr == 1)
    check_mod = (percent_slope >= percent_slope_moderate) & (intr == 2)
    check_wetland = (percent_slope >= percent_slope_wetland) & (intr == 3)
    check_low = (percent_slope >= percent_slope_low) & (intr == 4)
    
    inwm[check_high | check_mod | check_wetland | check_low] = 0

    mask[check_high | check_mod | check_wetland | check_low] = 3

    # test 2 : compare hillshade band to hillshade threshold
    check_hillshade = (hillshade <= hillshade_threshold)
    inwm[check_hillshade] = 0
    mask[check_hillshade] = 4

    # test 3 : compare pixel QA band to cloud, snow, and cloud shadow values
        # if pixel QA cloud (bit 1), cloud shadow (bit 3), and/or 
        # snow (bit 4) is set
    check_cloud = (pixel_qa & (1 << 1)) != 0
    check_shadow = (pixel_qa & (1 << 3)) != 0
    check_snow = (pixel_qa & (1 << 4)) != 0

    inwm[check_cloud | check_shadow | check_snow] = 9
    mask[check_shadow] = 0
    mask[check_snow] = 1
    mask[check_cloud] = 2

    return inwm, mask

def clip_global_dem(output_subdir, global_dem, geo_transform, shape):
    # calculate percent slope
    n_row, n_col = shape

    #XXX old code had n_row + 1
    min_x = geo_transform[0]
    max_y = geo_transform[3]
    max_x = min_x + geo_transform[1] * n_col
    min_y = max_y + geo_transform[5] * n_row
    band_extent = [min_x, max_y, max_x, min_y]

    # clip global DEM to specific scene extent
    dem_out = os.path.join(output_subdir, 'DEM.tif')
    dem_clip = gdal.Translate(dem_out, global_dem, projWin=band_extent)
    return dem_clip


def percent_slope(output_subdir, dem_clip, use_zeven_thorne):
    slope_alg = 'Horn'
    if use_zeven_thorne:
        slope_alg = 'ZevenbergenThorne'

    # calculate percent slope
    slope_out = os.path.join(output_subdir, 'SLOPE.tif')
    slope = gdal.DEMProcessing(slope_out, dem_clip, 'slope',
            slopeFormat='percent', alg=slope_alg, format='GTiff')
    return slope


def hillshade(output_subdir, dem_clip):
    # calculate hillshade
    shade_out = os.path.join(output_subdir, 'SHADE.tif')


    shade = gdal.DEMProcessing(shade_out, dem_clip, 'hillshade',
            format='GTiff', azimuth=azimuth, altitude=altitude)

    return shade


def main(input_dir, output_dir,
            include_tests, include_ps, include_hs,
            use_zeven_thorne, use_toa, verbose):
    '''
    INPUTS:
        input_dir : str : path to directory with input data
        output_dir : str : output directory for interpreted band,
            mask band, interpreted band with masking, and optional
            diagnostic band, percent slope, and hillshade
    OPTIONAL INPUTS:
        include_tests : bool : if flagged, save results of diagnostic 
            tests to a file
        include_ps : bool : if flagged, save percent slope to a file
        include_hs : bool : if flagged, save hillshade (shaded relief)
            to a file
        use_zeven_thorne : bool : if flagged, use Zevenbergen and
            Thorne's slope algorithm; otherwise, defaults to Horn's
            slope algorithm
        use_toa : bool : if flagged, Top of Atmosphere (TOA)
            reflectance is used; otherwise, defaults to Surface
            Reflectance
        quiet : bool : if flagged, no print messages are shown
        
    RETURNS:
    '''
    
    # make a list of all files (HLS or Landsat) in main dir
    files = [f.path for f in os.scandir(input_dir) if os.path.isfile(f)]
    for filename in files:
        # make an output dir
        subdir_name = os.path.splitext(filename)[0] # get file path with out extension
        subdir_name = os.path.split(subdir_name)[1] # get just filename from path
        output_subdir = os.path.join(output_dir, subdir_name)
        os.makedirs(output_subdir, exist_ok=True)

        # check if file is HDF4 (or tar.gz)
        if verbose:
            print('Getting solar data')
        with open(filename, 'rb') as f:
            magic_string = f.read(4)
        if magic_string == b'\x0e\x03\x13\x01':
            # this is a HDF4 file
            all_bands, azimuth, altitude = utils.hdf_bands_solar_geo(filename)
        else:
            # this is a tar.gz file
            all_bands, azimuth, altitude = utils.tar_bands_solar_geo(filename, output_subdir)

        # assign each DSWE band
        if verbose:
            print('Assigning DSWE bands')
        geo_transform, projection, blue, green, red, nir, swir1, swir2, pixel_qa = utils.assign_bands(all_bands)

        shape = blue.shape

        
        breakpoint()
        if verbose:
            print('Clipping global DEM')

        dem_clip = clip_global_dem(output_subdir, global_dem, geo_transform, shape)
        slope = percent_slope(output_subdir, dem_clip, use_zeven_thorne)
        shade = hillshade(output_subdir, dem_clip)

        if include_ps: # save percent slope
            slope_filename = os.path.join(output_subdir, 'SLOPE.tif')
            utils.save_output_tiff(slope, slope_filename, geo_transform, projection)
        if include_hs: # save hillshade
            shade_filename = os.path.join(output_subdir, 'SHADE.tif')
            utils.save_output_tiff(shade, shade_filename, geo_transform, projection)



        #TODO MAKE SURE 255 PIXELS ARE ACCOUNTED FOR IN THE FOLLOWING FUNCS
        # calculate indexes for diagnostic tests
        mndwi, mbsrv, mbsrn, awesh, ndvi = diagnostic_setup(blue, green, red,
                                                            nir, swir1, swir2)
        diag = diagnostic_tests(mndwi, mbsrv, mbsrn, awesh, ndvi)
        
        if include_tests: # save diagnostic tests
            diag_filename = os.path.join(output_subdir, 'DIAG.tif')
            utils.save_output_tiff(diag, diag_filename, geo_transform, projection)

        # recode to interpreted DSWE
        intr = recode_to_interpreted(diag, shape)
        # save interpreted layer
        intr_filename = os.path.join(output_subdir, 'INTR.tif')
        utils.save_output_tiff(intr, intr_filename, geo_transform, projection)

        # filter interpreted band results
        inwm, mask = mask_interpreted(intr, slope, shade, pixel_qa)
        # save interpreted layer with mask
        inwm_filename = os.path.join(output_subdir, 'INWM.tif')
        utils.save_output_tiff(inwm, inwm_filename, geo_transform, projection)
        # save mask layer
        mask_filename = os.path.join(output_subdir, 'MASK.tif')
        utils.save_output_tiff(mask, mask_filename, geo_transform, projection)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=(''))

    #XXX add required arguments here
    parser.add_argument('input_dir',
            metavar='INPUT_DIRECTORY',
            type=str,
            help='path to directory with input data')
    parser.add_argument('output_dir',
            metavar='OUTPUT_DIRECTORY',
            type=str,
            help='output directory for interpreted band, mask band, interpreted band with masking, and optional diagnostic band, percent slope, and hillshade')
    

    # options from documentation
    parser.add_argument('--include_tests',
            dest='include_tests',
            action='store_true',
            help='if flagged, save results of diagnostic tests to a file')
    parser.add_argument('--include_ps',
            dest='include_ps',
            action='store_true',
            help='if flagged, save percent slope to a file')
    parser.add_argument('--include_hs',
            dest='include_hs',
            action='store_true',
            help='if flagged, save hillshade (shaded relief) to a file')
    parser.add_argument('--use_zeven_thorne',
            dest='use_zeven_thorne',
            action='store_true',
            help=('if flagged, use Zevenbergen and Thorne\'s slope '
            'algorithm; otherwise, defaults to Horn\'s slope algorithm'))
    parser.add_argument('--use_toa',
            dest='use_toa',
            action='store_true',
            help=('if flagged, Top of Atmosphere (TOA) reflectance is '
            'used; otherwise, defaults to Surface Reflectance'))

    parser.add_argument('--verbose',
            dest='verbose',
            action='store_true',
            help='if flagged, print messages are shown')

    args = parser.parse_args()
    main(**vars(args))
