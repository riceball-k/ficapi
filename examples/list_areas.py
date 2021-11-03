import ficapi

fic = ficapi.FicAPI('./ficapi.ini')
response = fic.request({
    "name": "List Areas",
    "overview": "Get List of Area Information",
    "method": "get",
    "path": "{api_endpoint}/fic-eri/v1/areas",
    "header": {
        "X-Auth-Token": "<token_id>",
        "Content-Type": "application/json"
    }
})

print(f'status = {response}')
print(f'header = {str(response.headers):.65} ...')
print(f'  body = {response.text:.65} ...')
