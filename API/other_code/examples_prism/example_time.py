'''
Example to download PRISM climate data by 
time (daily, monthly, annual, or historical) 
as a zip file.

More information on the parameters required 
can be found at:
https://prism.oregonstate.edu/documents/PRISM_downloads_web_service.pdf
'''
# if code is in directory below download_prism_data.py:
import sys
sys.path.insert(1, '../')

from download_prism_data import download_time_zip

# assign parameters
output_file = 'mydata.zip'
element = 'tmin'
date = '20090405' # to request daily data
#date = '200904' # to request montly data
#date = '2009' # to request annual data
#date = '1944' # to request historical monthly data

# call function to download data
download_time_zip(output_file, element, date)


