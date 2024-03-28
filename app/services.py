import requests
from django.conf import settings

def qbo_api_call(access_token, realm_id):
    """[summary]
    
    """
    
    if settings.ENVIRONMENT == 'production':
        base_url = settings.QBO_BASE_PROD
    else:
        base_url =  settings.QBO_BASE_SANDBOX

    route = '/v3/company/{0}/companyinfo/{0}'.format(realm_id)
    auth_header = 'Bearer {0}'.format(access_token)
    headers = {
        'Authorization': auth_header, 
        'Accept': 'application/json'
    }
    return requests.get('{0}{1}'.format(base_url, route), headers=headers)
    

def qbo_api_call_invoice(access_token, realm_id):
    """[summary]
    
    """
    print(realm_id)
    if settings.ENVIRONMENT == 'production':
        base_url = settings.QBO_BASE_PROD
    else:
        base_url =  settings.QBO_BASE_SANDBOX

    # route = '/v3/company/{0}/query?query=select * from Invoice&minorversion=69'.format(realm_id)
    route = "/v3/company/{0}/query?query=select * from Customer Where Metadata.LastUpdatedTime > '2015-03-01'&minorversion=69".format(realm_id)
    auth_header = 'Bearer {0}'.format(access_token)
    headers = {
        'Authorization': auth_header, 
        'Accept': 'application/json'
    }
    return requests.get('{0}{1}'.format(base_url, route), headers=headers)
    

    # GET /v3/company/4620816365345759820/query?query=<selectStatement>&minorversion=54

# Content type:application/text
# Production Base URL:https://quickbooks.api.intuit.com
# Sandbox Base URL:https://sandbox-quickbooks.api.intuit.com