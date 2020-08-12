'''
Main code to calculate proportions.
'''
import argparse
import os
import utils
import time_periods as tp

import gdal
import osr


main_dir = '/home/mad/DSWE_EaD/test_data/DRB_test/data/good_data'
dswe_layer = 'INWM'



# move to main directory
os.chdir(main_dir)

# make a list of DSWE files of interest and their dates
all_files, all_dates = utils.get_files(main_dir, dswe_layer)
num_files = len(all_files)
print(f'Processing {num_files} total scenes from {min(all_dates)} to {max(all_dates)}')


# get corners of each file

all_top_left = []
all_bot_right = []

for file in all_files:
    
    def get_corners(file):
        raster = gdal.Open(os.path.abspath(file))
        geo_transform = raster.GetGeoTransform()
        
        x_size = raster.RasterXSize
        y_size = raster.RasterYSize
        x_res = geo_transform[1]
        y_res = geo_transform[5]

        x_min = geo_transform[0]
        y_max = geo_transform[3]
        x_max = x_min + x_res * x_size
        y_min = y_max + y_res * y_size

        top_left = (x_min, y_max)
        bot_right = (x_max, y_min)

        return top_left, bot_right

    top_left, bot_right = get_corners(file)

    all_top_left.append(top_left)
    all_bot_right.append(bot_right)

# now we have lists of all top left and bottom right corners

# for each unique coordinates, we need to process the files

for top_left in uniq_top_left:

    current_top_left = top_left

    for top_left in all_top_left:
        if top_left == current_top_left:
            # process here
    






# get extent (lat/long) of each file

# get coordinates of 4 corners and reproject to lat/long


all_extents = []
all_latlons = []

all_lat = []
all_lon = []

all_xmin = []
all_ymax = []

for file in all_files:
    raster = gdal.Open(os.path.abspath(file))
    geo_transform = raster.GetGeoTransform()

    x_min = geo_transform[0]
    y_max = geo_transform[3]
    x_max = x_min + geo_transform[1] * raster.RasterXSize
    y_min = y_max + geo_transform[5] * raster.RasterYSize
    

    all_xmin.append(x_min)
    all_ymax.append(y_max)

    all_extents.append([x_min, y_min, x_max, y_max])

    
    print(geo_transform[1])
    print(geo_transform[5])

    # now reporject coordinates
    src_srs = osr.SpatialReference()
    src_srs.ImportFromWkt(raster.GetProjection())
    tgt_srs = src_srs.CloneGeogCS()

    transform = osr.CoordinateTransformation(src_srs, tgt_srs)
    lat_min, lon_min, _ = transform.TransformPoint(x_min, y_min)
    lat_max, lon_max, _ = transform.TransformPoint(x_max, y_max)
    
    lower_left = (lon_min, lat_min)
    upper_right = (lon_max, lat_max)
    
    #print(lon_max-lon_min)
    #print(lat_max-lat_min)

    #all_latlons.append([lower_left, upper_right])
    all_lat.append(lat_min)
    all_lat.append(lat_max)
    all_lon.append(lon_min)
    all_lon.append(lon_max)


uniq_lat = (list(set(all_lat)))
uniq_lat.sort()
uniq_lon = (list(set(all_lon)))
uniq_lon.sort()

#print(uniq_lat)
#print(uniq_lon)

#for i,val in enumerate(uniq_lat):
#    diff = uniq_lat[i+1] - val
#    print(diff)



uniq_x = (list(set(all_xmin)))
uniq_y = list(set(all_ymax))
print(uniq_x)
print(uniq_y)


