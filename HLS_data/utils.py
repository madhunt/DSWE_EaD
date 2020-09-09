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


def hdf_bands_solar_geo(filename):
    hdf_data = gdal.Open(os.path.abspath(filename))
    hdf_metadata = hdf_data.GetMetadata_Dict()

    # get bands (subdatasets) from HDF data
    bands_info = hdf_data.GetSubDatasets()
    all_bands = []
    for band in bands_info:
        all_bands.append(band[0])
        
    # get solar geometry
    azimuth_search = 'MEAN_SUN_AZIMUTH_ANGLE'
    zenith_search = 'MEAN_SUN_ZENITH_ANGLE'

    # search metadata
    azimuth = [val for key, val in hdf_metadata.items() if azimuth_search in key][0]
    zenith = [val for key, val in hdf_metadata.items() if zenith_search in key][0]
    # convert strings to floats
    azimuth = float(azimuth)
    zenith = float(zenith)
    altitude = 90.0 - zenith

    return all_bands, azimuth, altitude


def tar_bands_solar_geo(filename, output_subdir):
    untar(filename, output_subdir)
    all_bands = [f.path for f in os.scandir(output_subdir) if os.path.isfile(f)]
    # get metadata file
    for filename in all_bands:
        if 'MTL' in filename:
            print(filename)
            metadata_file = os.path.join(output_subdir, filename)

    #XXX make sure this works for landsat 7, too
    # NOT an xml file, but has MTL in filename
    # search parameters are:
    azimuth_search = 'SUN_AZIMUTH'
    altitude_search = 'SUN_ELEVATION'

    # search through all lines of metadata file
    with open(metadata_file, 'r') as metadata:
        for line in metadata.readlines():

            print(line)

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
        return all_bands, azimuth, altitude


def assign_bands(all_bands):
    for filename in all_bands:
        #TODO make sure these WORK for all cases (and don't assign the wrong bands!!)
        if 'band02' or 'B02' or 'B2' in filename:
            blue, blue_geo, blue_proj = file_to_array(filename)
        if 'band03' or 'B03' or 'B3' in filename:
            green, green_geo, green_proj = file_to_array(filename)
        if 'band04' or 'B04' or 'B4' in filename:
            red, red_geo, red_proj = file_to_array(filename)
        if 'band05' or 'B8A' or 'B5' in filename:
            nir, nir_geo, nir_proj = file_to_array(filename)
        if 'band06' or 'B11' or 'B6' in filename:
            swir1, swir1_geo, swir1_proj = file_to_array(filename)
        if 'band07' or 'B12' or 'B7' in filename:
            swir2, swir2_geo, swir2_proj = file_to_array(filename)
        if 'Grid:QA' or 'BQA' in filename:
            pixel_qa, qa_geo, qa_proj = file_to_array(filename)

    # assert all bands have the same geo transform, 
        # projection, and shape
    assert (blue_geo == green_geo == red_geo == nir_geo ==
                swir1_geo == swir2_geo == qa_geo)
    assert (blue_proj == green_proj == red_proj == nir_proj ==
                swir1_proj == swir2_proj == qa_proj)
    assert (blue.shape == green.shape == red.shape == nir.shape ==
                swir1.shape == swir2.shape == pixel_qa.shape)

    # assign geo transform, projection, and shape
    geo_transform = blue_geo
    projection = blue_proj
    return geo_transform, projection, blue, green, red, nir, swir1, swir2, pixel_qa





