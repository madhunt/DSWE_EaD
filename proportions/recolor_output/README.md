# Recolor output images
The simple bash script will recolor the output images from *proportions.py* or *proportions_mosaic.py* using gdaldem and the three provided color schemes.

The provided color schemes re-colors images from grey (0% inundations) to either brown, blue, or green for 100% nonwater, partial surface water, and open surface water, respectively.

## Usage
Run *recolor.sh* in the output directory of the processed data (make sure you make it executable on your computer). The script will create a new folder called *recolored\_images*, which will contain the images recolored according to the nonwater, open surface water, and partial surface water colormaps.

## Make a different color scheme
Example color schemes for nonwater, open surface water, and partial surface water images are provided. The list the pixel value followed by the RGB color values. In addition to RGB color values, supported colors are: white, black, red, green, blue, yellow, magenta, cyan, aqua, grey/gray, orange, brown, purple/violet and indigo.

## References
- [gdaldem documentation](https://gdal.org/programs/gdaldem.html)
