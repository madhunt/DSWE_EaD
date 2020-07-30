''' 
Script for downloading PRISM climate data
https://prism.oregonstate.edu/
'''
import requests


def download_time_zip(output_file, element, date, chunk_size=128):
    '''
    Download daily, monthly, annual, or historical data
    INPUTS:
        output_file : str : path to and name of zip file
        element : str : type of BIL data requested
        date : str : can request daily data (in the form YYYYMMDD), monthly data (YYYYMM), and annual data (YYYY)
            before 1981, and historical data (YYYY) between 1980 and 1895
        chunk_size : int, optional : used to save data to a file
    RETURNS:
        downloads data in ZIP file format
    '''
    element_options = ['ppt', 'tmin', 'tmax', 'tmean', 'tdmean', 'vpdmin', 'vpdmax']
    if element not in element_options:
        raise Exception(f'{element} is not a valid element option')
    
    # create endpoint url
    endpoint = f'http://services.nacse.org/prism/data/public/4km/{element}/{date}'

    # request data
    response = requests.get(endpoint, stream=True)

    status = response.status_code
    if not status in range(200,299):
        raise Exception(f'Uh oh; status code is: {status}')

    if '.zip' not in output_file:
        output_file = output_file + '.zip'

    print('Downloading data')

    # save data to zip file
    with open(output_file, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

    return


def download_normals_zip(output_file, resolution, element, month):
    '''
    Download normals data
    INPUTS:
        output_file : str : path to and name of zip file; must end in '.zip'
        resolution : str : resolution of data; can be '4km' or '800m'
        element : str : type of BIL data requested
        month : str : monthly (MM, range of 01 to 12) or annually (month=14)
        chunk_size : int, optional : used to save data to a file
    RETURNS:
        downloads data in ZIP file format
    '''
    element_options = ['ppt', 'tmin', 'tmax', 'tmean', 'tdmean', 'vpdmin', 'vpdmax']
    if element not in element_options:
        raise Exception(f'{element} is not a valid element option')
    if resolution not in ['4km','800m']:
        raise Exception(f'{resolution} is not a valid resolution; must be 4km or 800m')

    # create endpoint url
    endpoint = f'http://services.nacse.org/prism/data/public/normals/{resolution}/{element}/{month}'
    
    # request data
    response = requests.get(endpoint, stream=True)

    status = response.status_code
    if not status in range(200,299):
        raise Exception(f'Uh oh; status code is: {status}')

    if '.zip' not in output_file:
        output_file = output_file + '.zip'

    print('Downloading data')

    # save data to zip file
    with open(output_file, 'wb') as fd:
        for chunk in response.iter_content(chunk_size=chunk_size):
            fd.write(chunk)
    
    return


