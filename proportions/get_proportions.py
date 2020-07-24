'''
'''

import numpy as np
import gdal
import os
import datetime
import glob
import sys

import proportions_utils as utils

main_dir = '/home/mad/DSWE_EaD/proportions/test_data/20yrspan'
Start_yr = 1985
End_yr = 1995
DSWE_layer = 'INWM' #or 'INTR'

#Ultimately, we’d like user input for the compilation period, that is: by month, year, semi-decade, “season”, and within month but across all years!


os.chdir(main_dir)

# make a list of all DSWE files of interest
all_files = []
# look through all directories and subdirectories (tree)
for dirpath, dirnames, filenames in os.walk(main_dir):
    # find all files in tree
    for filename in filenames:
        # if the file is the layer of interest
        if DSWE_layer in filename: 
            all_files.append(os.path.join(dirpath, filename))

# make output directories
process_dir, prop_dir, dec_prop_dir = utils.make_dirs(main_dir)

num_files = len(all_files)
print(f'Processing {num_files} Total Scenes (All Years)')

breakpoint()

for folder in paths:

    print(all_files)

    # initialize extent to be overwritten 
    extent_0 = [1e12, -1e12, -1e12, 1e12]

    # Loop through rasters in list
    for raster in all_files:
        # calculate max extent
        extent_0 = utils.find_max_extent(raster, extent_0)
    max_extent = extent_0
    print("Max Extent calculated")
    # Get Path/Row
    trim = raster[-50:]
    print('trim', trim)
    PathRow=trim[3:9] #XXX what is pathrow
    print('path row', PathRow)

    #Calculate proportions year by year, only searching for scenes from the year of interest
    Active_yr=Start_yr
    while Active_yr <= End_yr:
        Year_Interp=[]
        for raster in all_files:
            trim = raster[-50:]
            year = int(trim[16:20])
            print('year',year)
            if year == Active_yr:
                Year_Interp.append(raster)
                
        num_files=len(Year_Interp)
        if num_files>=1: #XXX unnecessary?
            count = 0
            for raster in Year_Interp:
                interp, MaxGeo, shape, interpproj = utils.open_interp(raster, process_dir, max_extent)
                #XXX orignially, interpproj was from last call of maxextent, so see if this works (doesn't make sense that it whould have worked prev)
                if count == 0:
                    # initialize arrays
                    openSW = np.zeros(shape)
                    partialSW = np.zeros(shape)
                    nonwater = np.zeros(shape)
                # reclassify layer and add to previous
                openSW_new, partialSW_new, nonwater_new = utils.reclassify_interp_layer(interp)
                openSW += openSW_new
                partialSW += partialSW_new
                nonwater += nonwater_new

                count += 1
                print(count, "of", num_files, "scenes processed")

                if count == num_files: #XXX unnecessary?
                    break

            if count == num_files: #XXX unnecessary?
                year=str(Active_yr)
                #Identify pixels that contain data
                containsdata= openSW+partialSW+nonwater
                utils.create_output_file(containsdata, 'containsdata', process_dir, PathRow, year, shape, MaxGeo, interpproj)
                #openSW pixels
                utils.create_output_file(openSW, 'openSW', process_dir ,PathRow, year, shape, MaxGeo, interpproj)
                #partialSW pixels
                utils.create_output_file(partialSW, 'partialSW', process_dir, PathRow, year, shape, MaxGeo, interpproj)
                #Non openSW pixels
                utils.create_output_file(nonwater, 'nonwater',process_dir, PathRow, year, shape, MaxGeo, interpproj)
                #Calculate openSW proportion for the year
                openSWproportion = utils.calculate_proportion(openSW, containsdata)
                utils.create_output_file(openSWproportion, 'openSW', prop_dir, PathRow, year, shape, MaxGeo, interpproj)
                #Calculate partialSW proportion for the year
                partialSWproportion = utils.calculate_proportion(partialSW, containsdata)
                utils.create_output_file(partialSWproportion, 'partialSW', prop_dir, PathRow, year, shape, MaxGeo, interpproj)
                print("Proportions completed for year", year)
        Active_yr+=1

########################################################################################

    #Decadal Proportions calculations
    del containsdata, containsdata_output, containsdata_out, openSW_output, openSW_out, partialSW_output, partialSW_out, nonwater_output, nonwater_out, openSWproportion, partialSWproportion, openSW, openSW2, partialSW, partialSW2, nonwater #XXX unnecessary?
    print("Processing semi-decadal proportions")

#TODO copied from above -- make sure this works and can split into 2 different functions (working towards user input time)
#count=0#XXX there are 2 count variables used for different things -- make sure these are actually working
#for folder in paths:
#    count+=1
#    # make output directories
#    wdir, process_dir, prop_dir, dec_prop_dir = utils.make_dirs(main_dir, folder)
    # Create a list to hold our rasters
    #driver = gdal.GetDriverByName("GTiff")
    Active_yr=Start_yr
    Range_yr=Active_yr+4

    os.chdir(process_dir)
    All_Rasters=[]

    openSW_rasters=[]
    partialSW_rasters=[]
    data_rasters=[]

    #Identify previously created reclassified interpreted layers for processing.
    for (dirpath, dirnames, filenames) in os.walk(process_dir):
        print(filenames)
        for filename in filenames:
            All_Rasters.append(filename)
            All_Rasters=[s for s in All_Rasters if s.endswith('tif')]
            openSW_rasters=[s for s in All_Rasters if "openSWsum" in s]
            partialSW_rasters=[s for s in All_Rasters if "partialSWsum" in s]
            data_rasters=[s for s in All_Rasters if "containsdatasum" in s]

    print(Active_yr, "-", Range_yr)
    while Range_yr <= End_yr:
        #Process only the semi-decadal years of interest
        openSW_yr_rasters = utils.years_to_process(openSW_rasters)
        partialSW_yr_rasters = utils.years_to_process(partialSW_rasters)
        data_yr_rasters = utils.years_to_process(data_rasters)

       # Sum each annual raster to create semi-decadal proportions         
        if len(openSW_yr_rasters)>=1:
            openSW = utils.sum_annual_rasters(openSW_yr_rasters, shape)
            partialSW = utils.sum_annual_rasters(partialSW_yr_rasters, shape)
            data = utils.sum_annual_rasters(data_yr_rasters, shape)

            year = [str(Active_yr), str(Range_yr)]
            #Calculate proportions
            openSWproportion = utils.calculate_proportion(openSW, data)
            partialSWproportion = utils.calculateproportion(partialSW, data)
            #Save
            utils.create_output_file(openSWproportion, 'openSW', dec_prop_dir, PathRow, year, shape, MaxGeo, interpproj)
            utils.create_output_file(partialSWproportion, 'partialSW',  dec_prop_dir, PathRow, year, shape, MaxGeo, interpproj)

            #Move on to the next semi-decade
            Active_yr=Range_yr+1
            Range_yr=Active_yr+4
            print(Active_yr, "-", Range_yr)
        else:
            Active_yr=Range_yr+1
            Range_yr=Active_yr+4
            print(Active_yr, "-", Range_yr)
    #End of script
    print("Decadal proportions output")
    #Cleanup
    del partialSW_out, partialSWproportion,openSW_out, openSWproportion, openSWDecPropOut, partialSWDecPropOut
    print("All processing completed")

  
    
    

    
