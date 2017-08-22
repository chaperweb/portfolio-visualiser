import requests
import uuid
import json
from portfolio_manager.importer import from_data_array
from portfolio_manager.exporter import get_data_array

graph_endpoint = 'https://graph.microsoft.com/v1.0{0}'

# Function that makes api calls to given url
def make_api_call(method, url, token, user_email, extra_headers={},payload=None, parameters=None):
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
    headers.update(extra_headers)

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
    # Create session so that changes persist
    session_url = graph_endpoint.format('/me/drive/items/{}/workbook/createSession'.format(file_id))
    session_params = { 'persistChanges': 'true' }
    session_result = make_api_call(
        'POST',
        session_url,
        access_token,
        user_email,
        parameters=session_params
    )

    if (session_result.status_code == requests.codes.created):
        session_id = session_result.json()['id']
        range_end, data = get_data_array()

        # TODO: Change it so it isn't hardcoded as NewSheet but let user choose
        #       which sheet it should be exported to
        item_url = '/me/drive/items/{}'.format(file_id)
        newsheet_url = 'workbook/worksheets(\'NewSheet\')'
        range_url = 'range(address=\'NewSheet!A1:{}\')'.format(range_end)
        export_url = graph_endpoint.format('{}/{}/{}'.format(
            item_url,
            newsheet_url,
            range_url
        ))
        payload = { 'values': data }
        export_result = make_api_call(
            'PATCH',
            export_url,
            access_token,
            user_email,
            extra_headers={'workbook-session-id': session_id},
            payload=payload
        )
        if (export_result.status_code == requests.codes.ok):
            return data
        elif (export_result.status_code == 404):
            return print('NewSheet not found!')
        else:
            print('{0}: {1}'.format(export_result.status_code, export_result.text))
    else:
        print('{0}: {1}'.format(session_result.status_code, session_result.text))
