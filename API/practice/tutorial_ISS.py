# example tutorial to get data about the ISS using the Open Notify API
# https://www.dataquest.io/blog/python-api-tutorial/

# GET request = gets data/info
# API endpoint = server route to retrieve different data from the API (just add to base URL of the API)


import requests # for working with APIs
import json # for working with JSON data

# use the "iss-now.json" endpoint to get current position of the ISS
response = requests.get("http://api.open-notify.org/iss-now.json")
# print status code of response (see tutorial for more explanation of status codes)
print(response.status_code) # 200 = success

# now use "iss-pass.json" endpoint (http://open-notify.org/Open-Notify-API/ISS-Pass-Times/)
# this requires 2 parameters (lat, lon) and has 2 optional parameters (alt, n) 
parameters = {'lat': 35.78, "lon": -78.64} # lat/lon of Raleigh, NC
response = requests.get("http://api.open-notify.org/iss-pass.json", params=parameters)

# JSON: JavaScript Object Notation; encode data structures into strings (readable by other machines)
# json library converts python object to string (DUMPS) or converts JSON string to python object (LOADS)

data = response.json()
print(type(data)) # should be a dictionary (python object) using .json() method
print(data)

# server sends status code, data, AND metadata as headers
# within the headers, content-type tells the format of response and how to decode it
# for this API, the format is JSON (which is why we could use the json package to decode it previously)
print(response.headers)
print(response.headers['content-type'])

# use astros.json endpoint to find how many people are currently in space
response = requests.get("http://api.open-notify.org/astros.json")
data = response.json()

print(data)
print(data['number'])


