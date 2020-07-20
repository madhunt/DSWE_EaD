# Downloading data from other sources

This will be where scripts to download data from other websites will be found. Examples on how to use and run code are in the files named `example_[...]_data.py`. You should only need to change code in these files.


- [US Drought Monitor](https://droughtmonitor.unl.edu/)
    - Edit code in `example_drought_data.py`, which will download data in JSON format. Many of the parameters used to search for datasets can only take specific values, which can be found [here](https://droughtmonitor.unl.edu/WebServiceInfo.aspx).
    - Behind-the-scenes code is in `download_drought_data.py`.

- [PRISM Climate Data](https://prism.oregonstate.edu/)
    - Edit code in `example_prism_data.py`, which will download a zip file of data.
    - Behind-the-scenes code is in `download_prism_data.py`. For more information, check [here](https://prism.oregonstate.edu/documents/PRISM_downloads_web_service.pdf).

