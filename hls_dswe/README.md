# DSWE code supporting Harmonized Landsat-Sentinel (HLS) input

This code implements the [DSWE algorithm](https://www.usgs.gov/media/files/landsat-dynamic-surface-water-extent-add) in Python. The code was generalized to take in either Harmonized Landsat-Sentinel (HLS) or Landsat data as inputs.

Two options are available to the user: the code can be run without a user-supplied DEM, and will return DSWE results without the mask (the INTR and optional DIAG layers). The user can also choose to supply a DEM (which covers an area larger than the study location), and the code will return all DSWE results (including the INWM and optional MASK, SLOPE, and SHADE layers).


## Usage

### dswe\_without\_mask.py
'''
usage: dswe_without_mask.py [-h] [--include_tests] [--verbose]
                            INPUT_DIRECTORY OUTPUT_DIRECTORY
'''





