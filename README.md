<!-- omit in toc -->
# Flexible InterConnect API Access Module

## Introduction

This module is a Python library that provides API access functions for Flexible InterConnect, a network service of NTT Communications.

It has functions to automatically acquire a authentication token (reuse it within the expiration date, and reacquire when expire), API access with parameters from JSON files or DICT, and the ability to specify resource IDs by resource name.

## How to Install

This package has not been registered with PyPI. Therefore, you need to clone it from GitHub, run `setup.py` to create the package, and then install it.

```powershell
> git clone https://github.com/riceball-k/ficapi
> cd ficapi
> py setup.py sdist
> py -m pip install dist\ficapi-x.x.x.tar.gz
```

## Example

- First, login to the FIC Portal and get the following credentials.
  - api kye
  - api secret
  - tenant id
- Then create `ficapi.ini` in the current directory. (execute `create_ficapi_ini.exe`)

**Source code**:

```python
import ficapi

fic = ficapi.FicAPI('./ficapi.ini')
response = fic.request('param.json')

print(f'status = {response}')
print(f'header = {str(response.headers):.65} ...')
print(f'  body = {response.text:.65} ...')
```

**Parameter File (JSON Format)**:

`param.json`:

```json
{
    "name": "List Areas",
    "overview": "Get List of Area Information",
    "method": "get",
    "path": "{api_endpoint}/fic-eri/v1/areas",
    "header": {
        "X-Auth-Token": "<token_id>",
        "Content-Type": "application/json"
    }
}
```

**Result**:

```text
input password: 
       confirm: 
status = <Response [200]>
header = {'Date': 'Wed, 03 Nov 2021 02:32:49 GMT', 'Content-Type': 'applic ...
  body = {"areas":[{"id":"8227d19719eb49d1a7fd47b12d142864","name":"JPWEST ...
```
