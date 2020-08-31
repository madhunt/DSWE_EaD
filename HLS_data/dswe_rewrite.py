import argparse
import datetime
import gdal
import json
import numpy as np
import os
import read_hls

def percent_slope_horn(elevation_band):

    return percent_slope_band

def percent_slope_zeven_thorne(elevation_band):

    return percent_slope_band

def calculate_hillshade(elevation_band, sun_altitude, sun_azimuth):

    return hillshade


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


def get_thresholds():
    '''
    Open the thresholds.json file, which should be in the same
    directory as this python file.
    Returns the threshold values as a dictionary.
    '''
    # get path of this file
    script_path = os.path.realpath(__file__)
    thresholds_path = os.path.join(script_path, 'thresholds.json')

    # make sure the thresholds.json file exists
    if os.path.isfile(thresholds_path):
        with open(thresholds_path, 'r') as f:
            thresholds_dict = json.load(f)
        return thresholds_dict

    else:
        raise Exception('Make sure thresholds.json is in the same '
                            'directory as this python file')


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
    thresholds_dict = get_thresholds()
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



def save_output_tiff(data, filename, geo_transform, projection):
    '''
    Save a numpy array of data as a GeoTiff file.
    INPUTS:
        data : numpy array : data to save
        filename : str : full path and filename for output file
        geo_transform : tuple : raster coordinates related to
            georeferencing coordinates by affine transform
        projection : list : GDAL projection metadata
    RETURNS:
        output file saved as filename
    '''
    shape = array.shape
    driver = gdal.GetDriverByName('GTiff')
    outdata = driver.Create(filename, shape[1], shape[0], 1, gdal.GDT_Byte)
    outdata.SetGeoTransform(geo_transform)
    outdata.SetProjection(projection)
    outdata.GetRasterBand(1).SetNoDataValue(255)
    outdata.GetRasterBand(1).WriteArray(data)
    outdata.FlushCache()


def file_to_array(filename):
    '''
    Open file as gdal dataset, get geo transform and
    projection, convert to numpy array.
    '''
    data = gdal.Open(filename)
    geo_transform = data.GetGeoTransform()
    projection = data.GetProjection()
    array = data.GetRasterBand(1).ReadAsArray()
    return array, geo_transform, projection


def assign_bands(files):
    for filename in files:
        # assign hillshade and slope
        #XXX is there any other file from preprocessing that needs to be called in?
        if 'hillshade' in filename:
            hillshade = gdal.Open(filename)

        # check if file is HDF4
        with open(filename, 'rb') as f:
            magic_string = f.read(4)
        if magic_string == b'\x0e\x03\x13\x01':
            # this is a HDF4 file
            hdf_data = gdal.Open(os.path.abspath(filename))
            hdf_metadata = hdf_data.GetMetadata_Dict()

            # get bands (subdatasets) from HDF data
            all_bands = hdf_data.GetSubDatasets()

            # assign each DSWE band
            for band in all_bands:
                band_filename = band[0]
                if 'band02' or 'B02' in filename:
                    blue, blue_geo, blue_proj = file_to_array(band_filename)
                if 'band03' or 'B03' in filename:
                    green, green_geo, green_proj = file_to_array(band_filename)
                if 'band04' or 'B04' in filename:
                    red, red_geo, red_proj = file_to_array(band_filename)
                if 'band05' or 'B8A' in filename:
                    nir, nir_geo, nir_proj = file_to_array(band_filename)
                if 'band06' or 'B11' in filename:
                    swir1, swir1_geo, swir1_proj = file_to_array(band_filename)
                if 'band07' or 'B12' in filename:
                    swir2, swir2_geo, swir2_proj = file_to_array(band_filename)
                if 'Grid:QA' in band_filename:
                    pixel_qa, qa_geo, qa_proj = file_to_array(band_filename)

        else:
            # assign landsat bands
            #XXX this works for landsat 8, but what about other landsat?
            if 'B2' in filename:
                blue, blue_geo, blue_proj = file_to_array(filename)
            if 'B3' in filename:
                green, green_geo, green_proj = file_to_array(filename)
            if 'B4' in filename:
                red, red_geo, red_proj = file_to_array(filename)
            if 'B5' in filename:
                nir, nir_geo, nir_proj = file_to_array(filename)
            if 'B6' in filename:
                swir1, swir1_geo, swir1_proj = file_to_array(filename)
            if 'B7' in filename:
                swir2, swir2_geo, swir2_proj = file_to_array(filename)
            if 'BQA' in filename:
                pixel_qa, qa_geo, qa_proj = file_to_array(filename)


            # assert all bands have the same geo transform, 
                # projection, and shape
            assert (blue_geo == green_geo == red_geo == nir_geo ==
                        swir1_geo == swir2_geo == qa_geo)
            assert (blue_proj == green_proj == red_proj == nir_proj ==
                        swir1_proj == swir2_proj == qa_proj)
            assert (blue.shape == green.shape == red.shape == nir.shape ==
                        swir1.shape == swir2.shape == qa.shape)

            # assign geo transform, projection, and shape
            geo_transform = blue_geo
            projection = blue_proj

    return geo_transform, projection, blue, green, red, nir, swir1, swir2, pixel_qa


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
    thresholds_dict = get_thresholds()
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



