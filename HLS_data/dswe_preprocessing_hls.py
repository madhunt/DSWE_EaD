'''

''' 
import os
import numpy as np # just use .shape and get rid of this import
import gdal
import datetime
import glob
import sys
import tarfile
import argparse


import re
import read_hls


from lxml import etree


def main(input_file, output_dir, us_dem, slope_in, targz):
    '''
    
    '''
    # create output_dir if doesn't exist
    os.makedirs(output_dir, exist_ok=True)


    if targz: # input is landsat tar.gz file
        # get list of bands
        unpack_dir = untar(input_file, output_dir)
        band_files = []
        for dirpath, _, filenames in os.walk(unpack_dir):
            for filename in filenames:
                if '.tif' in filename:
                    filepath = os.path.join(dirpath, filename)
                    band_files.append(filepath)
                if 'MTL' in filename:
                    metadata_file = filename

        # get metadata
        azimuth, altitude = get_tar_metadata(metadata_file)


    else: # input is HLS file
        # get list of bands
        dswe_bands = read_hls.main(input_file, tiff_output=False, output_dir=None)
        band_files = list(dswe_bands.values())

        # get metadata
        band_filename = band_files[0]
        match = re.search('\"(.+?)\"', band_filename)
        hls_filename = match.group(1)

        azimuth, altitude = get_hls_metadata(hls_filename)



    #TODO plus, make 3 sep functions for dem, slp, and hillshade
    create_dem_and_slope(output_dir, band_files, us_dem, slope_in)
    

    dem_slp_hillshade(output_dir, band_files, dem, slp)


def untar(input_file, output_dir):
    '''
    Unpack tar.gz file of Landsat bands.
    INPUTS:
        input_file : str : path to tar.gz file
        output_dir : str : path to directory to unpack files in
    RETURNS:
        tar.gz files unpacked in subdirectory of output_dir
    '''
    # make sure input file exists and is a tar file
    if os.path.isfile(input_file) and tarfile.is_tarfile(input_file):
        unpack_dir = os.path.splitext(input_file)[0]
        tar_file = tarfile.open(input_file, mode='r:gz')
        # extract data to subdirectory
        tar_file.extractall(unpack_dir)
        
        # close tar file
        tar_file.close()

        return unpack_dir

    elif not os.path.isfile(input_file):
        raise Exception(f'Input file does not exist: {input_file}')
    elif not tarfile.is_tarfile(input_file):
        raise Exception(f'Input file is not a tar file: {input_file}')
        

    
def create_dem_and_slope(output_dir, band_files, us_dem, slope_in):
    '''
    Create DEM and percent slope as output TIFF files.
    INPUTS:
        output_dir : str : path to save DEM and slope TIFF files
        band_files : list of str : list of paths to each band in the Landsat or HLS data
        
    RETURNS:
        
    '''
    dem_out = os.path.join(output_dir, 'DEM.tif')
    slope_out = os.path.join(output_dir, 'slope.tif')

    geo_transform, projection, n_col, n_row = get_band_properties(band_files)

    # get min/max coordinates from landsat bands
    min_x = geo_transform[0]
    max_y = geo_transform[3]
    max_x = min_x + geo_transform[1] * n_col
    min_y = max_y + geo_transform[5] * n_row

    # open total US DEM and percent slope
    dem_in = gdal.Open(us_dem)
    slope_in = gdal.Open(slope_in)

    # clip DEM and slope
    #XXX are these clipped images saved? check on this
    geo_clip = [min_x, max_y, max_x, min_y]
    dem_clip = gdal.Translate(dem_out, dem_in, projWin=geo_clip)
    slope_clip = gdal.Translate(slope_out, slope_in, projWin=geo_clip)
    #perslp = gdal.DEMProcessing(slope_out, dem_clip, 'slope', slopeFormat = 'percent', format = 'GTiff')


def get_tar_metadata(metadata_file):
    '''
    '''

    azimuth_search = 'SUN_AZIMUTH'
    altitude_search = 'SUN_ELEVATION'
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


