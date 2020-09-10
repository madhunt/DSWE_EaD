'''
Contains utility functions called by main in DSWE code.
'''

import gdal
import json
import os
import tarfile
import re

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
        tar_file = tarfile.open(input_file)#, mode='r:gz')

        # extract data to subdirectory
        tar_file.extractall(output_dir)
        
        # close tar file
        tar_file.close()

    # otherwise..
    elif not os.path.isfile(input_file):
        raise Exception(f'Input file does not exist: {input_file}')
    elif not tarfile.is_tarfile(input_file):
        raise Exception(f'Input file is not a tar file: {input_file}')


def get_geo_info(filename):
    ''' 
    Open file as gdal dataset, get geo transform and
    projection, convert to numpy array.
    '''
    data = gdal.Open(filename)
    geo_transform = data.GetGeoTransform()
    projection = data.GetProjection()
    #array = data.GetRasterBand(1).ReadAsArray()
    return geo_transform, projection


def get_thresholds():
    '''
    Open the thresholds.json file, which should be in the same
    directory as this python file.
    Returns the threshold values as a dictionary.
    '''
    # get path of this file
    script_path = os.path.realpath(__file__)
    path = os.path.split(script_path)[0] # get path to script dir
    thresholds_path = os.path.join(path, 'thresholds.json')

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
    shape = data.shape
    driver = gdal.GetDriverByName('GTiff')
    outdata = driver.Create(filename, shape[1], shape[0], 1, gdal.GDT_Byte)
    outdata.SetGeoTransform(geo_transform)
    outdata.SetProjection(projection)
    outdata.GetRasterBand(1).SetNoDataValue(255)
    outdata.GetRasterBand(1).WriteArray(data)
    outdata.FlushCache()


def hdf_bands(filename):
    hdf_data = gdal.Open(os.path.abspath(filename))

    # get bands (subdatasets) from HDF data
    bands_info = hdf_data.GetSubDatasets()
    all_bands = []
    for band in bands_info:
        all_bands.append(band[0])
    return all_bands


def tar_bands(filename, output_subdir):
    untar(filename, output_subdir)
    all_bands = [f.path for f in os.scandir(output_subdir) if os.path.isfile(f)]
    return all_bands


def assign_bands(all_bands):
    band_dict = {}
    for filename in all_bands:
        #TODO make sure these WORK for all cases (and don't assign the wrong bands!!)
        if ('band02' or 'B02' or 'B2') in filename:
            band_dict['blue'] = filename
            blue_geo, blue_proj = get_geo_info(filename)
        if ('band03' or 'B03' or 'B3') in filename:
            band_dict['green'] = filename
            green_geo, green_proj = get_geo_info(filename)
        if ('band04' or 'B04' or 'B4') in filename:
            band_dict['red'] = filename
            red_geo, red_proj = get_geo_info(filename)
        if ('band05' or 'B8A' or 'B5') in filename:
            band_dict['nir'] = filename
            nir_geo, nir_proj = get_geo_info(filename)
        if ('band06' or 'B11' or 'B6') in filename:
            band_dict['swir1'] = filename
            swir1_geo, swir1_proj = get_geo_info(filename)
        if ('band07' or 'B12' or 'B7') in filename:
            band_dict['swir2'] = filename
            swir2_geo, swir2_proj = get_geo_info(filename)
        if ('Grid:QA' or 'BQA') in filename:
            band_dict['pixel_qa'] = filename
            qa_geo, qa_proj = get_geo_info(filename)

    # assert all bands have the same geo transform, 
        # projection, and shape
    assert (blue_geo == green_geo == red_geo == nir_geo ==
                swir1_geo == swir2_geo == qa_geo)
    assert (blue_proj == green_proj == red_proj == nir_proj ==
                swir1_proj == swir2_proj == qa_proj)
    #assert (blue.shape == green.shape == red.shape == nir.shape ==
                #swir1.shape == swir2.shape == pixel_qa.shape)

    # assign geo transform, projection, and shape
    geo_transform = blue_geo
    projection = blue_proj
    return band_dict, geo_transform, projection


def file_to_array(filename):
    data = gdal.Open(filename)
    array = data.GetRasterBand(1).ReadAsArray()
    return array


def fill_value(filename):
    data = gdal.Open(filename)
    fill = data.GetRasterBand(1).GetNoDataValue()
    return fill


def get_fill_array(band_dict):
    blue = file_to_array(band_dict['blue'])
    green = file_to_array(band_dict['green'])
    red = file_to_array(band_dict['red'])
    nir = file_to_array(band_dict['nir'])
    swir1 = file_to_array(band_dict['swir1'])
    swir2 = file_to_array(band_dict['swir2'])

    blue_fill = fill_value(band_dict['blue'])
    green_fill = fill_value(band_dict['green'])
    red_fill = fill_value(band_dict['red'])
    nir_fill = fill_value(band_dict['nir'])
    swir1_fill = fill_value(band_dict['swir1'])
    swir2_fill = fill_value(band_dict['swir2'])

    assert (blue_fill == green_fill == red_fill ==
                nir_fill == swir1_fill == swir2_fill)
    fill = blue_fill

    fill_array = np.full(blue.shape, False, dtype=bool)
    fill_array[(blue == fill) | (green == fill) | (red == fill) |
                (nir == fill) | (swir1 == fill) | (swir2 == fill)] = True

    return fill, fill_array

