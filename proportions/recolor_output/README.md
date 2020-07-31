# Recolor output images from proportions code

Since the output images from `proportions.py` are scaled from 0 to 1 (with invalid pixels as 255), the image appears all black in most image viewers. The simple bash script in `recolor.sh` will recolor the output images using the color scheme in `col.txt`.

## To use
Copy `col.txt` to the output directory from `proportions.py`, and run `recolor.sh` in that directory. The script will make a new folder called 'recolored\_images', which will contain the recolored images.

## Make a different color scheme
Feel free to change to contents of `col.txt`, which lists the pixel value followed by the color, to create your own color scheme.

Supported colors are: white, black, red, green, blue, yellow, magenta, cyan, aqua, grey/gray, orange, brown, purple/violet and indigo. RGB values for colors can be used as well. See [here](https://gdal.org/programs/gdaldem.html) for more information.

## Requirements
Requires GDAL library to use gdaldem.

