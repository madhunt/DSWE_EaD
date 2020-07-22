'''
Example scripts showing how to download 
statistics by threshold data 
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
STATISTICS BY THRESHOLD
Example: statistics for percent of area in drought for the 
total US between Jan 1 2012 and Jan 1 2013 in 
traditional format, where the min percent of D1 is 10% and 
the max percent is 70%
'''
output_file = 'threshold.json'
start_date = '1/1/2012'
end_date = '1/1/2013'
area_of_interest = 'total'
area = 'USStatistics'
drought_level = '1'
min_threshold = '10'
max_threshold = '70'
statistics_type = 'GetDroughtSeverityStatisticsByAreaPercent' 
statistics_format = '1'

download_data(output_file, start_date, end_date,
                        area_of_interest, 
                        area=area,
                        drought_level=drought_level,
                        min_threshold=min_threshold,
                        max_threshold=max_threshold,
                        statistics_type=statistics_type,
                        statistics_format=statistics_format)


