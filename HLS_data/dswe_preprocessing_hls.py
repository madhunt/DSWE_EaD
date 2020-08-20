#################
# unzip function --
#     Unzip tar.gz file, put in a folder.
# dem_slp_hillshade function --
#     Read in the first image to get the extent
#     clip the DEM to Landsat image
#     get solar geometry from .xml file 
#     calculate the % slope and hillshade
# ??? needs to install gdal.Translate and gdal.DEMprocessing functions ?????
#################
# python DSWE_preprocessing.py --input_file=/disks/igskaecgus86241/disk2/DSWE/p026r029/tiff_zip/LC80260292014207-SC20160122142319.tar --output_dir=/disks/igskaecgus86241/disk2/DSWE/p026r029/tiff_zip/LC80260292014207-SC20160122142319/
    
import os
import time
import numpy as np # just use .shape and get rid of this import
import gdal
import datetime
import glob
import sys
import tarfile  # extract data from .tar achives
import shutil   # file copy/move/delete operations
import argparse # for command line aruguments
import getopt 

from lxml import etree

########
# unzip an archive of landsat bands
########
def unzip_landsat(in_file, out_dir):
    print "Unzipping", in_file, "to", out_dir

    if not os.path.exists(in_file):
        print 'Could not find ' + in_file
        return(False)

    #if not os.path.exists(out_dir):
    #    print 'Creating ' + out_dir
    #    os.makedirs( os.path.dirname(out_dir) )

    tar = tarfile.open(in_file, mode='r:gz')
    tar_members = tar.getmembers()

    tar.extractall(out_dir)
    
#######
# create dem, % slope and hillshade tiff files for later use
#######
def dem_slp_hillshade(gz_folder, dem, slp):
    ## filenames for processed dem, slope and hillshade
    dst_dem = gz_folder + "/" + "DEM.tif"
    dst_slp = gz_folder + "/" + "perslp.tif"
    dst_hshd = gz_folder + "/" + "hillshade.tif"

    ## read in the first tif to crop the dem
    file_list = glob.glob1(gz_folder, "*.tif")
    print file_list, gz_folder

    first_file_ds = gdal.Open(gz_folder + "/" + file_list[0])

    ## grab image size and projection info
    nCol = first_file_ds.RasterXSize
    nRow = first_file_ds.RasterYSize + 1

    # coordinates are for top-left corners of pixels
    geotrans = first_file_ds.GetGeoTransform()    
    
    # clip with geotrans from first Landsat band
    minx = geotrans[0]
    maxy = geotrans[3]
    maxx = minx + geotrans[1] * nCol
    miny = maxy + geotrans[5] * nRow
    
    # open the big DEM and percent slope
    src_dem = gdal.Open(dem)
    src_slp = gdal.Open(slp)

    ##Clip our slope and hillshade mask to the image (have to do this for each image due to the variable extents of each image)
    GeoClip= [minx, maxy, maxx, miny]
    print GeoClip
    print "clipping DEM..."
    dem_clip = gdal.Translate(dst_dem, src_dem, projWin = GeoClip)
    
    print "calculating slope..."
    slp_clip = gdal.Translate(dst_slp, src_slp, projWin = GeoClip)
    #perslp = gdal.DEMProcessing(dst_slp, dem_clip, 'slope', slopeFormat = 'percent', format = 'GTiff')

    # close open datasets
    src_dem = None
    src_slp = None
    dem_clip = None
    slp_clip = None
    
    ## get solar geometry
    print "Getting metadata ..."
    Metadata = glob.glob1(gz_folder, "*.xml")
    xmldoc = etree.parse(gz_folder + "/" + Metadata[0])
    root = xmldoc.getroot()
    SunAngleData=str(root[0][6].attrib)
    charlist="':}{,"
    for char in charlist:
        SunAngleData=SunAngleData.replace(char,"")
    SunAngleList=SunAngleData.split()
    Zen= float(SunAngleList[3])
    Az= float(SunAngleList[5])
    Az = int(Az)
    Alt= float(90 - Zen)
    print Alt
    print Az
    
    ## calculate hillshade
    print "calculate hillshade ..."
    #HillshadeOut="hillshade_mask" + "_%s.tif"%"_".join(raster.split('_'))[0:length]
    #Hoping the altitude issue is repaired shortly, will be an easy fix once it is corrected
    #Hillshade = gdal.DEMProcessing('hillshade.tif', DEM, 'hillshade', format = 'GTiff', azimuth = Az, altitude=Alt)
    dst_dem_ds = gdal.Open(dst_dem)
    geotrans = dst_dem_ds.GetGeoTransform()
    prj = dst_dem_ds.GetProjectionRef()
    hlshd_ds = gdal.DEMProcessing(dst_hshd, dst_dem_ds, 'hillshade', format = 'GTiff', azimuth = Az) # this fails on linux :(
    hlshd_band = hlshd_ds.GetRasterBand(1)
    hlshd_data = hlshd_band.ReadAsArray()
    
    # save the hillshade
    nrows,ncols = np.shape(hlshd_data)
    driver = gdal.GetDriverByName("GTiff")
    dst_hlshd = driver.Create(dst_hshd, ncols, nrows, 1, gdal.GDT_Byte)
    dst_hlshd.SetGeoTransform( geotrans )
    dst_hlshd.SetProjection( prj )
    hlsh_band = dst_hlshd.GetRasterBand(1)       
    hlsh_band.WriteArray( hlshd_data )
    hlsh_band.SetNoDataValue(255)
    hlsh_band = None
    dst_hlshd.FlushCache()
    dst_hlshd = None    
    dst_dem_ds = None
    
    
def main(input_file, output_dir, dem, slp):
    start_time = time.time()
    print(f'Preprocessing {input_file}')
    
    unzip_landsat(input_file, output_dir)

    #TODO add option to specify HLS data instead of zipped landsat

    dem_slp_hillshade(output_dir, dem, slp)
    
    preproc_time = round(time.time() - start_time / 60, 0)
    print('Preprocessing time: {preproc_time} min')

    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')

    parser.add_argument('input_file',
            metavar='INPUT_FILE.ZIP',
            type=str,
            help='input Landsat tar.gz file')
    parser.add_argument('output_dir',
            metavar='OUTPUT_DIR',
            type=str,
            help='output directory for Landsat geotiffs, metadata, and elevation model')
    parser.add_argument('dem',
            metavar='DEM_DIR',
            type=str,
            help='path to US DEM file')
    parser.add_argument('slp',
            metavar='SLOPE_FILE',
            type=str,
            help='path to slope TIF file')
    
    args = parser.parse_args()

    main(**vars(args))

