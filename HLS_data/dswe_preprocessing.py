'''
Use Landsat or HLS (Harmonized Landsat Sentinel-2) data to create DEM,
slope, and hillshade files to input into DSWE code.
''' 
import argparse
import gdal
import os
import re
import read_hls
import tarfile

def main(input_file, output_dir, us_dem, slope_in, targz):
    '''
    Use Landsat or HLS (Harmonized Landsat Sentinel-2) data to create
    DEM, slope, and hillshade files to input into DSWE code.
    INPUTS:
        input_file : str : input file 
            (supports Landsat tar.gz or HLS hdf4)
        output_dir : str : output directory for DEM, slope, 
            and hillshade TIFFs
        us_dem : str : path to US national DEM file
        slope_in : str : path to slope TIF file
        targz : bool : if True, input is a Landsat tar.gz file;
            if False, input is HLS data in HDF4 format
    RETURNS:
        DEM, slope, and hillshade files saves as TIFFs in output_dir
    '''
    # create output_dir if doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    if targz: # input is landsat tar.gz file
        # get list of bands
        print('Extracting Landsat tar file')
        sub_dir = untar(input_file, output_dir)
        band_files = []
        for dirpath, _, filenames in os.walk(sub_dir):
            for filename in filenames:
                if '.tif' or '.TIF' in filename:
                    filepath = os.path.join(dirpath, filename)
                    band_files.append(filepath)
                if 'MTL' in filename:
                    metadata_file = os.path.join(dirpath, filename)

        # get solar geometry
        print('Getting solar geometry')
        azimuth, altitude = get_tar_solar_geometry(metadata_file)

    else: # input is HLS file
        # get list of bands
        dswe_bands = read_hls.main(input_file, tiff_output=False,
                                        output_dir=None)
        band_files = list(dswe_bands.values())

        # get solar geometry
        print('Getting solar geometry')
        band_filename = band_files[0]
        match = re.search('\"(.+?)\"', band_filename)
        hls_filename = match.group(1)
        azimuth, altitude = get_hls_solar_geometry(hls_filename)


    breakpoint() #TODO test code beyone this point

    # create DEM and slope files
    print('Creating DEM and slope files')
    dem_out, _ = create_dem_and_slope(sub_dir, band_files,
                                        us_dem, slope_in)
    # create hillshade file
    print('Creating hillshade file')
    create_hillshade(sub_dir, dem_out, azimuth, altitude)


def untar(input_file, output_dir):
    '''
    Extract tar.gz file of Landsat bands.
    INPUTS:
        input_file : str : path to tar.gz file
        output_dir : str : path to directory to extract files in
    RETURNS:
        tar.gz files extracted in output_dir
    '''
    # make sure input file exists and is a tar file
    if os.path.isfile(input_file) and tarfile.is_tarfile(input_file):
        # create directory for extracted files
        sub_dir = os.path.splitext(input_file)[0] + '_input'
        tar_file = tarfile.open(input_file, mode='r:gz')

        # extract data to subdirectory
        tar_file.extractall(sub_dir)
        
        # close tar file
        tar_file.close()
        return sub_dir

    # otherwise..
    elif not os.path.isfile(input_file):
        raise Exception(f'Input file does not exist: {input_file}')
    elif not tarfile.is_tarfile(input_file):
        raise Exception(f'Input file is not a tar file: {input_file}')


def get_tar_solar_geometry(metadata_file):
    '''
    Get solar geometry from Landsat metadata file.
    Assumes naming convention that metadata file is a txt document
    with 'MTN' in the name.
    '''
    azimuth_search = 'SUN_AZIMUTH'
    altitude_search = 'SUN_ELEVATION'

    # search through all lines of metadata file
    with open(metadata_file, 'r') as metadata:
        for line in metadata.readlines():
            if re.search(azimuth_search, line, re.I):
                # get rid of whitespace
                azimuth_line = line.replace(' ', '')
                # get the value on right side of =
                azimuth = azimuth_line.split('=')[1]
                azimuth = float(azimuth)

            if re.search(altitude_search, line, re.I):
                # get rid of whitespace
                altitude_line = line.replace(' ', '')
                # get the value on right side of =
                altitude = altitude_line.split('=')[1]
                altitude = float(altitude)
        return azimuth, altitude


def get_hls_solar_geometry(hls_filename):
    '''
    Get solar geometry from metadata of HLS HDF4 file.
    '''
    hls_data = gdal.Open(hls_filename)
    hls_metadata = hls_data.GetMetadata()
    
    azimuth_search = 'MEAN_SUN_AZIMUTH_ANGLE'
    zenith_search = 'MEAN_SUN_ZENITH_ANGLE'

    # search metadata
    azimuth = [val for key, val in hls_metadata.items() if azimuth_search in key][0]
    zenith = [val for key, val in hls_metadata.items() if zenith_search in key][0]

    # convert strings to floats
    azimuth = float(azimuth)
    zenith = float(zenith)
    altitude = 90.0 - zenith
    return azimuth, altitude


