import requests
import json


def check_request(response):
    if response.status_code != 200 and response.status_code != 201:
        raise requests.exceptions.HTTPError(f"HTTP Error: {response.status_code} - {response.text}")
    return response.json()

def get_request(url, headers):
    response = requests.get(url=url, headers=headers)
    return check_request(response=response)

def put_request(url, headers, body):
    response = requests.put(url=url, headers=headers, data=json.dumps(body))
    return check_request(response)

def post_request(url, headers, body):
    response = requests.post(url=url, headers=headers, data=json.dumps(body))
    return check_request(response)