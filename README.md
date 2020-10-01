# DSWE\_EaD
Madeline Hunt's work for USGS Dynamic Surface Water Extent (DSWE) internship (from July to Sept 2020), under the direction of Dr. John W. Jones.

## API
Contains code to interface with the EarthExplorer API, along with command-line applications and example scripts to download and search for datasets.

Also contains code to filter downloaded DSWE datasets by the number of valid (non-255) pixels, and code for a few other simple APIs.

## Proportions
Contains code to calulate the proportions of pixels inundated with open or partial surface water over time, given a set of DSWE data. Two scripts are provided to calculate proportions for a stack of tiles in the same location, or tiles spread out across a larger study area.

Also contains a simple bash script to recolor the output images using GDALDEM.

## HLS DSWE
The DSWE algorithm was written in Python, and this code was generalized to take in either Harmonized Landsat-Sentinel (HLS) or Landsat data as inputs.

It will run either without a user-supplied DEM (returning only DSWE layers without masking) or with a user-supplied DEM larger than the study area (returning all DSWE layers with and without masking).

## Questions?
Feel free to email me at madannahunt@gmail.com with any questions, or to request access for another account to view this github. If there are any major bugs, please email me or make them into an issue, and I'll check back periodically to see if there's anything I can fix or explain.

