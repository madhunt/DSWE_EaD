'''
Example to download PRISM climate data 
normals as a zip file.

More information on the parameters required 
can be found at:
https://prism.oregonstate.edu/documents/PRISM_downloads_web_service.pdf
'''
# if code is in directory below download_prism_data.py:
import sys
sys.path.insert(1, '../')

from download_prism_data import download_normals_zip

# assign parameters
output_file = 'mynormals.zip'
resolution = '800m'
element = 'tmin'
month = '03' # to download normal grid for March
#month = '14' # to download annual normal grid

# call function to download data
download_normals_zip(output_file, resolution, element, month)