def get_hls_metadata(hls_filename):
    hls_data = gdal.Open(hls_filename)
    hls_metadata = hls_data.GetMetadata()
    
    zenith_search = 'MEAN_SUN_ZENITH_ANGLE'
    azimuth_search = 'MEAN_SUN_AZIMUTH_ANGLE'

    zenith = [val for key, val in hls_metadata.items() if zenith_search in key][0]
    azimuth = [val for key, val in hls_metadata.items() if azimuth_search in key][0]

    zenith = float(zenith)
    azimuth = float(azimuth)
    altitude = 90.0 - zenith
    return azimuth, altitude


def dem_slp_hillshade(output_dir, band_files, dem, slp):

    ####################

    dst_hshd = os.path.join(output_dir, 'hillshade.tif')
    ## calculate hillshade
    print "calculate hillshade ..."
    #HillshadeOut="hillshade_mask" + "_%s.tif"%"_".join(raster.split('_'))[0:length]
    #Hoping the altitude issue is repaired shortly, will be an easy fix once it is corrected
    #Hillshade = gdal.DEMProcessing('hillshade.tif', DEM, 'hillshade', format = 'GTiff', azimuth = Az, altitude=Alt)
    dst_dem_ds = gdal.Open(dst_dem)
    geotrans = dst_dem_ds.GetGeoTransform()
    prj = dst_dem_ds.GetProjectionRef()
    hlshd_ds = gdal.DEMProcessing(dst_hshd, dst_dem_ds, 'hillshade', format = 'GTiff', azimuth = Az) # this fails on linux :(
    hlshd_band = hlshd_ds.GetRasterBand(1)
    hlshd_data = hlshd_band.ReadAsArray()
    
    # save the hillshade
    nrows,ncols = np.shape(hlshd_data)
    driver = gdal.GetDriverByName("GTiff")
    dst_hlshd = driver.Create(dst_hshd, ncols, nrows, 1, gdal.GDT_Byte)
    dst_hlshd.SetGeoTransform( geotrans )
    dst_hlshd.SetProjection( prj )
    hlsh_band = dst_hlshd.GetRasterBand(1)       
    hlsh_band.WriteArray( hlshd_data )
    hlsh_band.SetNoDataValue(255)
    hlsh_band = None
    dst_hlshd.FlushCache()
    dst_hlshd = None    
    dst_dem_ds = None
    




def get_band_properties(band_files):
    '''
    Get properties of all bands in the Landsat or HLS data.
    INPUTS:
        band_files : list of str : list of paths to each band in 
            the Landsat or HLS data
    RETURNS:
        geo_transform : tuple : coordinates of top left corner of all bands
        projection : 
        n_col : int : number of columns (pixels in x direction)
        n_row : int : number of rows (pixels in y direction)
    '''
    for i, filename in enumerate(band_files):
        band = gdal.Open(filename)
        geo_transform = band.GetGeoTransform()
        projection = band.GetProjection()
        n_col = band.RasterXSize
        n_row = band.RasterYSize + 1 #XXX why +1 ??

        if i != 0:
            # assert these properties are the same for all bands
            assert geo_transform == geo_transform_old
            assert projection == projection_old
            assert n_col == n_col_old
            assert n_row == n_row_old
        geo_transform_old = geo_transform
        projection_old = projection
        n_col_old = n_col
        n_row_old = n_row
        return geo_transform, projection, n_col, n_row



    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('input_file',
            metavar='INPUT_FILE',
            type=str,
            help='input Landsat tar.gz file')
    parser.add_argument('output_dir',
            metavar='OUTPUT_DIR',
            type=str,
            help='output directory for Landsat geotiffs, metadata, and elevation model')
    parser.add_argument('us_dem',
            metavar='US_DEM',
            type=str,
            help='path to US DEM file')
    parser.add_argument('slope_in',
            metavar='SLOPE_FILE',
            type=str,
            help='path to slope TIF file')


    data_type = parser.add_mutually_exclusive_group(required=True)
    data_type.add_argument(--targz,
            dest='targz',
            action='store_true',
            help='if flagged, input is a Landsat tar.gz file')
    data_type.add_argument(--hls,
            dest='targz',
            action='store_false',
            help='if flagged, input is HLS data in HDF4 format')


    args = parser.parse_args()

    main(**vars(args))
