# ---------------------------------------------------------------------------
# DSWE_V2_GDAL_Proportions_v1- Jake Shermeyer 4/26/2017
# Calculates annual and semi-decadal proportions of water and mixed vegetation landcover
# for a single path/row.  The path/row folder is specified in the Path_dir line below.
# *** NOTE: This script only works with the new LSRP data with the new naming convention that was deployed in April 2017.


# *****************DEPENDENCIES*******************************************
# Python 2.7 64 bit, will not run on 32 bit Python
# GDAL 2.1+
# numpy 1.12
#
# *****************OUTPUT INFORMATION*****************************
#
# Import modules
import numpy as np
import gdal
import os
import datetime
import glob
import sys

# ***************************REQUIRED PATH/INPUT INFORMATION**************************
# Specify the path for input data. This should be the output folder containing your DSWE output, each contained in their own scene specific subfolder.
# Start year recommended to end with a 0 or 5 regardless of where your data starts.  This is for semi-decadal proportions that will span a 5 year stretch.
# Ensure that your start year is less than the first year of your DSWE output.
Path_dir = '/home/mad/DSWE_EaD/proportions/test_data/20yrspan'
#os.path.join('~', 'DSWE_EaD', 'proportions', 'test_data', 'DSWE_out')
Start_yr = 1985
End_yr = 1995

os.chdir(Path_dir)
paths = glob.glob('*/')
print(paths)
pathcount=len(paths)

print(pathcount)

count=0
for folder in paths:
    count+=1
    working_dir=Path_dir + '/' + folder
    os.chdir(working_dir)

    print(working_dir)

