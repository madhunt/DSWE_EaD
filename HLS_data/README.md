# Read HLS data as input to DSWE


## Example usage
### Command line
This code can be called from the command line to create a sing TIFF output file with all bands.

```
usage: read_hls.py [-h] [--tiff_output]
                   [--output_dir OUTPUT_DIRECTORY]
                   HDF_FILE_PATH
```

To create a TIFF output file in */path/to/output* from HLS data in */path/to/hdf4_file.hdf*, the following command would be run:

```
python3 read_hls.py --tiff_output --output_dir '/path/to/output' '/path/to/hdf4_file.hdf'
```

### Call in script
This code can also be called within a script. The code will return a dictionary *dswe\_bands* with paths to each band of the input HDF4 file.

```
import read_hls
hdf_file = '/path/to/hdf4_file.hdf'

dswe_bands = read_hls.main(hdf_file, tiff_output=False, output_dir=None)
```

The individual DSWE bands can be called from this dictionary and opened with `gdal.Open()`:

```
blue = dswe_bands['blue']
green = dswe_bands['green']
red = dswe_bands['red']
nir = dswe_bands['nir']
swir1 = dswe_bands['swir1']
swir2 = dswe_bands['swir2']
```
