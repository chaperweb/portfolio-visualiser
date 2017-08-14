import requests
import uuid
import json
from portfolio_manager.importer import from_data_array

graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'

# Function that makes api calls to given url
def make_api_call(method, url, token, user_email, payload=None, parameters=None):
    headers = {
        'User-Agent': 'portfolio_manager/1.0',
        'Authorization': 'Bearer {}'.format(token),
        'Accept': 'application/json',
        'X-AnchorMailbox': user_email
    }

    request_id = str(uuid.uuid4())
    instrumentation = {
        'client-request-id': request_id,
        'return-client-request-id': 'true'
    }
    headers.update(instrumentation)

    response = None

    if (method.upper() == 'GET'):
        response = requests.get(url, headers=headers, params=parameters)
    elif (method.upper() == 'DELETE'):
        response = requests.delete(url, headers=headers, params=parameters)
    elif (method.upper() == 'PATCH'):
        headers.update({'Content-Type': 'application/json'})
        response = requests.patch(url, headers=headers, data=json.dumps(payload), params=parameters)
    elif (method.upper() == 'POST'):
        headers.update({'Content-Type': 'application/json'})
        response = requests.post(url, headers=headers, data=json.dumps(payload), params=parameters)

    return response


# Gets the microsoft user via API
def get_me(access_token):
    get_me_url = graph_endpoint.format('/me')
    query_parameters = {'$select': 'displayName,mail'}

    r = make_api_call('GET', get_me_url, access_token, '', parameters=query_parameters)

    if (r.status_code == requests.codes.ok):
        return r.json()
    else:
        return '{0}: {1}'.format(r.status_code, r.text)


def get_my_drive(access_token, user_email):
    url = graph_endpoint.format("/me/drive/root/microsoft.graph.search(q='.xlsx')?$select=id,name")
    r = make_api_call(
        'GET',
        url,
        access_token,
        user_email
    )

    if (r.status_code == requests.codes.ok):
        return r.json()['value']
    else:
        return "{0}: {1}".format(r.status_code, r.text)


# Gets the used range and loads it from the file with the given file id
# REQUIRES SHEETNAME TO BE "Sheet1"
def get_my_sheet(access_token, user_email, file_id, do_import=False):
    url = graph_endpoint.format('/me/drive/items/{}/workbook/worksheets/Sheet1/UsedRange'.format(file_id))
    r = make_api_call('GET', url, access_token, user_email)
    if (r.status_code == requests.codes.ok):
        if do_import:
            from_data_array(r.json()['formulas'])
        return r.json()['formulas']
    else:
        return "{0}: {1}".format(r.status_code, r.text)
