'''
'''

import gdal
import os
import numpy as np
import argparse

def main(hdf_dir, tiff_output):
    '''

    INPUTS:
        hdf_dir : str : path to HDF4 file
        tiff_output : bool : if True, output results to TIFF files;
            if False, return DSWE bands as **_____**
    RETURNS:
    
    '''
    # open HDF file and get metadata
    hdf_data = gdal.Open(os.path.abspath(hdf_dir))
    hdf_metadata = hdf_data.GetMetadata_Dict()

    # determine if data is OLI (landsat) or MSI (sentinel)
    is_landsat, is_sentinel = oli_or_msi(hdf_metadata)

    # get bands (subdatasets) from HDF data
    all_bands = hdf_data.GetSubDatasets()

    # use OLI–HLS Band Equivalence table to assign each DSWE band
    dswe_bands = {}
    for band in all_bands:
        band_filename = band[0]
        if 'band01' or 'B01' in band_filename:
            dswe_bands['coastal'] = gdal.Open(band_filename)
        if 'band02' or 'B02' in band_filename:
            dswe_bands['blue'] = gdal.Open(band_filename))
        if 'band03' or 'B03' in band_filename:
            dswe_bands['green'] = gdal.Open(band_filename))
        if 'band04' or 'B04' in band_filename:
            dswe_bands['red'] = gdal.Open(band_filename))
        if 'B08' in band_filename:
            dswe_bands['nir10m'] = gdal.Open(band_filename))
        if 'band05' or 'B8A' in band_filename:
            dswe_bands['nir'] = gdal.Open(band_filename))
        if 'band06' or 'B11' in band_filename:
            dswe_bands['swir1'] = gdal.Open(band_filename))
        if 'band07' or 'B12' in band_filename:
            dswe_bands['swir2'] = gdal.Open(band_filename))

    if tiff_output:
        # create path to output file
        dt_str, hls_tile = get_filename_info(hdf_metadata)
        main_dir, _ = os.path.split(hdf_dir)
        filename = (dt_str + hls_tile + '_' + x30 + '_DSWEin.tiff')
        file_path = os.path.join(main_dir, filename)

        create_output_file(dswe_bands, file_path)

        return


    else:
        # currently returning a dict of gdal dataset shadows (pointers)
        return dswe_bands

    # what type should the program return for each DSWE variable if the user does not want TIFF output?
        # eg. an array, a gdal dataset, etc.?

        # WHAT TYPE SHOULD THESE BE??


def oli_or_msi(hdf_metadata):
    '''
    Determine if data is OLI (landsat) or MSI (sentinel).
    INPUTS:
        metadata : dict : metadata for input HDF dataset
    RETURNS:
        is_landsat, is_sentinel : bool
    '''
    is_landsat = False
    is_sentinel = False

    if 'SENSOR' in hdf_metadata:
        if 'OLI' in hdf_metadata['SENSOR']:
            is_landsat = True
            x30 = 'L30' # for output filename
    if 'SPACECRAFT_NAME' in hdf_metadata:
        if 'Sentinel' in hdf_metadata['SPACECRAFT_NAME']:
            is_sentinel = True
            x30 = 'S30' # for output filename
        #XXX do I need a separate category for S10?
    if is_landsat and is_sentinel:
        raise Exception('Assumption that SENSOR and SPACECRAFT_NAME are exclusive failed.')
    if not is_landsat and not is_sentinel:
        raise Exception('Dataset is neither OLI (landsat) nor MSI (sentinel).')

    return is_landsat, is_sentinel



def get_filename_info(hdf_metadata):
    '''
    Get strings for date and HLS tile ID.
    '''
    # get time of observation
    if 'SENSING_TIME' in hdf_metadata:
        date = hdf_metadata['SENSING_TIME']
        yr = date[0:4]
        mt = date[5:7]
        dy = date[8:10]
        dt_str = yr + '_' + mt + '_' + dy + '_'
    else:
        raise Exception('Assumption that SENSING_TIME in metadata failed.')

    # get HLS tile ID
    if 'TILE_ID' in hdf_metadata:
        # this makes me feel sketchy.. need to check with a regex
        # to make sure tile_id is in the correct format?
        tile_id = hdf_metadata['TILE_ID']
        hls_tile = tile_id[-13:-7]
    elif 'SENTINEL2_TILEID' in hdf_metadata:
        # this is for sure good and correct
        hls_tile = hdf_metadata['SENTINEL2_TILEID']
    else:
        raise Exception('Assumption that TILE_ID present for MSI or SENTINel2_TILEID present for OLI failed.')

    return dt_str, hls_tile


def create_output_file(dswe_bands, file_path):
    dswe_data = {}

    # read in data
    for i, key in enumerate(dswe_bands):
        band = dswe_bands[key]
        geo_transform = band.GetGeoTransform()
        projection = band.GetProjection()

        assert band.RasterCount == 1
        data = band.GetRasterBand(1).ReadAsArray()
        shape = data.shape
        dswe_data[key] = data
        
        if i != 0:
            # assert geo transform and projection remained the same
            assert geo_transform == geo_transform_old
            assert projection == projection_old
            assert shape == shape_old
        geo_transform_old = geo_transform
        projection_old = projection
        shape_old = shape

    # write out data
    num_bands = len(dswe_bands)
    driver = gdal.GetDriverByName('GTiff')
    outdata = driver.Create(file_path, shape[1], shape[0], num_bands, gdal.GDT_Byte)
    outdata.SetGeoTransform(geo_transform)
    outdata.SetProjection(projection)
    
    for i, key in enumerate(dswe_data, start=1):
        data = dswe_data[key]
        outdata.GetRasterBand(i).WriteArray(data)

    outdata.FlushCache()



#if __name__ = '__main__':
    # get command line args
#hdf_dir = '/home/mad/DSWE_EaD/test_data/hls_data/HLS.L30.T01UDT.2020008.v1.4.hdf'
hdf_dir = '/home/mad/DSWE_EaD/test_data/hls_data/HLS.S30.T08UNG.2020001.v1.4.hdf'
#hdf_dir = '/home/mad/DSWE_EaD/test_data/hls_data/HLS.S30.T32SMJ.2017004.v1.4.hdf'

tiff_output = True



main(hdf_dir, tiff_output)