# Output directory paths auto generated.  All will be subfolders in the Path_dir
    processing_dir= working_dir + "/processing"
    proportion_dir= working_dir + "/Proportions"
    decadalproportion_dir=working_dir + "/DecadalProportions"


    #Make directories, if they exist, don't make them!
    if not os.path.exists(processing_dir):
        os.makedirs(processing_dir)

    if not os.path.exists(proportion_dir):
        os.makedirs(proportion_dir)

    if not os.path.exists(decadalproportion_dir):
        os.makedirs(decadalproportion_dir)

    print("directories made")
    print(datetime.datetime.now())

    # Create a list to hold our rasters
    driver = gdal.GetDriverByName("GTiff")
    All_Rasters = []

    for dirpath, dirnames, filenames in os.walk(working_dir):
        for filename in filenames:
            All_Rasters.append(os.path.join(dirpath, filename))
    print('all rasters', All_Rasters)


    #We only want to process the Interp Masked rasters, so we prune our list and make a new list to hold only these rasters
    Interp_Masked=[s for s in All_Rasters if s.endswith('tif')]
    Interp_Masked=[s for s in Interp_Masked if "INWM" in s]
        #[s for s in Interp_Masked if "interp_masked" in s]

    NumRast=len(Interp_Masked)
    print(Interp_Masked)
    print("Processing ",NumRast, " Total Scenes (All Years)")

    #Extent min and max to be overwritten
    M_minx=1000000000000
    M_maxy=-1000000000000
    M_maxx=-1000000000000
    M_miny=1000000000000

    # Loop through rasters in list
    for raster in Interp_Masked:
        interp = gdal.Open(os.path.abspath(raster))
        interpgeo=interp.GetGeoTransform()
        interpproj=interp.GetProjection()
        #Determine the maximum extent of all of our rasters that we are processing, this will be used to ensure no imagery is cropped and extent/georeferencing remains consistent
        minx = interpgeo[0]
        maxy = interpgeo[3]
        maxx = minx + interpgeo[1] * interp.RasterXSize
        miny = maxy + interpgeo[5] * interp.RasterYSize
        Extent= [minx, maxy, maxx, miny]
        if minx < M_minx:
            M_minx=minx
        if maxy > M_maxy:
            M_maxy=maxy
        if maxx > M_maxx:
            M_maxx=maxx
        if miny < M_miny:
            M_miny=miny
        MaxExtent= [M_minx, M_maxy, M_maxx, M_miny]
        
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
                interp = gdal.Open(os.path.abspath(raster))
                print("Opened:", raster)
                interpmaxextent_out= processing_dir + "/interp.tif"
                #Expand every interpreted layer to the maximum extent of all data for the path/row
                interp=gdal.Translate(interpmaxextent_out, interp, projWin = MaxExtent)
                MaxGeo=interp.GetGeoTransform()
                interp=interp.GetRasterBand(1).ReadAsArray()
                shape=interp.shape
                # Reclassify the interpreted layer
                if count == 0:
                    water=interp.copy()
                    water[np.where((water == 255) | (water == 9))] = 0
                    water[np.where((water == 2))] = 1
                    water[np.where((water == 4) | (water == 3))] = 0
                    mixed=interp.copy()
                    mixed[np.where((mixed == 255) | (mixed == 9))] = 0
                    mixed[np.where((mixed == 1) | (mixed == 2) | (mixed == 4))] = 0
                    mixed[np.where((mixed == 3))] = 1
                    nonwater=interp.copy()
                    nonwater[np.where((nonwater == 0))] = 4
                    nonwater[np.where((nonwater == 255)| (nonwater == 9))] = 0
                    nonwater[np.where((nonwater == 1) | (nonwater == 2) | (nonwater == 3))] = 0
                    nonwater[np.where((nonwater == 4))] = 1
                    count += 1
                    print(count, "of", NumRast, "scenes processed")
                # Reclassify the interpreted layer and add it to previously reclassified interpreted layers
                elif count > 0 and count < NumRast:
                    water2=interp.copy()
                    water2[np.where((water2 == 255)| (water2 == 9))] = 0
                    water2[np.where((water2 == 2))] = 1
                    water2[np.where((water2 == 4) | (water2 == 3))] = 0
                    water= water + water2
                    mixed2=interp.copy()
                    mixed2[np.where((mixed2 == 255) | (mixed2 == 9))] = 0
                    mixed2[np.where((mixed2 == 1) | (mixed2 == 2) | (mixed2 == 4))] = 0
                    mixed2[np.where((mixed2 == 3))] = 1
                    mixed=mixed + mixed2
                    nonwater2=interp.copy()
                    nonwater2[np.where((nonwater2 == 0))] = 4
                    nonwater2[np.where((nonwater2 == 255) | (nonwater2 == 9))] = 0
                    nonwater2[np.where((nonwater2 == 1) | (nonwater2 == 2) | (nonwater2 == 3))] = 0
                    nonwater2[np.where((nonwater2 == 4))] = 1
                    nonwater= nonwater + nonwater2
                    count += 1
                    print(count, "of", NumRast, "scenes processed")
            if count == NumRast:
                year=str(Active_yr)
                #Identify pixels that contain data
                containsdata= water+mixed+nonwater
                containsdata_output= processing_dir + "/DSWE_V2_P1_" + PathRow + "_" + year + "_containsdatasum.tif"
                containsdata_out=driver.Create(containsdata_output, shape[1], shape[0], 1, gdal.GDT_Byte)
                containsdata_out.SetGeoTransform(MaxGeo)
                containsdata_out.SetProjection(interpproj)
                containsdata_out.GetRasterBand(1).WriteArray(containsdata)
                #Water pixels
                water_output= processing_dir + "/DSWE_V2_P1_" + PathRow + "_" + year + "_watersum.tif"
                water_out=driver.Create(water_output, shape[1], shape[0], 1, gdal.GDT_Byte)
                water_out.SetGeoTransform(MaxGeo)
                water_out.SetProjection(interpproj)
                water_out.GetRasterBand(1).WriteArray(water)
                #Mixed pixels
                mixed_output= processing_dir + "/DSWE_V2_P1_" + PathRow + "_" + year + "_mixedsum.tif"
                mixed_out=driver.Create(mixed_output, shape[1], shape[0], 1, gdal.GDT_Byte)
                mixed_out.SetGeoTransform(MaxGeo)
                mixed_out.SetProjection(interpproj)
                mixed_out.GetRasterBand(1).WriteArray(mixed)
                #Non Water pixels
                nonwater_output= processing_dir + "/DSWE_V2_P1_" + PathRow + "_" + year + "_nonwatersum.tif"
                nonwater_out=driver.Create(nonwater_output, shape[1], shape[0], 1, gdal.GDT_Byte)
                nonwater_out.SetGeoTransform(MaxGeo)
                nonwater_out.SetProjection(interpproj)
                nonwater_out.GetRasterBand(1).WriteArray(nonwater)
                #Calculate water proportion for the year
                water_output= proportion_dir + "/DSWE_V2_P1_" + PathRow + "_" + year + "_Water_Proportion.tif"
                waterproportion= water/np.float32(containsdata)
                waterproportion=waterproportion * 100
                np.rint(waterproportion)
                water_out=driver.Create(water_output, shape[1], shape[0], 1, gdal.GDT_Byte)
                water_out.SetGeoTransform(MaxGeo)
                water_out.SetProjection(interpproj)
                water_out.GetRasterBand(1).WriteArray(waterproportion)
                #Calculate mixed proportion for the year
                mixed_output= proportion_dir + "/DSWE_V2_P1_" + PathRow + "_" + year + "_Mixed_Proportion.tif"
                mixedproportion= mixed/np.float32(containsdata)
                mixedproportion=mixedproportion * 100
                np.rint(mixedproportion)
                mixed_out=driver.Create(mixed_output, shape[1], shape[0], 1, gdal.GDT_Byte)
                mixed_out.SetGeoTransform(MaxGeo)
                mixed_out.SetProjection(interpproj)
                mixed_out.GetRasterBand(1).WriteArray(mixedproportion)
                print("Proportions completed for year", year        )
        Active_yr+=1

    #Decadal Proportions calculations
    del containsdata, containsdata_output, containsdata_out, water_output, water_out, mixed_output, mixed_out, nonwater_output, nonwater_out, waterproportion, mixedproportion, water, water2, mixed, mixed2, nonwater
    print("Processing semi-decadal proportions")
    Active_yr=Start_yr
    Range_yr=Active_yr+4

    os.chdir(processing_dir)
    All_Rasters=[]

    water_rasters=[]
    mixed_rasters=[]
    data_rasters=[]

    #Identify previously created reclassified interpreted layers for processing.
    for (dirpath, dirnames, filenames) in os.walk(processing_dir):
        print(filenames)
        for filename in filenames:
            All_Rasters.append(filename)
            All_Rasters=[s for s in All_Rasters if s.endswith('tif')]
            water_rasters=[s for s in All_Rasters if "_watersum" in s]
            mixed_rasters=[s for s in All_Rasters if "_mixedsum" in s]
            data_rasters=[s for s in All_Rasters if "containsdatasum" in s]

    print(Active_yr, "-", Range_yr)
    while Range_yr <= End_yr:
        water_yr_rasters=[]
        mixed_yr_rasters=[]
        data_yr_rasters=[]
        #Process only the semi-decadal years of interest
        for raster in water_rasters:
            if int(raster[18:22]) >=Active_yr and int(raster[18:22]) <= Range_yr:
                water_yr_rasters.append(raster)
        for raster in mixed_rasters:
            if int(raster[18:22]) >=Active_yr and int(raster[18:22]) <= Range_yr:
                mixed_yr_rasters.append(raster)
        for raster in data_rasters:
            if int(raster[18:22]) >=Active_yr and int(raster[18:22]) <= Range_yr:
                data_yr_rasters.append(raster)
       # Sum each annual raster to create semi-decadal proportions         
        if len(water_yr_rasters)>=1:
            water=np.zeros(shape)
            mixed=np.zeros(shape)
            data=np.zeros(shape)
            for raster in water_yr_rasters:
                print(raster)
                water2 = gdal.Open(os.path.abspath(raster))
                water2 = water2.GetRasterBand(1).ReadAsArray()
                water=water + water2
            for raster in mixed_yr_rasters:
                mixed2 = gdal.Open(os.path.abspath(raster))
                mixed2 = mixed2.GetRasterBand(1).ReadAsArray()
                mixed=mixed + mixed2
            for raster in data_yr_rasters:
                data2 = gdal.Open(os.path.abspath(raster))
                data2 = data2.GetRasterBand(1).ReadAsArray()
                data=data + data2
            WaterDecPropOut= decadalproportion_dir + "/DSWE_V2_P1_" + PathRow + "_" + str(Active_yr) + "_" + str(Range_yr) + "_Water_Proportion.tif"
            MixedDecPropOut= decadalproportion_dir + "/DSWE_V2_P1_" + PathRow + "_" + str(Active_yr) + "_" + str(Range_yr) + "_Mixed_Proportion.tif"
            #Calculate proportions
            waterproportion= water/np.float32(data)
            waterproportion=waterproportion * 100
            np.rint(waterproportion)
            mixedproportion= mixed/np.float32(data)
            mixedproportion=mixedproportion * 100
            np.rint(mixedproportion)
            #Save
            water_out=driver.Create(WaterDecPropOut, shape[1], shape[0], 1, gdal.GDT_Byte)
            water_out.SetGeoTransform(MaxGeo)
            water_out.SetProjection(interpproj)
            water_out.GetRasterBand(1).WriteArray(waterproportion)
            mixed_out=driver.Create(MixedDecPropOut, shape[1], shape[0], 1, gdal.GDT_Byte)
            mixed_out.SetGeoTransform(MaxGeo)
            mixed_out.SetProjection(interpproj)
            mixed_out.GetRasterBand(1).WriteArray(mixedproportion)
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

  
    
    

    
