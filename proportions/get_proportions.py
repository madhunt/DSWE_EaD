'''
Calculate annual and semi-decadal proportions of water and 
mixed vegetation landcover for a single path/row.
'''


# calculate annual and semi-decadal proportions of obserations 'inundated' by open water and partial surface water classes

# input filenames have been changed by EROS since

# rework code for python 3.8 and for efficiency

# LONG-TERM GOAL: user input for compilation period (by month, year, semi-decade, season, within month) across all years
    # how do I get here from this starting point?
    # use input of either interpreted (INTR) or interpreted with masks (INWM)


# KEEP IN MIND:
    # for any given pixel, the percentages of time classified as open water, partial surface water, and not water should add up to 1.0
    # in the case of masked input, we need to trak the number of valid observations (cannot simply divide the number of tiles into number od inundations observed)
    # want 2 outputs for each timeframe (proprotion OSW and proportion PSW)


import numpy as np
#import gdal
import os
import datetime
import glob
import sys


input_dir = os.path.join('data_test', 'DSWE_out')
start_year = 2010
end_year = 2020

def setup(input_dir):
    # set working directory
    os.chdir(input_dir)

    #XXX what even does this do
    paths = glob.glob('*/')
    print(paths)
    pathcount = len(paths)


def folder_loop(input_dir, folder):
    wdir = os.path.join(input_dir, folder)
    os.chdir(wdir)
    # generate output paths
    proc_dir = os.path.join(wdir, 'processing')
    prop_dir = os.path.join(wdir, 'proportions')
    dec_prop_dir = os.path.join(wdir, 'dec_proportions')
    # make directories if they don't exist yet
    os.makedirs(proc_dir, exist_ok=True)
    os.makedirs(prop_dir, exist_ok=True)
    os.makedirs(dec_prop_dir, exist_ok=True)
    #XXX the ABOVE can become a separate function
    print('directories made', datetime.datetime.now())
    ###########################################################################################################


    # create list to hold rasters
    driver = gdal.GetDriverByName('GTiff')
    all_rasters = []
    for dir_path, dir_name, filenames in os.walk(wdir):
        for filename in filenames:
            all_rasters.append(os.path.join(dir_path, filename))
    #XXX can prob do the ABOVE better
    # process interp masked rasters
    #TODO support both interp and interp masked
    interp_mask = [s for s in all_rasters if (s.endswith('tif') and 'interp_masked' in s)]
#    interp_mask = [s for s in interp_mask if 'interp_masked' in s]
    num_rast = len(interp_mask)
    print(interp_mask)
    print(f'processing {num_rast} total scenes (all years)')
    #XXX above can be separate function
    ##############################################################################################################



    # overwrite extent min and max
    #XXX why???????????????????????????????????
    M_minx = 1e12
    M_maxx = -1e12
    M_miny = 1e12
    M_maxy = -1e12
    # loop through rasters in list
    for raster in interp_mask:
        interp = gdal.Open(os.path.abspath(raster))
        interp_geo = interp.GetGeoTransform()
        interp_proj = interp.GetProjection()
        # determine max extent of all rasters that we are processing
        # to make sure no imagery is cropped and extent/georeferencing remains const
        minx = interp_geo[0]
        maxy = interp_geo[3] #XXX print these lists out and see what's inside to understand better
        maxx = minx + interp_geo[1] * interp.RasterXSize #XXX why
        miny = maxy + interp_geo[5] * interp.RasterYSize
        extent = [minx, maxy, maxx, miny]
        # if stmts
        M_minx = minx if minx<M_minx
        M_maxy = maxy if maxy>Mmaxy
        M_maxx = maxx if maxx>M_maxx
        M_miny = miny if miny<M_miny
        max_extent = [M_minx, M_maxy, M_maxx, M_miny]
        #XXX above can be a function PLUS prob can do it better
    print('calculated max extent')
    ############################################################################################



    return


def main():
    
    for folder in paths:
        count += 1
        folder_loop(input_dir, folder)

    return



setup(input_dir)

    


























