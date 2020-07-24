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

os.chdir(main_dir)
paths = glob.glob('*/')
print(paths)
pathcount=len(paths)

print(pathcount)

count=0
for folder in paths:
    count+=1
    # make output directories
    wdir, process_dir, prop_dir, dec_prop_dir = utils.make_dirs(main_dir, folder)

    # Create a list to hold our rasters
    driver = gdal.GetDriverByName("GTiff")
    All_Rasters = []

    for dirpath, dirnames, filenames in os.walk(wdir):
        for filename in filenames:
            All_Rasters.append(os.path.join(dirpath, filename))
    print('all rasters', All_Rasters)

    
    #TODO make INWM or INTP an input into this script (change reclassify function to match documentation -- no 9s -- but maybe dont have to change anything)

    #We only want to process the Interp Masked rasters, so we prune our list and make a new list to hold only these rasters
    Interp_Masked=[s for s in All_Rasters if s.endswith('tif')]
    Interp_Masked=[s for s in Interp_Masked if "INWM" in s]
        #[s for s in Interp_Masked if "interp_masked" in s]

    NumRast=len(Interp_Masked)
    print(Interp_Masked)
    print("Processing ",NumRast, " Total Scenes (All Years)")

    # initialize extent to be overwritten 
    extent_0 = [1e12, -1e12, -1e12, 1e12]

    # Loop through rasters in list
    for raster in Interp_Masked:
        # calculate max extent
        extent_0 = utils.find_max_extent(raster, extent_0)
    MaxExtent = extent_0
    print("Max Extent calculated")
    # Get Path/Row
    trim = raster[-25:]
    print(trim)
    PathRow=trim[3:9]
    print(PathRow)

    #Calculate proportions year by year, only searching for scenes from the year of interest.
    Active_yr=Start_yr
    while Active_yr <= End_yr:
        Year_Interp=[]
        for raster in Interp_Masked:
            trim = raster[-50:]#raster[-25:]
            year = int(trim[16:20])#int(trim[9:13])
            print('year',year)
            if year == Active_yr:
                Year_Interp.append(raster)
                
        NumRast=len(Year_Interp)
        if NumRast>=1:
            count = 0
            for raster in Year_Interp:
                interp, MaxGeo, shape = utils.open_interp(raster, process_dir, MaxExtent)

                # Reclassify the interpreted layer

                if count == 0:
                    # initialize arrays
                    water = np.zeros(shape)
                    mixed = np.zeros(shape)
                    nonwater = np.zeros(shape)
                water, mixed, nonwater += utils.reclassify_interp_layer(interp)
                count += 1
                print(count, "of", NumRast, "scenes processed")

                if count == NumRast:
                    break

                # Reclassify the interpreted layer and add it to previously reclassified interpreted layers
                #elif count > 0 and count < NumRast:
                    #water2, mixed2, nonwater2 = reclassify_interp_layer(interp)
                    #water += water2
                    #mixed += mixed2
                    #nonwater += nonwater2
            

            if count == NumRast:
                year=str(Active_yr)
                #Identify pixels that contain data
                containsdata= water+mixed+nonwater
                utils.create_output_file(containsdata, 'containsdata', process_dir, PathRow, year, shape, MaxGeo, interpproj)
                #Water pixels
                utils.create_output_file(water, 'water', process_dir ,PathRow, year, shape, MaxGeo, interpproj)
                #Mixed pixels
                utils.create_output_file(mixed, 'mixed', process_dir, PathRow, year, shape, MaxGeo, interpproj)
                #Non Water pixels
                utils.create_output_file(nonwater, 'nonwater',process_dir, PathRow, year, shape, MaxGeo, interpproj)
                
                #Calculate water proportion for the year
                waterproportion = utils.calculate_proportion(water, containsdata)
                utils.create_output_file(waterproportion, 'water', prop_dir, PathRow, year, shape, MaxGeo, interpproj)

                #Calculate mixed proportion for the year
                mixedproportion = utils.calculate_proportion(mixed, containsdata)
                utils.create_output_file(mixedproportion, 'mixed', prop_dir, PathRow, year, shape, MaxGeo, interpproj)
                print("Proportions completed for year", year)
        Active_yr+=1


    #Decadal Proportions calculations
    del containsdata, containsdata_output, containsdata_out, water_output, water_out, mixed_output, mixed_out, nonwater_output, nonwater_out, waterproportion, mixedproportion, water, water2, mixed, mixed2, nonwater
    print("Processing semi-decadal proportions")
    Active_yr=Start_yr
    Range_yr=Active_yr+4

    os.chdir(process_dir)
    All_Rasters=[]

    water_rasters=[]
    mixed_rasters=[]
    data_rasters=[]

    #Identify previously created reclassified interpreted layers for processing.
    for (dirpath, dirnames, filenames) in os.walk(process_dir):
        print(filenames)
        for filename in filenames:
            All_Rasters.append(filename)
            All_Rasters=[s for s in All_Rasters if s.endswith('tif')]
            water_rasters=[s for s in All_Rasters if "watersum" in s]
            mixed_rasters=[s for s in All_Rasters if "mixedsum" in s]
            data_rasters=[s for s in All_Rasters if "containsdatasum" in s]

    print(Active_yr, "-", Range_yr)
    while Range_yr <= End_yr:
        #Process only the semi-decadal years of interest
        water_yr_rasters = utils.years_to_process(water_rasters)
        mixed_yr_rasters = utils.years_to_process(mixed_rasters)
        data_yr_rasters = utils.years_to_process(data_rasters)

       # Sum each annual raster to create semi-decadal proportions         
        if len(water_yr_rasters)>=1:
            water = utils.sum_annual_rasters(water_yr_rasters, shape)
            mixed = utils.sum_annual_rasters(mixed_yr_rasters, shape)
            data = utils.sum_annual_rasters(data_yr_rasters, shape)

            year = [str(Active_yr, str(Range_yr)]
            #Calculate proportions
            waterproportion = utils.calculate_proportion(water, data)
            mixedproportion = utils.calculateproportion(mixed, data)
            #Save
            utils.create_output_file(waterproportion, 'water', dec_prop_dir, PathRow, year, shape, MaxGeo, interpproj)
            utils.create_output_file(mixedproportion, 'mixed',  dec_prop_dir, PathRow, year, shape, MaxGeo, interpproj)

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
    del mixed_out, mixedproportion,water_out, waterproportion, WaterDecPropOut, MixedDecPropOut
    if pathcount==count:
        print("All processing completed")
        exit()

  
    
    

    
