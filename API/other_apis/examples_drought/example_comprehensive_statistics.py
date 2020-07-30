'''
Example script showing how to download 
comprehensive statistics data 
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
COMPREHENSIVE STATISTICS
Example: statistics for total area in drought for both the 
continental US and the total US between Jan 1 2012 and 
Jan 1 2013 in traditional format
'''
output_file = 'comprehensive.json'
start_date = '1/1/2012'
end_date = '1/1/2013'
area_of_interest = 'us'
area = 'USStatistics'
statistics_type = 'GetDroughtSeverityStatisticsByArea'
statistics_format = '1'

download_data(output_file, start_date, end_date,
                        area_of_interest, 
                        area=area,
                        statistics_type=statistics_type, 
                        statistics_format=statistics_format)


