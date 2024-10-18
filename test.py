import requests

response = requests.get('http://140.112.251.50:5000/ping')

print(response.text)