def main(input_dir, output_dir, **kwargs):
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
    
    # find percent slope file (should be in top dir)
    files = [f.path for f in os.scandir(input_dir) if os.path.isfile(f)]
    percent_slope_str = ['perslp', 'percent_slope', 'per_slope', 'per_slp']
    percent_slope = None
    for filename in files:
        if any(substr in filename for substr in percent_slope_str):
            percent_slope = filename
    if percent_slope == None:
        raise Exception('No percent slope file found in top directory.')
    
    # make a list of subdirectories (separate HLS or Landsat scenes after pre-processing)
    subdirs = [f.path for f in os.scandir(input_dir) if f.is_dir()]

    # for each subdir (separate HLS/landsat scene)
    for input_subdir in subdirs:
        # make an output subdir
        output_subdir = os.path.join(output_dir, input_subdir)
        os.makedirs(output_subdir, exist_ok=True)

        # get bands
        files = [f.path for f in os.scandir(input_subdir) if os.path.isfile(f)]
        geo_transform, projection, blue, green, red, nir, swir1, swir2, pixel_qa = assign_bands(files)


        #TODO MAKE SURE 255 PIXELS ARE ACCOUNTED FOR IN THE FOLLOWING FUNCS
        # calculate indexes for diagnostic tests
        mndwi, mbsrv, mbsrn, awesh, ndvi = diagnostic_setup(blue, 
                                        green, red, nir, swir1, swir2)
        diag = diagnostic_tests(mndwi, mbsrv, mbsrn, awesh, ndvi)
        
        if include_tests:
            # save diag as TIF
            diag_filename = os.path.join(output_subdir, 'DIAG.tif') #XXX better filename -- landsat_id_info_DIAG.TIF
            save_output_tiff(diag, diag_filename, geo_transform, projection)

        # recode to interpreted DSWE
        intr = recode_to_interpreted(diag, shape)
        # save intr as TIF
        intr_filename = os.path.join(output_subdir, 'INTR.tif')
        save_output_tiff(intr, intr_filename, geo_transform, projection)

        # filter interpreted band results
        inwm, mask = mask_interpreted(intr, percent_slope, hillshade, pixel_qa)
        # save intr_filtered as TIF
        inwm_filename = os.path.join(output_subdir, 'INWM.tif')
        save_output_tiff(inwm, inwm_filename, geo_transform, projection)




    return









