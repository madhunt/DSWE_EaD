'''
'''

import numpy as np
import gdal
import os
import datetime
import glob
import sys
from dateutil import rrule

import proportions_utils as utils

main_dir = '/home/mad/DSWE_EaD/proportions/test_data/20yrspan_take2'
DSWE_layer = 'INWM' #or 'INTR'



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
            file_date = utils.get_file_date(filename)
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



# ANNUAL (1 YEAR AT A TIME)
def process_yearly(all_files, all_dates):
    '''
    Process files yearly
    '''
    all_years = [i.year for i in all_dates]
    start_year = min(all_years)
    end_year = max(all_years)

    for current_time in range(start_year, end_year+1):
        current_files = []
        # make a list of files in the current year of interest
        for i, file in enumerate(all_files):
            file_time = all_years[i]
            if file_time == current_time:
                current_files.append(file)

        # process files in current year of interest
        process_files()
        #TODO add function call here

        print(f'Proportions completed for {current_year}')

    return

### MONTHLY (1 MONTH AT A TIME)
def process_monthly(all_files, all_dates):
    '''
    Process files monthly
    '''
    start_date = datetime.date(min(all_dates).year, 1, 1)
    end_date = datetime.date(max(all_dates).year+1, 1, 1)

    for current_time in rrule.rrule(rrule.MONTHLY, 
            dtstart=start_date, until=end_date):
        current_files = []
        # make a list of files in the current month of interest
        for i, file in enumerate(all_files):
            file_time = all_dates[i]
            if (file_time.month == current_time.month and
                    file_time.year == current_time.year):
                current_files.append(file)

        # process files in current year of interest
        process_files()
        #TODO add function call here

        print(f'Proportions completed for month 
                {current_time.month} in {current_time.year}')

    return


### ACROSS ALL MONTHS FOR ALL YEARS
def process_allmonth_across_allyears(all_files, all_dates):
    '''
    Process files across all months for all years 
    '''
    all_months = [i.month for i in all_dates] 
    start_month = min(all_months)
    end_month = max(all_months)

    for current_time in range(start_month, end_month+1):
        current_files = []
        # make a list of files in the current month of interest
        for i, file in enumerate(all_files):
            file_time = all_months[i]
            if file_time == current_time:
                current_files.append(file)
        
        # process files in current year of interest
        process_files()
        #TODO add function call here

        print(f'Proportions completed for month 
                {current_time.month}')
    return   

## SEMI DECADAL
def process_semidecadally(all_files, all_dates):
    '''
    Process files semi-decadally (every 5 years)
    '''
    all_years = [i.year for i in all_dates]
    start_year = min(all_years)
    end_year = max(all_years)

    for current_time in range(start_year, end_year+5, 5):
        current_files = []
        # make a list of files in the current semi-decade
            # of interest
        for i, file in enumerate(all_files):
            file_time = all_years[i]
            if (file_time - file_time%5) == current_time:
                current_files.append(file)

        # process files in current year of interest
        process_files()
        #TODO add function call here

        print(f'Proportions completed for month 
                {current_time.month}')
    return

#### SEASONAL
def process_seasonally():
    '''
    Process files seasonally.
    Seasons defined meteorologically:
        N. Hemisphere | S. Hemisphere | Start Date
        Winter        | Summer        | 1 Dec
        Spring        | Autumn        | 1 March
        Summer        | Winter        | 1 June
        Autumn        | Spring        | 1 Sept
        
    '''
    all_months = [i.month for i in all_dates] 

    # 0=winter, 1=spring, 2=summer, 3=fall
    for current_time in range(0, 4):
        current_files = []

        for i, file in enumerate(all_files):
            file_time = np.floor(all_months[i]/3 %4)
            if file_time == current_time:
                current_files.append(file)
                print(file_time)

        # process files in current year of interest
        process_files()
        #TODO add function call here

        print(f'Proportions completed for month 
                {current_time.month}')
    return






def process_files(current_files, process_dir, prop_dir, 
        max_extent):
    '''
    Process files in the current time period of interest
    '''
    for i, file in enumerate(current_files):
        # open the file    
        raster, MaxGeo, rasterproj = utils.open_raster(
                file, process_dir, max_extent)

        if i == 0:
            shape = raster.shape #XXX or np.shape(raster) ?
            # initialize arrays
            openSW = np.zeros(shape)
            partialSW = np.zeros(shape)
            nonwater = np.zeros(shape)

        # reclassify layer and add to previous
        openSW_new, partialSW_new, nonwater_new = utils.reclassify(raster)
        openSW += openSW_new
        partialSW += partialSW_new
        nonwater += nonwater_new

    # maximum number any given pixel can be
    total_num = len(current_files)
    

    # calculate proportions open and partial surface water
    openSW_prop = utils.calculate_proportion(openSW, total_num)
    partialSW_prop = utils.calculate_proportion(partialSW, total_num)
    nonwater_prop = utils.calculate_proportion(nonwater, total_num)

    #TODO MaxGeo is created in for loop above, so the input to these functions would be the LAST MaxGeo -- is this correct?????
    #TODO same for rasterproj
    
################# code up to here is great!!

    # create output files
    reclass_data = [openSW, partialSW, nonwater]
    prop_data = [openSW_prop, partialSW_prop, nonwater_prop]
    data_str = ['openSW', 'partialSW', 'nonwater']

    for i, data in enumerate(reclass_data):
        utils.create_output_file(data, data_str[i],
                process_dir, current_year, 
                MaxGeo, rasterproj)
    for i, data in enumerate(prop_data):
        utils.create_output_file(data, data_str[i],
                prop_dir, current_year,
                MaxGeo, rasterproj)

    return

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

  
    
    

    
