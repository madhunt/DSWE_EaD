# Applications for the EarthExplorer API

This folder contains applications to use the EarthExplorer API, with an option to use each in the command line or call them in a script.

Future applications can be added here as needed.

## download\_list.py
Download scenes from a given CSV list of scene IDs or product IDs.
```   
usage: download_list.py [-h] [--dataset] [--landsat]
                        (--scene_ids | --product_ids)
                        OUTPUT_DIR CSV_PATH
```
- *Example Usage*

    Download all data from /path/to/mycsv.csv, which contains a column of Landsat scene IDs. Save this data in /path/to/output. The following command would be run in your terminal to do this:
    ``` 
    python3 download_list.py --landsat --scene_ids '/path/to/output' '/path/to/mycsv.csv'
    ```

## download\_search.py
Download all scenes from a search on EarthExplorer. 
```
usage: download_search.py [-h] [--download_code DOWNLOAD_CODE]
                      [--lat LATITUDE] [--long LONGITUDE]
                      [--bbox BBOX] [--months MONTHS]
                      [--start START_DATE] [--end END_DATE]
                      [--unknown_cloud {True,False}]
                      [--min_cloud MIN_CLOUD_COVER]
                      [--max_cloud MAX_CLOUD_COVER]
                      [--max_results MAX_RESULTS]
                      OUTPUT_DIR DATASET
```
- *Example Usage*

    Download search results for DSWE data in Winous Point Marsh, OH (41.4626, -82.9960). Limit results between 1986 and 1996 and the month of June. Only download the first 30 results to /path/to/output. The following command would be run:
    ```
    python3 download_search.py --lat 41.4626 --long -82.9960 --months [6] --start '1986-01-01' --end '1997-01-01' --max_results 30 '/path/to/output' 'SP_TILE_DSWE'
    ```
    Note: If the dataset name is unknown, it can be found using search\_datasets.py.

## search\_datasets.py
Search available datasets on EarthExplorer. By passing no parameters, all available datasets are returned. This can be used to find the dataset name to pass into download\_search.py.
```
usage: search_datasets.py [-h] [--dataset DATASET] [--public]
                          [--lat LATITUDE] [--long LONGITUDE]
                          [--bbox BBOX] [--start START_DATE]
                          [--end END_DATE]
```
- *Example Usage*

    To search for all publicly-available datasets that contain Landsat data between 1970 and 1980, the following command would be run:
    ```
    python3 search_datasets.py --dataset 'landsat' --public --start '1970-01-01' --end '1981-01-01'
    ```
    As of Sept 2020, this should return and print to the screen information about three datasets: ORTHO_MSS_SCENE, MSS_FILM, and RBV_FILM.

## search.py
Search for scenes using the EarthExplorer API.
```
usage: search.py [-h] [--download_code DOWNLOAD_CODE]
             [--lat LATITUDE] [--long LONGITUDE]
             [--bbox BBOX] [--months MONTHS]
             [--start START_DATE] [--end END_DATE]
             [--unknown_cloud {True,False}]
             [--min_cloud MIN_CLOUD_COVER]
             [--max_cloud MAX_CLOUD_COVER]
             [--max_results MAX_RESULTS]
             DATASET
```
- *Example Usage*

    Search DSWE data for the first 50 search results of scenes at Fontana Dam Lake, NC (35.4441, -83.7279) during the months of Sept, Oct, and Nov between 1990 and 2000. Only include scenes with less than 50% cloud cover. To do this, the following command would be run:
    ```
    python3 search.py --lat 35.4441 --long -83.7279 --months [9,10,11] --start '1990-01-01' --end '2001-01-01' --max_cloud 50 --max_results 50 'SP_TILE_DSWE'
    ```
    As of Sept 2020, this should return and print to the screen 43 datasets that meet this criteria.

    Note: If the dataset name is unknown, it can be found using search\_datasets.py.

## untar.py
Untars downloaded data into folders of the same name.
```
usage: untar.py [-h] [--delete_tars] OUTPUT_DIR
```
- *Example Usage*

    To untar all data in /path/to/data, and delete tar files once data is extracted, the following command would be run:
    ```
    python3 untar.py '/path/to/data' --delete_tars
    ```
