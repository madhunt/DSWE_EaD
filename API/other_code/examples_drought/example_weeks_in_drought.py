'''
Example scripts showing how to download 
weeks in drought data 
from the US Drought Monitor:
https://droughtmonitor.unl.edu/

For a full list of posssible values for parameters, go to:
https://droughtmonitor.unl.edu/WebServiceInfo.aspx
'''
# if code is in directory below download_drought_data.py:
import sys
sys.path.insert(1, '../')

from download_drought_data import download_data

'''
WEEKS IN DROUGHT
Example: counties in Nebraska that were in drought for at 
least 4 weeks (not necessarially consecutively) between 
Jan 1 2012 and Jan 1 2013
'''
output_file = 'weeks.json'
start_date = '1/1/2012'
end_date = '1/1/2013'
area_of_interest = 'NE'
drought_level = '0'
min_weeks = '4'

download_data(output_file, start_date, end_date,
                        area_of_interest,
                        drought_level=drought_level,
                        min_weeks=min_weeks)

