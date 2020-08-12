# EarthExplorer API

This code is used to interface with the [EarthExplorer API](https://earthexplorer.usgs.gov/) to download and search datasets.

Usage of this code is shown through examples in the `examples` directory. You should only need to modify these examples to download or search datasets.

Note: you should have an EROS account in order to use this API. You can create one [here](https://ers.cr.usgs.gov/register). You should also request machine access to download data [here](https://ers.cr.usgs.gov/profile/access).

## Using the API: Applications
See scripts in applications to download or search for datasets.


## Code explanation
- `earthExplorerAPI.py`: contains a class for working with the API. Functions in this class were created base on those in the documentation (cited below). Large parts of this code were generalized from the [landsatxplore Python package](https://github.com/yannforget/landsatxplore), which uses the EarthExplorer API for landsat data.

- `utils.py`: contains a few data models referenced in the EarthExplorer documentation, which can be found [here](https://earthexplorer.usgs.gov/inventory/documentation/datamodel) (EROS account needed to view)


## EarthExplorer API Documentation
Documentation for the EarthExplorer API can be found [here](https://earthexplorer.usgs.gov/inventory/) (EROS account needed to view)

