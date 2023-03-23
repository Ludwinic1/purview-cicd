import requests


# Acquire an access token
def get_access_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    url = f'https://login.microsoftonline.com/{tenant_id}/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "resource": "https://purview.azure.net"
    }
    access_token_request = requests.get(url=url, headers=headers, data=data)
    return access_token_request.json()['access_token']