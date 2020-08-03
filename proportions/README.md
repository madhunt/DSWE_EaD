# Proportions over time inundated with water
This code calculates proportions of time that pixels are inundated by open water and partial surface water, or never inundated. It can perform these calculations by year, month, month across all years, season, or for any group of years (decade, etc). The user can choose to perform calculations on interpreted (INTR) or interpreted with mask (INWM) DSWE layers.

Results are given as a TIFF file with pixel values from 0 to 100, corresponding with 0 to 100% of time spent in that state.

The input directory will be recursively searched for valid files, regardless of the subdirectory structure.

## Code explanation
- `proportions.py`: this is the main code, and can be run with command line arguments in your terminal

    usage: `proportions.py [-h] [-y NUM_YEARS] DIRECTORY_PATH {INWM,INTR} {year,month,month_across_years,season,multiyear}`

- `time_periods.py`: this file contains functions to group the files based on the time period of interest, and then process the data

- `utils.py`: this file contains all other utility functions the code uses

## Example usage
### By month
To run this code for INWM data stored in /path/to/DSWE/data, processing data by month, the following command would be run:
    
    `python3 proportions.py /path/to/DSWE/data 'INWM' 'month'`

### By semi-decade
To run this code for INWM data stored in /path/to/DSWE/data, processing data by semi-decade (or groups of 5 years), the following command would be run:

    `python3 proportions.py -y 5 /path/to/DSWE/data 'INWM' 'multiyear'`

## Recolor output images
Since the output images have pixels on a scale from 0 to 100 (with invalid data as 255), the images will show up as all black in most image viewers. Use the bash script in recolor\_output to recolor them.

## References
- [DSWE User Guide](https://www.usgs.gov/land-resources/nli/landsat/landsat-dynamic-surface-water-extent?qt-science_support_page_related_con=0#qt-science_support_page_related_con)

- [Recoloring output with gdaldem](https://gdal.org/programs/gdaldem.html)

