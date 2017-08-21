import requests
import uuid
import json
from portfolio_manager.importer import from_data_array
from portfolio_manager.exporter import get_data_array

graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'

# Function that makes api calls to given url
def make_api_call(method, url, token, user_email, xtra_headers={},payload=None, parameters=None):
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
    headers.update(xtra_headers)

    response = None

    if (method.upper() == 'GET'):
        response = requests.get(url, headers=headers, params=parameters)
    elif (method.upper() == 'DELETE'):
        response = requests.delete(url, headers=headers, params=parameters)
    elif (method.upper() == 'PATCH'):
        headers.update({'Content-Type': 'application/json'})
        print(url)
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
    url = graph_endpoint.format("/me/drive/root/microsoft.graph.search(q='.xlsx')?$select=id,name,webUrl")
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
def get_and_import_my_sheet(access_token, user_email, file_id):
    url = graph_endpoint.format('/me/drive/items/{}/workbook/worksheets/Sheet1/UsedRange'.format(file_id))
    r = make_api_call('GET', url, access_token, user_email)
    if (r.status_code == requests.codes.ok):
        from_data_array(r.json()['formulas'])
        return r.json()['formulas']
    else:
        return "{0}: {1}".format(r.status_code, r.text)


def export_sheet(access_token, user_email, file_id):
    url = graph_endpoint.format('/me/drive/items/{}/workbook/createSession'.format(file_id))
    params = {
        'persistChanges': 'true'
    }
    r = make_api_call('POST', url, access_token, user_email, parameters=params)

    if (r.status_code == requests.codes.created):
        session_id = r.json()['id']
        range_end, data = get_data_array()
        url2 = graph_endpoint.format('/me/drive/items/{}/workbook/worksheets(\'NewSheet\')/range(address=\'NewSheet!A1:{}\')'.format(file_id,range_end))
        params2 = {
            'values': data
        }
        r2 = make_api_call('PATCH', url2, access_token, user_email, xtra_headers={'workbook-session-id': session_id}, payload=params2)
        if (r2.status_code == requests.codes.ok):
            return data
        else:
            print('{0}: {1}'.format(r2.status_code, r2.text))
    else:
        print("NOT CREATED!")
        print('{0}: {1}'.format(r.status_code, r.text))
