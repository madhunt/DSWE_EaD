'''
Login to the EarthExplorer API using EROS account.
'''
import getpass
import os
import sys
sys.path.insert(1, '../')
import earth_explorer_api as eeapi

def login():
    '''
    Call API and login.
    If environment variables EROS_USERNAME and EROS_PASSWORD exist,
    do not prompt for username and password.
    '''
    # get login information
    username = os.environ.get('EROS_USERNAME','')
    if username == '':
        username = input('EROS Username: ')

    password = os.environ.get('EROS_PASSWORD', '')
    if password == '':
        password = getpass.getpass()
    
    # login to EROS account
    api = eeapi.API(username, password)
    return api
