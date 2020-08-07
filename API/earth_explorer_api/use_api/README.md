# Use EarthExplorer API

Use the EarthExplorer API in the command line with these files.


## Options and example usage

- `download_list.py` : Download scenes from a given CSV list of scene IDs or product IDs.
    `usage: download_list.py [-h] --scene_ids {True,False} [--dataset {True,False}] [--landsat {True,False}] OUTPUT_DIR CSV_PATH`

    Example usage: Download all data from /path/to/mycsv.csv, which contains a column of Landsat scene IDs. Save this data in /path/to/output. The following command would be run in your terminal to do this: 
        `python3 download_list.py --scene_ids True --landsat True '/path/to/output' '/path/to/mycsv.CSV'`





