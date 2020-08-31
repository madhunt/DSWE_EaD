'''
Contains utility functions called by main in DSWE code.
'''

import gdal
import json
import os



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







