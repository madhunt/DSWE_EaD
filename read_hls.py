'''
'''

import gdal
import os


#hdf_dir = '/home/mad/DSWE_EaD/test_data/hls_data/HLS.L30.T01UDT.2020008.v1.4.hdf'
hdf_dir = '/home/mad/DSWE_EaD/test_data/hls_data/HLS.S30.T08UNG.2020001.v1.4.hdf'


hdf_data = gdal.Open(os.path.abspath(hdf_dir))


is_landsat = False
is_sentinel = False


# figure out if the data is OLI (landsat) or MSI (sentinel)
hdf_metadata = hdf_data.GetMetadata_Dict()

if 'SENSOR' in hdf_metadata:
    if 'OLI' in hdf_metadata['SENSOR']:
        is_landsat = True

if 'SPACECRAFT_NAME' in hdf_metadata:
    if 'Sentinel' in hdf_metadata['SPACECRAFT_NAME']:
        is_sentinel = True

if is_landsat and is_sentinel:
    # raise an error if this ever happens in the future!
    raise Exception('Assu mption that SENSOR and SPACECRAFT_NAME are exclusive failed.')


if 'SENSING_TIME' in hdf_metadata:
    dt_str = hdf_metadata['SENSING_TIME']
    yr = dt_str[0:4]
    mt = dt_str[5:7]
    dy = dt_str[8:10]
    

all_bands = hdf_data.GetSubDatasets()
coastal = all_bands[0]
blue = all_bands[1]
green = all_bands[2]
red = all_bands[3]

if is_landsat:
    nir = all_bands
    swir1 = all_bands
    swir2 = all_bands
if is_sentinel:
    nir10m = all_bands
    nir = all_bands
    swir1 = all_bands
    swir2 = all_bands



breakpoint()





# tiff output desired?



# make file list from HLS subdirs



# OSI (landsat) or MSI (sentinel2)?



# variables for each band used in DSWE [* see table]




# write tiff output files if desired [* see file naming convention]





out_filename = yr + '_' + mt + '_' + dy


#YYYY_MM_DD_HLSTile_X30_DSWEin.tiff
#
#Where:
#
#YYYY = year of observation
#
#MM = month of observation
#
#DD = day of observation
#
#HLSTile = HLS tile designation (e.g., T18STJ)
#
#X = L for Landsat, S for Sentinel
#
#DSWEin = just what it says! DSWEin for ‘DSWE Input’







