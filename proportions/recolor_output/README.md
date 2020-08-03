# Recolor output images from proportions code
Since the output images from `proportions.py` are scaled from 0 to 100 (with invalid pixels as 255), the image appears all black in most image viewers. The simple bash script in `recolor.sh` will recolor the output images using the color scheme in a file `col.txt` using gdaldem.

## To use
Copy the colormap of your choice to `col.txt` in the output directory of the processed data, and run `recolor.sh` in that directory (make sure you make it executable). The script will make a new folder called 'recolored\_images', which will contain the recolored images.

## Make a different color scheme
Several color schemes are provided in other text files. Feel free to create your own color scheme in `col.txt`, by listing the pixel value followed by the color.

Supported colors are: white, black, red, green, blue, yellow, magenta, cyan, aqua, grey/gray, orange, brown, purple/violet and indigo. RGB values for colors can be used as well.

## References
- [gdaldem documentation](https://gdal.org/programs/gdaldem.html)



