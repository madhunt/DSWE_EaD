'''
Example scripts showing how to download data 
from the US Drought Monitor:
https://droughtmonitor.unl.edu/

For a full list of posssible values for parameters, go to:
https://droughtmonitor.unl.edu/WebServiceInfo.aspx
'''
from request_drought_data import download_data

'''
COMPREHENSIVE STATISTICS
Example: statistics for total area in drought for both the 
continental US and the total US between Jan 1 2012 and 
Jan 1 2013 in traditional format; for a full list of values,
go to:
https://droughtmonitor.unl.edu/WebServiceInfo.aspx
'''
output_file = 'comprehensive.json'
start_date = '1/1/2012'
end_date = '1/1/2013'
area_of_interest = 'us'
area = 'USStatistics'
statistics_type = 'GetDroughtSeverityStatisticsByArea'
statistics_format = '1'

response = download_data(output_file, start_date, end_date,
                        area_of_interest, 
                        area=area,
                        statistics_type=statistics_type, 
                        statistics_format=statistics_format)

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

response = download_data(output_file, start_date, end_date,
                        area_of_interest, 
                        area=area,
                        drought_level=drought_level,
                        min_threshold=min_threshold,
                        max_threshold=max_threshold,
                        statistics_type=statistics_type,
                        statistics_format=statistics_format)

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

response = download_data(output_file, start_date, end_date,
                        area_of_interest,
                        drought_level=drought_level,
                        min_weeks=min_weeks)

