# DSWE code supporting Harmonized Landsat-Sentinel (HLS) input

This code implements the [DSWE algorithm](https://www.usgs.gov/media/files/landsat-dynamic-surface-water-extent-add) in Python. The code was generalized to take in either Harmonized Landsat-Sentinel (HLS) or Landsat data as inputs.

Two options are available to the user: the code can be run without a user-supplied DEM, and will return DSWE results without the mask (the INTR and optional DIAG layers). The user can also choose to supply a DEM (which covers an area larger than the study location), and the code will return all DSWE results (including the INWM and optional MASK, SLOPE, and SHADE layers).


## Usage
To use the DSWE code, you must provide an input directory that contains HLS data in HDF4 format or Landsat data in TAR format. The --include\_tests option can be flagged to save the DIAG layer to disk.

If the --dem option is not flagged, the code will calculate only the INTR and optional DIAG DSWE layers. However, the user may provide a path to a DEM TIF file with the --dem option. The DEM must be larger than and contain the study area. If this option is used, the code will also calculate the masked DSWE layers.

If a DEM is provided, the --include\_ps and --include\_hs options can be used to save the SLOPE and SHADE layers to disk. The --use\_zeven\_thorne option can be used to change the percent slope calculation algorithm.

'''
usage: dswe.py [-h] [--dem DEM_PATH] [--include_tests]
               [--include_ps] [--include_hs]
               [--use_zeven_thorne]
               [--verbose]
               INPUT_DIRECTORY OUTPUT_DIRECTORY
'''

The output of this code can be fed directly as an input into the proportions code.




