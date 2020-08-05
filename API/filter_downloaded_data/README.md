# Filter downloaded DSWE data

This code can be used to filter out DWSE datasets that have less than a certain percentage of valid data (that is, pixels that are not 255). The EarthExplorer API will return datasets for a search even if only a small percentage of the tile surrounds the specified lat/long. This means that some downloaded datasets might be unusable for analysis, as they are mostly unusable data.

## Using the code

Once DSWE data has been downloaded using the EarthExplorer API, this code can be used to sort the existing data into 'good' and 'bad' categories, depending on the percentage of valid data in each file.

    `usage: filter_valid_data.py [-h] DIRECTORY_PATH PERCENT`

For example, if the DSWE data is in the folder /path/to/data, and only files with 80% or more valid data want to be used, the following command would be run:

    `python3 filter_valid_data.py '/path/to/data' 80`

