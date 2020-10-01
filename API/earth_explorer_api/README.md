# EarthExplorer API

This code is used to interface with the [EarthExplorer API](https://earthexplorer.usgs.gov/) to download and search available datasets.

Note: you should have an EROS account in order to use this API. You can create one [here](https://ers.cr.usgs.gov/register). You should also request machine access to download data [here](https://ers.cr.usgs.gov/profile/access).

## Using the API: Applications
Various applications to download or search for datasets are provided in the applications folder. These applications can all be used in the command line, or called in scripts (see examples folder) if needed.

## Code explanation
- `earth_explorer_api.py`: Contains a class for working with the API. Functions in this class were created based on those in the documentation (cited below). Large parts of this code were also generalized from the [landsatxplore Python package](https://github.com/yannforget/landsatxplore), which uses the EarthExplorer API for Landsat data.

- `utils_api.py`: Contains a few data models referenced in the EarthExplorer documentation, which can be found [here](https://earthexplorer.usgs.gov/inventory/documentation/datamodel) (EROS account needed to view).

## EarthExplorer API Documentation
Documentation for the EarthExplorer API can be found [here](https://earthexplorer.usgs.gov/inventory/) (EROS account needed to view).

