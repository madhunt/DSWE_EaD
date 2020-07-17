# this is a translation of the EarthExplorer API example client given in perl to python

import requests
import json


#TODO follow stackoverflow to make this into a class https://stackoverflow.com/questions/20429516/translating-perl-to-python-what-does-this-line-do-class-variable-confusion
def new(username, password, authType, endpoint, catalogId, customUserAgent=None):
    #TODO somethign with shift
    self = [] #TODO is this even correct

    validateCatalog(catalogId) #TODO a func to write later

    status = status() #TODO a func to write later

    apiVersion = status[api_version] # this is a dict in python, hash map in perl

    if apiVersion == compatibleVersion:
        raise Exception(f"API Version {api_version} is not compatible with this library {compatibleVersion}")
    
    userAgent = ""

    return



def get_status():
    response = requests.get(status, None, 0)

    status = response[data]

    status[api_version] = response[api_version]

    #FIXME these might be . instead of [] depending on output

    return status


def validate_catalog(catalogID):
    if not catalogID or catalogID == None:
        raise Exception('A catalogID value is required')
    
    catalog_array = ['CWIC', 'EE', 'GLOVIS', 'HDDS', 'LPCS']

    if catalogID not in catalog_array:
        raise Exception('Invalid catalogID value')

    return

def validate_coordinate(coordinate):
    finalCoord = {'latitude': None, 'longitude': None}

    if coordinate['latitude'] == None:
       raise Exception('Coordinate is missing latitude property') 
    elif not isinstance(coordinate['latitude'], (int, float)):
        raise Exception('Latitude value must be numeric')
        #NOTE: this could be an issue, not sure if I need to include other python types here
    else:
        latitude = coordinate['latitude']

        if latitude < -90 or latitude > 90:
            raise Exception('Latitude value must be between -90 and 90')
        finalCoord['latitude'] = latitude

    if coordinate['longitude'] == None:
        raise Exception('Coordinate is missing longitude property')
    elif not isinstance(coordinate['longitude'], (int, float)):
        raise Exception('Longitude value must be numeric')
    else:
        longitude = coordinate['longitude']

        if longitude < -180 or longitude > 180:
            raise Exception('Longitude value must be between -180 and 180')
        finalCoord['longitude'] = longitude

    return finalCoord

def validate_date(time):
    #FIXME how to do regex in python??
    if time =! :
        raise Exception('Date should be in format YYYY-MM-DD')
    return time





