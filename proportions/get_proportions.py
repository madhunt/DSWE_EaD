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
DSWE_layer = 'INWM' #or 'INTR'

#Ultimately, we’d like user input for the compilation period, that is: by month, year, semi-decade, “season”, and within month but across all years!


os.chdir(main_dir)

# make a list of all DSWE files of interest
all_files = []
all_dates = []
# look through all directories and subdirectories (tree)
for dirpath, dirnames, filenames in os.walk(main_dir):
    # find all files in tree
    for filename in filenames:
        # if the file is the layer of interest
        if DSWE_layer in filename:
            all_files.append(os.path.join(dirpath, filename))
            file_date = int(filename[15:23])
            all_dates.append(file_date)

# make output directories
process_dir, prop_dir, dec_prop_dir = utils.make_dirs(main_dir)

num_files = len(all_files)
print(f'Processing {num_files} Total Scenes (All Years)')


# initialize extent to be overwritten 
extent_0 = [1e12, -1e12, -1e12, 1e12]

# loop through all files to calculate max extent
for file in all_files:
    extent_0 = utils.find_max_extent(file, extent_0)
max_extent = extent_0
print("Max Extent calculated")


start_date = min(all_dates) #XXX currently int YYYYMMDD -- may need to change later
end_date = max(all_dates)

##########################################################
# ANNUAL (1 YEAR AT A TIME)

# make list of years
all_years = [int(str(i)[:4]) for i in all_dates]

start_year = min(all_years)
end_year = max(all_years)

for current_year in range(start_year, end_year+1):
    current_files = []
    # make a list of files in the current year of interest
    for i, file in enumerate(all_files):
        file_year = all_years[i]
        if file_year == current_year:
            current_files.append(file)

    # process files in the current year of interest
    for i, file in enumerate(current_files):
        # open the file    
        raster, MaxGeo, shape, rasterproj = utils.open_raster(file, process_dir, max_extent)

        #TODO shape = np.shape(raster) -- remove from func

        if i == 0:
            # initialize arrays
            openSW = np.zeros(shape)
            partialSW = np.zeros(shape)
            nonwater = np.zeros(shape)

        # reclassify layer and add to previous
        openSW_new, partialSW_new, nonwater_new = utils.reclassify(raster)
        openSW += openSW_new
        partialSW += partialSW_new
        nonwater += nonwater_new


    breakpoint()

    # maximum number any given pixel can be
    total_num = len(current_files)
    

    # calculate proportions open and partial surface water
    openSW_prop = utils.calculate_proportion(openSW, total_num)
    partialSW_prop = utils.calculate_proportion(partialSW, total_num)
    nonwater_prop = utils.calculate_proportion(nonwater, total_num)




    # create output files
    utils.create_output_file(openSW, 'openSW', process_dir ,current_year, shape, MaxGeo, rasterproj)
    utils.create_output_file(partialSW, 'partialSW', process_dir, current_year, shape, MaxGeo, rasterproj)
    utils.create_output_file(nonwater, 'nonwater',process_dir, current_year, shape, MaxGeo, rasterproj)
    
    utils.create_output_file(openSW_prop, 'openSW', prop_dir, current_year, shape, MaxGeo, rasterproj)
    utils.create_output_file(partialSW_prop, 'partialSW', prop_dir, current_year, shape, MaxGeo, rasterproj)
    utils.create_output_file(nonwater_prop, 'nonwater', prop_dir, current_year, shape, MaxGeo, rasterproj)
    
    print(f'Proportions completed for {current_year}')


breakpoint()


#Calculate proportions year by year, only searching for scenes from the year of interest


########################################################################################
for folder in paths:

    print(all_files)



    #Decadal Proportions calculations
    del contains_data, contains_data_output, contains_data_out, openSW_output, openSW_out, partialSW_output, partialSW_out, nonwater_output, nonwater_out, openSW_prop, partialSW_prop, openSW, openSW2, partialSW, partialSW2, nonwater #XXX unnecessary?
    print("Processing semi-decadal proportions")

#TODO copied from above -- make sure this works and can split into 2 different functions (working towards user input time)
#count=0#XXX there are 2 count variables used for different things -- make sure these are actually working
#for folder in paths:
#    count+=1
#    # make output directories
#    wdir, process_dir, prop_dir, dec_prop_dir = utils.make_dirs(main_dir, folder)
    # Create a list to hold our files
    #driver = gdal.GetDriverByName("GTiff")
    Active_yr=start_year
    Range_yr=Active_yr+4

    os.chdir(process_dir)
    All_files=[]

    openSW_files=[]
    partialSW_files=[]
    data_files=[]

    #Identify previously created reclassified rasterreted layers for processing.
    for (dirpath, dirnames, filenames) in os.walk(process_dir):
        print(filenames)
        for filename in filenames:
            All_files.append(filename)
            All_files=[s for s in All_files if s.endswith('tif')]
            openSW_files=[s for s in All_files if "openSWsum" in s]
            partialSW_files=[s for s in All_files if "partialSWsum" in s]
            data_files=[s for s in All_files if "contains_datasum" in s]

    print(Active_yr, "-", Range_yr)
    while Range_yr <= end_year:
        #Process only the semi-decadal years of interest
        openSW_yr_files = utils.years_to_process(openSW_files)
        partialSW_yr_files = utils.years_to_process(partialSW_files)
        data_yr_files = utils.years_to_process(data_files)

       # Sum each annual file to create semi-decadal proportions         
        if len(openSW_yr_files)>=1:
            openSW = utils.sum_annual_files(openSW_yr_files, shape)
            partialSW = utils.sum_annual_files(partialSW_yr_files, shape)
            data = utils.sum_annual_files(data_yr_files, shape)

            year = [str(Active_yr), str(Range_yr)]
            #Calculate proportions
            openSW_prop = utils.calculate_proportion(openSW, data)
            partialSW_prop = utils.calculateproportion(partialSW, data)
            #Save
            utils.create_output_file(openSW_prop, 'openSW', dec_prop_dir, year, shape, MaxGeo, rasterproj)
            utils.create_output_file(partialSW_prop, 'partialSW',  dec_prop_dir, year, shape, MaxGeo, rasterproj)

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
    del partialSW_out, partialSW_prop,openSW_out, openSW_prop, openSWDecPropOut, partialSWDecPropOut
    print("All processing completed")

  
    
    

    
