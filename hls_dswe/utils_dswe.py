'''
Contains utility functions used in DSWE code.
'''
import gdal
import json
import numpy as np
import os
import tarfile

def hdf_bands(filename):
    '''
    Get file paths to all bands in an HDF4 file.
    INPUTS:
        filename : str : path to HDF4 file
    RETURNS:
        all_bands : list of str : list of paths to each band
    '''
    hdf_data = gdal.Open(os.path.abspath(filename))
    bands_info = hdf_data.GetSubDatasets()
    all_bands = [band[0] for band in bands_info]
    return all_bands


def tar_bands(filename, output_subdir):
    '''
    Untar and get paths to all bands in a TAR file.
    INPUTS:
        filename : str : path to TAR file
        output_subdir : str : subdirectory to untar contents of
            file
    RETURNS:
        all_bands : list of str : list of paths to each band
    '''
    untar(filename, output_subdir)
    all_bands = [f.path for f in os.scandir(output_subdir)
                        if os.path.isfile(f)]
    return all_bands

def untar(input_file, output_dir):
    '''
    Extract contents of TAR file to output directory.
    INPUTS:
        input_file : str : path to tar file
        output_dir : str : path to directory to extract file
    RETURNS:
        Extracted TAR file in output_dir
    '''
    # make sure input file exists and is a tar file
    if os.path.isfile(input_file) and tarfile.is_tarfile(input_file):
        # create directory for extracted files
        tar_file = tarfile.open(input_file)

        tar_file.extractall(output_dir)
        tar_file.close()

    # otherwise..
    elif not os.path.isfile(input_file):
        raise Exception(f'Input file does not exist: {input_file}')
    elif not tarfile.is_tarfile(input_file):
        raise Exception(f'Input file is not a tar file: {input_file}')


def assign_bands(all_bands):
    '''
    Create a dictionary of paths to valid DSWE input bands.
    INPUTS:
        all_bands : list of str : list of paths to all bands
    RETURNS:
        band_dict : dict : dictionary with keys corresponding
            to the unscaled surface reflectance bands (blue,
            green, red, nir, swir1, and swir2) and values as
            paths to those bands
        geo_transform : tuple : raster coordinates related to
            georeferencing coordinates by affine transform
        projection : list : GDAL projection metadata
    '''
    band_dict = {}
    for filename in all_bands:
        if ('band02' in filename) or ('B02' in filename) or ('B2' in filename):
            band_dict['blue'] = filename
            blue_geo, blue_proj = get_geo_info(filename)
        if ('band03' in filename) or ('B03' in filename) or ('B3' in filename):
            band_dict['green'] = filename
            green_geo, green_proj = get_geo_info(filename)
        if ('band04' in filename) or ('B04' in filename) or ('B4' in filename):
            band_dict['red'] = filename
            red_geo, red_proj = get_geo_info(filename)
        if ('band05' in filename) or ('B8A' in filename) or ('B5' in filename):
            band_dict['nir'] = filename
            nir_geo, nir_proj = get_geo_info(filename)
        if ('band06' in filename) or ('B11' in filename) or ('B6' in filename):
            band_dict['swir1'] = filename
            swir1_geo, swir1_proj = get_geo_info(filename)
        if ('band07' in filename) or ('B12' in filename) or ('B7' in filename):
            band_dict['swir2'] = filename
            swir2_geo, swir2_proj = get_geo_info(filename)
        if ('Grid:QA' in filename) or ('BQA' in filename) or ('PIXELQA' in filename):
            band_dict['pixel_qa'] = filename
            qa_geo, qa_proj = get_geo_info(filename)

    # assert all bands have same geo transform and projection
    assert (blue_geo == green_geo == red_geo == nir_geo ==
                swir1_geo == swir2_geo == qa_geo)
    assert (blue_proj == green_proj == red_proj == nir_proj ==
                swir1_proj == swir2_proj == qa_proj)

    # assign geo transform and projection
    geo_transform = blue_geo
    projection = blue_proj
    return band_dict, geo_transform, projection


def get_geo_info(filename):
    ''' 
    Get geo transform and projection from dataset.
    INPUTS:
        filename : str : path to TIFF file or band
    RETURNS:
        geo_transform : tuple : raster coordinates related to
            georeferencing coordinates by affine transform
        projection : list : GDAL projection metadata
    '''
    data = gdal.Open(filename)
    geo_transform = data.GetGeoTransform()
    projection = data.GetProjection()
    return geo_transform, projection


def get_fill_array(band_dict):
    '''
    INPUTS:
        band_dict : dict : dictionary with keys corresponding
            to the unscaled surface reflectance bands (blue,
            green, red, nir, swir1, and swir2) and values as
            paths to those bands
    RETURNS:
        fill : int : value of non-data (fill) pixels in the
            above bands
        fill_array : numpy array : (n by m) boolean array;
            pixels are True where any input band has non-data
            (fill) values
    '''
    # get fill (no-data) values for all bands
    blue_fill = fill_value(band_dict['blue'])
    green_fill = fill_value(band_dict['green'])
    red_fill = fill_value(band_dict['red'])
    nir_fill = fill_value(band_dict['nir'])
    swir1_fill = fill_value(band_dict['swir1'])
    swir2_fill = fill_value(band_dict['swir2'])

    # make sure fill values are the same
    assert (blue_fill == green_fill == red_fill ==
                nir_fill == swir1_fill == swir2_fill)
    fill = blue_fill

    # get bands as np arrays
    blue = file_to_array(band_dict['blue'])
    green = file_to_array(band_dict['green'])
    red = file_to_array(band_dict['red'])
    nir = file_to_array(band_dict['nir'])
    swir1 = file_to_array(band_dict['swir1'])
    swir2 = file_to_array(band_dict['swir2'])

    # find where any input band has a no-data value
    fill_array = np.full(blue.shape, False, dtype=bool)
    fill_array[(blue == fill) | (green == fill) |
                (red == fill) | (nir == fill) |
                (swir1 == fill) | (swir2 == fill)] = True

    return fill, fill_array


def file_to_array(filename):
    '''
    Open file as GDAL dataset and read as numpy array.
    '''
    data = gdal.Open(filename)
    array = data.GetRasterBand(1).ReadAsArray()
    return array


def fill_value(filename):
    '''
    Find fill (no-data) value for a GDAL dataset.
    '''
    data = gdal.Open(filename)
    fill = data.GetRasterBand(1).GetNoDataValue()
    return fill


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