def create_dem_and_slope(output_dir, band_files, us_dem, slope_in):
    '''
    Create DEM and percent slope as output TIFF files.
    INPUTS:
        output_dir : str : path to save DEM and slope TIFF files
        band_files : list of str : list of paths to each band in the
            Landsat or HLS data
        us_dem : str : path to US national DEM file
        slope_in : str : path to slope TIF file
    RETURNS:
        DEM and slope files saves as TIFFs in output_dir
    '''
    # create output filenames
    dem_out = os.path.join(output_dir, 'DEM.tif')
    slope_out = os.path.join(output_dir, 'perslp.tif')
        #TODO change this filenaming convention to percent_slope

    # get min/max coordinates from input bands
    geo_transform, n_col, n_row = get_band_properties(band_files)
    min_x = geo_transform[0]
    max_y = geo_transform[3]
    max_x = min_x + geo_transform[1] * n_col
    min_y = max_y + geo_transform[5] * n_row

    # open total US DEM and slope
    dem_in = gdal.Open(us_dem)
    slope_in = gdal.Open(slope_in)

    # clip DEM and slope to coordinates from input
    geo_clip = [min_x, max_y, max_x, min_y]
    dem_clip = gdal.Translate(dem_out, dem_in, projWin=geo_clip)
    slope_clip = gdal.Translate(slope_out, slope_in, projWin=geo_clip)

    #XXX old leftover code:
    #percent_slope = gdal.DEMProcessing(slope_out, dem_clip, 'slope',
                                #slopeFormat='percent', format='GTiff')
    return dem_out, slope_out


def get_band_properties(band_files):
    '''
    Get properties of all bands in the Landsat or HLS data.
    INPUTS:
        band_files : list of str : list of paths to each band in 
            the Landsat or HLS data
    RETURNS:
        geo_transform : tuple : coordinates of top left corner of all bands
        n_col : int : number of columns (pixels in x direction)
        n_row : int : number of rows (pixels in y direction)
    '''
    for i, filename in enumerate(band_files):
        band = gdal.Open(filename)
        geo_transform = band.GetGeoTransform()
        n_col = band.RasterXSize
        n_row = band.RasterYSize + 1 #XXX why +1 ??

        if i != 0:
            # assert these properties are the same for all bands
            assert geo_transform == geo_transform_old
            assert n_col == n_col_old
            assert n_row == n_row_old
        geo_transform_old = geo_transform
        n_col_old = n_col
        n_row_old = n_row
        return geo_transform, n_col, n_row


def create_hillshade(output_dir, dem_out, azimuth, altitude):
    '''
    Create hillshade and save output as a TIFF file.
    INPUTS:
        output_dir : str : path to save DEM and slope TIFF files
        dem_out : str : path to clipped DEM
        azimuth : float : sun azimuth from metadata
        altitude : float : sun altitude from metadata
    RETURNS:
        hillshade TIFF file saved in output_dir
    '''
    # create output filename
    hillshade_out = os.path.join(output_dir, 'hillshade.tif')

    dem_out = gdal.Open(dem_out)
    geo_transform = dem_out.GetGeoTransform()
    projection = dem_out.GetProjectionRef()

    # calculate hillshade
    hillshade = gdal.DEMProcessing(hillshade_out, dem_out, 'hillshade',
                                    format='GTiff',
                                    azimuth=azimuth) #, altitude=altitude)
    assert hillshade.RasterCount == 1 #TODO remove this, just make sure for now
    hillshade_data = hillshade.GetRasterBand(1).ReadAsArray()
    shape = hillshade_data.shape

    # create output file
    driver = gdal.GetDriverByName('GTiff')
    outdata = driver.Create(hillshade_out, shape[1], shape[0], 1, gdal.GDT_Byte) 
    outdata.SetGeoTransform(geo_transform)
    outdata.SetProjection(projection)
    outdata.GetRasterBand(1).SetNoDataValue(255)
    outdata.GetRasterBand(1).WriteArray(hillshade_data)

    outdata.FlushCache()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=('Use Landsat or HLS '
                '(Harmonized Landsat Sentinel-2) data to create DEM, '
                'slope, and hillshade TIFFs to input into DSWE code.'))

    parser.add_argument('input_file',
            metavar='INPUT_FILE',
            type=str,
            help='input file (supports Landsat tar.gz or HLS hdf4')
    parser.add_argument('output_dir',
            metavar='OUTPUT_DIR',
            type=str,
            help='output directory for DEM, slope, and hillshade TIFFs')
    parser.add_argument('us_dem',
            metavar='US_DEM',
            type=str,
            help='path to US national DEM file') #TODO provide more info
    parser.add_argument('slope_in',
            metavar='SLOPE_FILE',
            type=str,
            help='path to slope TIF file') #TODO provide more info

    data_type = parser.add_mutually_exclusive_group(required=True)
    data_type.add_argument('--targz',
            dest='targz',
            action='store_true',
            help='if flagged, input is a Landsat tar.gz file')
    data_type.add_argument('--hls',
            dest='targz',
            action='store_false',
            help='if flagged, input is HLS data in HDF4 format')

    args = parser.parse_args()
    main(**vars(args))
