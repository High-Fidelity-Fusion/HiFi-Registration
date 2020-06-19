import json
import os
import requests
import sys


# Official One
url = 'https://api.mjml.io/v1/render'
username = os.getenv('MJML_USERNAME')
password = os.getenv('MJML_PASSWORD')

# Free One
if username is None or password is None:
    url = 'https://mjml.dev'

print("Rendering with:", url)

input_filename = sys.argv[1]
output_filename = sys.argv[2]

with open(input_filename, 'r') as file_open:
    payload = {'mjml': file_open.read()}

r = requests.post(url, json=payload, auth=(username, password))

with open(output_filename, 'w') as file_open:
    file_open.write(r.json()['html'])
