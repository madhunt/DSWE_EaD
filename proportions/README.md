# Proportions over time inundated with water

This code calculates proportions of time that pixels are inundated by open water and partial surface water, or never inundated. It can perform these calculations by year, month, month across all years, semi-decade, or season. The user can choose to perform calculations on interpreted (INTR) or interpreted with mask (INWM) DSWE layers.

## Code explanation
- `proportions.py`: this is the main code, and can be run with command line arguments in your terminal

    `usage: proportions.py -d <directory> -l <layer> -t <timeperiod>`

- `time_periods.py`: this file contains functions to group the files based on the time period of interest, and then process the data

- `utils.py`: this file contains all other utility functions the code uses

## Recolor output images
Since the output images have pixels on a scale from 0 to 1 (with invalid data as 255), the images will show up as all black in most image viewers. Use the bash script in recolor\_output to recolor them.

## References
- [DSWE User Guide](https://www.usgs.gov/land-resources/nli/landsat/landsat-dynamic-surface-water-extent?qt-science_support_page_related_con=0#qt-science_support_page_related_con)

