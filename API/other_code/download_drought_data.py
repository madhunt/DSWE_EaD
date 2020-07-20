''' 
Function for downloading JSON data from the US Drought Monitor
https://droughtmonitor.unl.edu/
'''

import requests
import json

def download_data(output_file, start_date, end_date, area_of_interest,
                        area=None, statistics_type=None, statistics_format=None,
                        drought_level=None, min_threshold=None, max_threshold=None, min_weeks=None):
    '''
    INPUTS:
        start_date : str : start date in format M/D/YYYY 
        end_date : str : end date in format M/D/YYYY
        area_of_interest : str : national, regional, states, or counties;
        area : str, optional : type of area 
        statistics_type : str, optional : area, percent of area, population, or percent of population
        statistics_format : str, optional : traditional ('1') or categorical ('2')
        drought_level : str, optional : drought level
        min_threshold : str, optional : minimum drought threshold level
        max_threshold : str, optional : maximum drought threshold level
        min_weeks : str, optional : minimum number of weeks in drought
    RETURNS:

    NOTE: for more information on formatting of input strings, 
        go to https://droughtmonitor.unl.edu/WebServiceInfo.aspx
    '''
    #TODO can add a check to make sure date is in M/D/YYYY format

    if statistics_format and statistics_format not in ['1','2']:
        raise Exception('Not a valid statistics format: {statistics_format}. Must choose 1 (traditional) or 2 (categorical).')

    if area == None and statistics_type == None:
        # Weeks in Drought
        area = 'ConsecutiveNonConsecutiveStatistics'
        statistics_type = 'GetNonConsecutiveStatisticsCounty'

        url_mid = f'&dx={drought_level}&minimumweeks={min_weeks}' 
        url_end = ''

    elif min_threshold != None and max_threshold != None:
        # Statistics by Threshold
        url_mid = f'&dx={drought_level}&DxLevelThresholdFrom={min_threshold}&DxLevelThresholdTo={max_threshold}' 
        url_end = f'&statisticsType={statistics_format}'

    else:
        # Comprehensive Statistics
        url_mid = ''
        url_end = f'&statisticsType={statistics_format}' 

    base_url = f'https://usdmdataservices.unl.edu/api/{area}/{statistics_type}?aoi={area_of_interest}'
    url_time = f'&startdate={start_date}&enddate={end_date}'
    endpoint = base_url + url_mid + url_time + url_end


    print(endpoint)

    response = requests.get(endpoint)

    status = response.status_code
    if not status in range(200,299):
        raise Exception(f'Uh oh; status code is: {status}')

    if '.json' not in output_file:
        output_file = output_file.json

    with open(output_file, 'w') as f:
        json.dump(response.json(), f)

    return


#output_file = './myfile.json'

#response = download_json_data(output_file, '1/1/2012', '1/1/2013', 'us',
#                        area='USStatistics', statistics_type='GetDroughtSeverityStatisticsByArea', statistics_format='1',
#                        drought_level=None, min_threshold=None, max_threshold=None, min_weeks=None)

#print(response)
