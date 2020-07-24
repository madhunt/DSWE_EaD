'''
Utility functions for get_proportions.py
Includes making directories and output files, 
basic calculations, and reclassifying layers.

'''




def make_dirs(main_dir, folder):
    '''
    Creates directories to process data and store results in.
    INPUTS:
        main_dir : str : path to main directory 
            with input data in subfolders
        folder : str : 
    RETURNS:
        wdir : str : path to current working directory 
        process_dir : str : path to processing directory
        prop_dir : str : path to annual proprtions directory
        dec_prop_dir : str : path to semi-decadal proportions directory
    '''
    # move to working directory in current sub-folder
    wdir = os.path.join(main_dir, folder)
    os.chdir(wdir)
    # create output directories (subfolders in main_dir)
    process_dir = os.path.join(wdir, 'processing')
    prop_dir = os.path.join(wdir, 'Proportions')
    dec_prop_dir = os.path.join(wdir, 'DecadalProportions')
    
    os.makedirs(process_dir, exist_ok=True)
    os.makedirs(prop_dir, exist_ok=True)
    os.makedirs(dec_prop_dir, exist_ok=True)
    
    print("directories made")
    print(datetime.datetime.now())
    return wdir, process_dir, prop_dir, dec_prop_dir


def find_max_extent(raster, extent_0):
    '''
    Determine the maximum extent of all rasters;
    ensures that no images are cropped and that 
    extent/georeferencing remains consistent
    INPUTS:
        raster : current raster being processed
        extent_0 : list : initial extent values to be 
            overwritten; in order [minx, maxy, maxx, miny]
    RETURNS:
        extent_0 : list : updated extent values 
    '''
    # calculate extent of current raster
    interp = gdal.Open(os.path.abspath(raster))
    interpgeo=interp.GetGeoTransform()
    interpproj=interp.GetProjection()
    
    minx = interpgeo[0]
    maxy = interpgeo[3]
    maxx = minx + interpgeo[1] * interp.RasterXSize
    miny = maxy + interpgeo[5] * interp.RasterYSize

    # rewrite extent with larger values
    #TODO check if this is correct -- appears to be decreasing every time (finding minimum instead of maximum extent)
    if minx < extent_0[0]:
        extent_0[0] = minx
    if maxy > extent_0[1]:
        extent_0[1]=maxy
    if maxx > extent_0[2]:
        extent_0[2]=maxx
    if miny < extent_0[3]:
        extent_0[3]=miny
    return extent_0


def open_interp(raster, process_dir, MaxExtent):
    interp = gdal.Open(os.path.abspath(raster))
    print("Opened:", raster)
    interpmaxextent_out= process_dir + "/interp.tif"
    #Expand every interpreted layer to the maximum extent of all data for the path/row
    interp=gdal.Translate(interpmaxextent_out, interp, projWin = MaxExtent)
    MaxGeo=interp.GetGeoTransform()
    interp=interp.GetRasterBand(1).ReadAsArray()
    shape=interp.shape
    return interp, MaxGeo, shape


def reclassify_interp_layer(interp):
    interp[np.where((interp_copy==255) | (interp_copy==9))] = 0 # 9=cloud/snow, 255=nodata
        #TODO ask if this is what Dr. Jones meant by 'valid observations' -- are ones with 255 invalid?
        # so are invalid results already accounted for in this line, since this is removed from everything
        # (and thus also from containsdata further down)?
    water=interp.copy()
    water[np.where((water == 2))] = 1
    water[np.where((water == 4) | (water == 3))] = 0
    mixed=interp.copy()
    mixed[np.where((mixed == 1) | (mixed == 2) | (mixed == 4))] = 0
    mixed[np.where((mixed == 3))] = 1
    nonwater=interp.copy()
    nonwater[np.where((nonwater == 0))] = 4
    nonwater[np.where((nonwater == 1) | (nonwater == 2) | (nonwater == 3))] = 0
    nonwater[np.where((nonwater == 4))] = 1
    return water, mixed, nonwater

def create_output_file(data, data_str, output_dir, PathRow, year, shape, MaxGeo, interpproj):
    if 'DecadalProportions' in output_dir:
        data_file = output_dir + "/DSWE_V2_P1_" + PathRow + "_" + year[0] + "_" + year[1] + "_Water_Proportion.tif" 
    elif 'processing' in output_dir:
        data_file = output_dir + "/DSWE_V2_P1_" + PathRow + "_" + year + "_" + data_str + "sum.tif"
    elif 'Proportions' in output_dir:
        data_file = output_dir + "/DSWE_V2_P1_" + PathRow + "_" + year + "_" + data_str + "_Proportion.tif"


    data_out=driver.Create(data_file, shape[1], shape[0], 1, gdal.GDT_Byte)
    data_out.SetGeoTransform(MaxGeo)
    data_out.SetProjection(interpproj)
    data_out.GetRasterBand(1).WriteArray(data)
    return


def calculate_proportion(data, total):
    proportion = data / np.fload32(total) * 100
    np.rint(proportion)
    return proportion




def years_to_process(rasters):
    year_rasters = []
    for raster in rasters:
        raster_year = int(raster[18:22])
        print('CHECK year should be', raster_year)
        if raster_year >= Active_yr and raster_year <= Range_yr:
            year_rasters.append(raster)
    return year_rasters

def sum_annual_rasters(year_rasters, shape):
    data = np.zeros(shape)
    for raster in year_rasters:
        new_data = gdal.Open(os.path.abspath(raster))
        new_data = new_data.GetRasterBand(1).ReadAsArray()
        data += new_data
    return data