def old_code():
    for folder in paths:
        out_name = 'DSWE_V2_P1'
        
        # Terrain Correction, here we are simply recoding slopes >=x degrees to PS (specified above), which will be reclassified as non-water.

        perslp = gdal.Open(Perslp)
        #Get extent and projection
        perslpgeo = perslp.GetGeoTransform()
        perslpproj = perslp.GetProjection()
        # Calculate percent slope
        #perslp= perslp.GetRasterBand(1).ReadAsArray()
        os.chdir(working_dir)
        CF = gdal.Open(CF)
        #Get extent of CF mask (and our LS image by proxy)
        geoTransform = CF.GetGeoTransform()
        minx = geoTransform[0]
        maxy = geoTransform[3]
        maxx = minx + geoTransform[1] * CF.RasterXSize
        miny = maxy + geoTransform[5] * CF.RasterYSize
        #Clip our slope and hillshade mask to the image (have to do this for each image due to the variable extents of each image)
        GeoClip= [minx, maxy, maxx, miny]
        hillshade= gdal.Open(Hillshade)
        perslp_clip=gdal.Translate('perslp_clip.tif', perslp, projWin = GeoClip)
        hillshade_clip=gdal.Translate('hillshade_clip.tif', hillshade, projWin = GeoClip)
        hillshade= hillshade_clip.GetRasterBand(1).ReadAsArray()
        hillshade[hillshade <= HS] = 0
        hillshade[hillshade > HS] = 1
        
        #Read in the slope and hillshade masks and convert to an array
        workingoutput_dir=output_dir2 + "\\" + directory
        if not os.path.exists(workingoutput_dir):
            os.makedirs(workingoutput_dir)
            
        #calculate our unmasked diagnostic map
        CF= CF.GetRasterBand(1).ReadAsArray()
        diagoutput=output_dir2 +  "\\" + directory + "\\" + out_name + "_diag" + "_%s.tif"%"_".join(raster.split('_'))[0:length]
        diagmap[np.where((CF == 255))] = -9999
        diagmap_out = driver.Create( diagoutput, shape[1], shape[0], 1, gdal.GDT_Int16)
        diagmap_out.SetGeoTransform( geo )
        diagmap_out.SetProjection( proj )
        diagmap_out.GetRasterBand(1).WriteArray(diagmap)
        diagmap_out.GetRasterBand(1).SetNoDataValue(-9999)
            
        
        # Output unmasked interpreted map
        interpoutput=output_dir2 +  "\\" + directory + "\\" + out_name + "_interp" + "_%s.tif"%"_".join(raster.split('_'))[0:length]
        interpmap=diagmap.copy()
        interpmap[np.where((diagmap == 0) | (diagmap == 1) | (diagmap == 10) | (diagmap == 100) | (diagmap == 1000))] = 0
        interpmap[np.where((diagmap == 1111) | (diagmap == 10111) | (diagmap == 11011) | (diagmap == 11101) | (diagmap == 11110) | (diagmap == 11111)) ] = 1
        interpmap[np.where((diagmap == 111) | (diagmap == 1011) | (diagmap == 1101) | (diagmap == 1110) | (diagmap == 10011) | (diagmap == 10101) | (diagmap == 10110) | (diagmap == 11001) | (diagmap == 11010) | (diagmap == 11100)) ] = 2
        interpmap[np.where((diagmap == 11000)) ] = 3
        interpmap[np.where((diagmap == 11) | (diagmap == 101) | (diagmap == 110) | (diagmap == 1001) | (diagmap == 1010) | (diagmap == 1100) | (diagmap == 10000) | (diagmap == 10001) | (diagmap == 10010) | (diagmap == 10100)) ] = 4
        interpmap[np.where((diagmap == -9999)) ] = 255
        interpmap_out = driver.Create( interpoutput, shape[1], shape[0], 1, gdal.GDT_Byte)
        interpmap_out.SetGeoTransform( geo )
        interpmap_out.SetProjection( proj )
        interpmap_out.GetRasterBand(1).WriteArray(interpmap)
        interpmap_out.GetRasterBand(1).SetNoDataValue(255)


        # Mask interpreted map using the slope file
        perslp= perslp_clip.GetRasterBand(1).ReadAsArray()
        interpmap_copy=interpmap.copy()
        interpmap[np.where((perslp >= 30) & (interpmap == 2))] = 0
        interpmap[np.where((perslp >= 20) & (interpmap == 3))] = 0
        interpmap[np.where((perslp >= 10) & (interpmap == 4))] = 0
        interpmap[np.where((perslp >= 30) & (interpmap == 1))] = 0
        interpmap_masked= interpmap * hillshade           


        
        #Cloud and snow masking and outputing masked interpreted layer
        interpmaskoutput=output_dir2 +  "\\" + directory + "\\" + out_name + "_interp_masked" + "_%s.tif"%"_".join(raster.split('_'))[0:length]
        interpmap_masked=interpmap_masked.copy()
        interpmap_masked[np.where((CF == 255))] = 255
        interpmap_masked[np.where((CF >= 2) & (CF < 255))] = 9
        interpmap_masked_out = driver.Create( interpmaskoutput, shape[1], shape[0], 1, gdal.GDT_Byte)
        interpmap_masked_out.SetGeoTransform( geo )
        interpmap_masked_out.SetProjection( proj )
        interpmap_masked_out.GetRasterBand(1).WriteArray(interpmap_masked)
        interpmap_masked_out.GetRasterBand(1).SetNoDataValue(255)
        del interpmap_masked_out
        del diagmap
        del interpmap



        #Create a full mask layer
        CF[np.where((CF == 1)) ] = 0
        perslp[np.where((perslp < 10) & (interpmap_copy == 4)) ] = 0
        perslp[np.where((perslp < 20) & (interpmap_copy == 3)) ] = 0
        perslp[np.where((perslp < 30) & (interpmap_copy == 2)) ] = 0
        perslp[np.where((perslp < 30) & (interpmap_copy == 1)) ] = 0
        perslp[np.where((perslp >= 10) & (interpmap_copy == 4)) ] = 10
        perslp[np.where((perslp >= 20) & (interpmap_copy == 3)) ] = 10
        perslp[np.where((perslp >= 30) & (interpmap_copy == 2)) ] = 10
        perslp[np.where((perslp >= 30) & (interpmap_copy == 1)) ] = 10
        perslp[np.where((interpmap_copy == 0)) ] = 0       
        hillshade[np.where((hillshade == 0)) ] = 20
        hillshade[np.where((hillshade == 1)) ] = 0
        MaskLayer=CF + perslp + hillshade
        MaskLayerOut=output_dir2 +  "\\" + directory + "\\" + out_name + "_MaskLayer" + "_%s.tif"%"_".join(raster.split('_'))[0:length]
        MaskLayer[np.where((CF == 255))] = 255
        MaskLayer_Output = driver.Create(MaskLayerOut, shape[1], shape[0], 1, gdal.GDT_Byte)
        MaskLayer_Output.SetGeoTransform( geo )
        MaskLayer_Output.SetProjection( proj )
        MaskLayer_Output.GetRasterBand(1).WriteArray(MaskLayer)
        MaskLayer_Output.GetRasterBand(1).SetNoDataValue(255)
        del hillshade_clip, hillshade, MaskLayer, CF, MaskLayerOut, MaskLayer_Output, diagoutput
        del Metadata, diagmap_out, interpmap_masked, interpmap_out, interpmaskoutput, interpoutput, perslp, perslp_clip           



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

    parser.add_argument('--quiet',
            dest='quiet',
            action='store_true',
            help='if flagged, no print messages are shown')

    args = parser.parse_args()
    main(**vars(args))
