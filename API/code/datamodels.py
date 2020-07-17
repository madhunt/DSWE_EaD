'''

'''


def coordinate(latitude, longitude):
    '''

    '''

    coordinate = {'latitude': latitude,
                    'longitude': longitude}
    return coordinate


def spatial_filter(xmin, ymin, xmax=None, ymax=None):
    '''

    '''
    if not xmax and not ymax:
        # arbitrarially define bounds
        xmax = xmin + 0.1
        ymax = ymin + 0.1
    lower_left = coordinate(xmin, ymin)
    upper_right = coordinate(xmax, ymax)

    spatial_filter = {'filterType': 'mbr',
                        'lowerLeft': lower_left,
                        'upperRight': upper_right}

    return spatial_filter


def temporal_filter(start_date, end_date=None):
    '''

    '''
    if not end_date:
        end_date = start_date

    temporal_filter = {'startDate': start_date,
                        'endDate': end_date}
    
    return temporal_filter





