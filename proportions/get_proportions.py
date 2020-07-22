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


#TODO break this file up into 2 files for readability: utilities and main code


import numpy as np
import gdal
import os
import datetime
import glob
import sys

import proportions_utils as utils



def find_max_extent(raster, max_extent):
    #XXX neaten and prob do better
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
    return max_extent


def reclassify_interp_layer(interp):
    interp_copy = interp.copy
    interp_copy[np.where((interp_copy==255) | (interp_copy==9))] = 0

    water = interp_copy.copy() #XXX what do these magic numbers mean/do?????????????????? ASK*****
    water[np.where(water==2)] = 1
    water[np.where((water==4) | (water==3))] = 0

    mixed = interp_copy.copy()
    mixed[np.where((mixed==1) | (mixed==2) | (mixed==4))] = 0
    mixed[np.where(mixed==3)] = 1

    nonwater = interp_copy.copy()
    nonwater[np.where(nonwater==0)] = 4
    npnwater[np.where((nonwater==1) | (nonwater==2) | (nonwater==3))] = 0
    nonwater[np.where(nonwater==4)] = 1

    return water, mixed, nonwater



def proportions_calculations(wdir, proc_dir, prop_dir, dec_prop_dir):
    count += 1
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

    # loop through rasters in list
    # overwrite extent min and max
    #XXX why???????????????????????????????????
    M_minx = 1e12
    M_maxx = -1e12
    M_miny = 1e12
    M_maxy = -1e12
    for raster in interp_mask:
        #TODO make sure that this is replacing max extent for each folder each time and that it makes sense
        # if stmts

        #TODO madeline make sure this is eorking and makes sense
        M_minx = minx if minx<M_minx else M_minx
        M_maxy = maxy if maxy>Mmaxy else M_maxy
        M_maxx = maxx if maxx>M_maxx else M_maxx
        M_miny = miny if miny<M_miny else M_miny
        max_extent = [M_minx, M_maxy, M_maxx, M_miny]
        #XXX prob can do it better
        max_extent = find_max_extent(raster) # function needs to get new updated M_vals every time
    print('calculated max extent')
    

    trim = raster[-25:]
    path_row = trim[3:9] #XXX what and why


    # calculate proportions each year, searching scenes only from the year of interest
    active_year = start_year
    while active_year <= end_year:
        ###############################################################################################
        year_interp = []
        for raster in interp_mask:
            trim = raster[-25:]
            year = int( trim[9:13] ) #XXX what and why
            if year == active_year:
                year_interp.append(raster)
            #XXX find a way to make this for loop better
        ##############################################################################################
        num_rast = len(year_interp)
        if num_rast >= 1: #XXX do we need this statement? do we need an else to this?
            count = 0
            for raster in year_interp:

                def open_interp(raster, proc_dir, max_extent):
                    interp = gdal.Open(os.path.abspath(raster))
                    print('opened', raster)
                    interp_max_extent_out = os.path.join(proc_dir, 'interp.tif')
                    # expand every interpreted layer to max extent of all data for the path/row
                    interp = gdal.Translate(interp_max_extent_out, interp, projWin=max_extent) #XXX what
                    max_geo = interp.GetGeoTransform()
                    interp = interp.GetRasterband(1).ReadAsArray()
                    shape = interp.shape
                    return interp, max_geo, shape

                interp, max_geo, shape = open_interp(raster, proc_dir, max_extent)

        ###############################################################################################
                # reclassify interpreted layer
                if count == 0:
                    #XXX initialze to 0 or empty and each time, += the function to remove both these gross if stmts
                    water, mixed, nonwater = reclassify_interp_layer(interp)

                    count += 1
                    
                    #XXX does the count = 0 need to happen where it does?
                    print(f'{count} of {num_rast} scenes processed')

                # reclassify interpreted layer and add to previously reclassified layers
                elif count > 0 and count < num_rast:
                    water2, mixed2, nonwater2 = reclassify_interp_layer(interp)
                    #XXX there has got to be a better way to do this -- we are just adding on each loop

                    water = water + water2
                    mixed = mixed + mixed2
                    nonwater = nonwater + nonwater2
                    count += 1
                    print(f'{count} of {num_rast} scenes processed')
                # get mixed, water, and nonwater at the end of all this
        ##################################################################################################
            if count == num_rast: 
                year = str(active_year)
                

                # identify which pixels contain data
                contains_data = water + mixed + nonwater
                create_proc_file(contains_data, 'containsdata', proc_dir, max_geo, interp_proj)
                # do the other pixels
                create_output_file(water, 'water', proc_dir, max_geo, interp_proj, path_row, year)
                create_output_file(mixed, 'mixed', proc_dir, max_geo, interp_proj, path_row, year)
                create_output_file(nonwater, 'nonwater', proc_dir, max_geo, interp_proj, path_row, year)
                # calculate water proportion for the year
                water_prop = np.rint(water / np.float32(contains_data) * 100) #round
                create_output_file(water_prop, 'water', prop_dir, max_geo, interp_proj, path_row, year)
                # calculate mixed proportion for the year
                mixed_prop = np.rint(mixed / np.float32(contains_data) * 100)
                create_output_file(mixed_prop, 'mixed', prop_dir, max_geo, interp_proj, path_row, year)
                print(f'proportions completed for {year}')
        active_year += 1
    return

