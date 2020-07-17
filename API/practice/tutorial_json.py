# folowing a short and simplt json tutorial
# https://realpython.com/python-json/

import requests
import json

response = requests.get("https://jsonplaceholder.typicode.com/todos")

#todos = response.json()

todos = json.loads(response.text)

