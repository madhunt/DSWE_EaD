# Proportions over time inundated with water
This code calculates proportions of time that pixels are inundated by open water and partial surface water, or never inundated. It can perform these calculations by year, month, month across all years, season, or for any group of years (decade, etc). The user can choose to perform calculations on interpreted (INTR) or interpreted with mask (INWM) DSWE layers.

Results are given as a TIFF file with pixel values from 0 to 100, corresponding with 0 to 100% of time spent in that state. Pixels with no data will be 255.

The input directory will be recursively searched for valid files, regardless of the subdirectory structure.

The *proportions\_mosaic.py* code also supports stacks of DSWE tiles from different locations, which will be merged into one mosaic. This would be used in the case of a larger study area.


## Code explanation
- **proportions.py**: this is the main code to calculate proportions for one stack of DSWE tiles.

    ```
    usage: proportions.py [-h]
                        [-y NUM_YEARS]
                        DIRECTORY_PATH
                        {INWM,INTR}
                        {year,month,month_across_years,season,multiyear}
    ```

- **proportions\_mosaic.py**: this is the main code to calculate proportions over a large study area, consisting of multiple DSWE tiles. The usage is the same as *proportions.py*, but the directory should contain data from all tiles.

    ```
    usage: proportions_mosaic.py [-h]
                           [-y NUM_YEARS]
                           DIRECTORY_PATH
                           {INWM,INTR}
                           {year,month,month_across_years,season,multiyear}
    ```

- **time\_periods.py**: this file contains functions to group the files based on the time period of interest, and then process the data.

- **utils.py**: this file contains all other utility functions the code uses.


## Example usage
### By month
To run this code for INWM data stored in /path/to/DSWE/data, processing data by month, the following command would be run:

```
python3 proportions.py /path/to/DSWE/data 'INWM' 'month'
```

If /path/to/DSWE/data contains tiles at different locations, the same command would be run, but using *proportions\_mosaic.py* instead:

```
python3 proportions_mosaic.py /path/to/DSWE/data 'INWM' 'month'
```

### By semi-decade
To run this code for INWM data stored in /path/to/DSWE/data, processing data by semi-decade (or groups of 5 years), the following command would be run:

```
python3 proportions.py -y 5 /path/to/DSWE/data 'INWM' 'multiyear'
```

Once again, if /path/to/DSWE/data contains tiles at different locations across a larger study area, the following command would be used:

```
python3 proportions_mosaic.py -y 5 /path/to/DSWE/data 'INWM' 'multiyear'
```

## Recolor output images
The output images from *proportions.py* and *proportions\_mosaic.py* will be greyscale images with pixels from 0 to 100 (and no data as 255). The bash script in *recolor\_output* can be used to recolor them if desired.


## References
- [DSWE User Guide](https://www.usgs.gov/land-resources/nli/landsat/landsat-dynamic-surface-water-extent?qt-science_support_page_related_con=0#qt-science_support_page_related_con)

- The bash script in *recolor\_output* uses [gdaldem](https://gdal.org/programs/gdaldem.html) to set colors.

- The code in [gdal\_merge](https://gdal.org/programs/gdal_merge.html) is used in *proportions\_mosaic.py* to merge a set of images together.