def create_output_file(data, data_str, out_dir, max_geo, interp_proj, path_row, year):
    if 'dec_proportions' in out_dir:
        data_file = os.path.join(out_dir, f'DSWE_V2_P1_{path_row}_{year[0]}_{year[1]}_{data_str}Proportion.tif')
    elif 'processing' in out_dir:
        data_file = os.path.join(out_dir, f'DSWE_V2_P1_{path_row}_{year}_{data_str}Sum.tif')
    elif 'proportions' in out_dir:
        data_file = os.path.join(out_dir, f'DSWE_V2_P1_{path_row}_{year}_{data_str}Proportion.tif')


    data_out = driver.Create(data_file, shape[1], shape[0], 1, gdal.GDT_Byte) #XXX what
    data_out.SetGeoTransform(max_geo)
    data_out.SetProjection(interp_proj)
    data_out.GetRasterBand(1).WriteArray(data)
    return

def decadal_calculations():
    print('processing semi-decadal proportions')
    active_year = start_year
    range_year = active_year + 4 #XXX why 4
    os.chdir(proc_dir)
    all_rasters = []
    water_rasters = []
    mixed_rasters = []
    data_rasters = []
    
    #########################################################################################################
    # id previously created reclassified interpreted layers for processing
    for (dir_path, dir_names, filenames) in os.walk(proc_dir):
        print(filenames)
        for filename in filenames:
            all_rasters.append(filename) #XXX note: can prob make this a function that gets called by proc_calc above
            all_rasters = [s for s in all_rasters if s.endswith('tif')] #XXX do these 4 statements need to be in the for loop?
            water_rasters = [s for s in all_rasters if 'waterSum' in s] #XXX OR is this unecessary and they could be outside the loo
            mixed_rasters = [s for s in all_rasters if 'mixedSum' in s]
            data_rasters = [s for s in all_rasters if 'containsdataSum' in s]
    #############################################################################################################
    print(active_year, 'to', range_year)
    while range_year <= end_year:
        # process only semi-decadal years of interest
        
        def years_to_process(rasters):
            year_rasters = []
            for raster in rasters:
                raster_year = int(raster[18:22])
                if raster_year >= active_year and raster_year <= range_year:
                    year_rasters.append(raster)
            return year_rasters

        water_year_rasters = years_to_process(water_rasters)
        mixed_year_rasters = years_to_process(mixed_rasters)
        data_year_rasters = years_to_process(data_rasters)

        # sum each annual raster to create semi-decadal proportions
        if len(water_year_rasters) >= 1:

            def sum_annual_rasters(year_rasters, shape):
                data = np.zeros(shape)
                for raster in year_rasters:
                    new_data = gdal.Open(os.path.abspath(raster))
                    new_data = new_data.GetRasterBand(1).ReadAsArray()
                    data += new_data
                return data

            water = sum_annual_rasters(water_year_rasters, shape)
            mixed = sum_annual_rasters(mixed_year_rasters, shape)
            data = sum_annual_rasters(data_year_rasters, shape)

            year = [str(active_year), str(range_year)]

            water_prop = np.rint(water / np.float32(data) * 100)
            create_output_file(water, 'water', dec_prop_dir, max_geo, interp_proj, path_row, year)

            mixed_prop = np.rint(mixed/ np.float32(data) * 100)
            create_output_file(mixed, 'mixed', dec_prop_dir, max_geo, interp_proj, path_row, year)

            active_year = range_year + 1
            range_year = active_year + 4
        else: #XXX could turn this if/else into a while
            active_year = range_year + 1
            range_year = active_year + 4

    print('decadal proportions output')




    return




def main(input_dir, start_year, end_year):
    # set working directory
    os.chdir(input_dir)

    #XXX what even does this do
    paths = glob.glob('*/')
    print(paths)
    pathcount = len(paths)
    
    for folder in paths:
        wdir, proc_dir, prop_dir, dec_prop_dir = utils.make_dirs(input_dir, folder)
        
        #proportions_calculations(wdir, proc_dir, prop_dir, dec_prop_dir)

        #decadal_calculations(start_year, end_year, proc_dir)

    #if pathcount == count:
    #    print('all processing done yay')


    return


input_dir = os.path.join('data_test', 'DSWE_out')
start_year = 2010
end_year = 2020

main(input_dir, start_year, end_year)
    


