from __future__ import absolute_import

from requests import HTTPError
import json

from intuitlib.client import AuthClient
from intuitlib.migration import migrate
from intuitlib.enums import Scopes
from intuitlib.exceptions import AuthClientError

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.conf import settings
from django.core import serializers
from . import models

from app.services import qbo_api_call,qbo_api_call_invoice,qbo_api_call_customer,qbo_api_call_invoice_pdf

from django.urls import reverse

# Create your views here.
def list(request):

    all_organizations = models.Organization.objects.all()
    all_customers = models.Customers.objects.all()
    print(all_organizations)
    print(all_customers)

    context = {'all_organizations':all_organizations, 
               'all_customers':all_customers}

    return render(request, 'list.html',context=context)


def delete(request):

    if request.POST:
        # delete the Org
        pk = request.POST['pk']
        try:
            models.Organization.objects.get(code=pk).delete()
            return redirect(reverse('app:list'))
        except:
            print('pk not found!')
            return redirect(reverse('app:list'))
    else:
        return render(request, 'delete.html')
    
def qbo_invoice(request):

    print(request.session.get('access_token',None))

    # if request.POST:
        # delete the Org
    pk = 1
    customer = models.Customers.objects.get(customer_id=pk)
    print(customer.company_name)
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
        realm_id=request.session.get('realm_id', None),
        )
    if auth_client.access_token is not None:
        access_token = auth_client.access_token

    if auth_client.realm_id is None:
        raise ValueError('Realm id not specified.')

    
    response = qbo_api_call_invoice(auth_client.access_token, auth_client.realm_id,customer.customer_id)
            # print(response)
    
    invoice_pulled = json.loads(response.content)
    print(invoice_pulled)
    invoice_id = invoice_pulled['QueryResponse']['Invoice'][1]['Id']
    print(invoice_id)
    response_2 = qbo_api_call_invoice_pdf(auth_client.access_token, auth_client.realm_id,invoice_id)
    print(response_2)



    return render(request, 'invoice.html')


# Create your views here.
def index(request):
    return render(request, 'index.html')

def oauth(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT,
    )

    url = auth_client.get_authorization_url([Scopes.ACCOUNTING])
    # print(url)
    request.session['state'] = auth_client.state_token
    return redirect(url)

def openid(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT,
    )

    url = auth_client.get_authorization_url([Scopes.OPENID, Scopes.EMAIL])
    request.session['state'] = auth_client.state_token
    return redirect(url)

def callback(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        state_token=request.session.get('state', None),
    )

    state_tok = request.GET.get('state', None)
    error = request.GET.get('error', None)
    
    if error == 'access_denied':
        return redirect('app:index')
    
    # if state_tok is None:
    #     return HttpResponseBadRequest()
    # elif state_tok != auth_client.state_token:  
    #     return HttpResponse('unauthorized', status=401)
    
    auth_code = request.GET.get('code', None)
    realm_id = request.GET.get('realmId', None)
    request.session['realm_id'] = realm_id

    if auth_code is None:
        return HttpResponseBadRequest()

    try:
        auth_client.get_bearer_token(auth_code, realm_id=realm_id)
        request.session['access_token'] = auth_client.access_token
        request.session['refresh_token'] = auth_client.refresh_token
        request.session['id_token'] = auth_client.id_token
    except AuthClientError as e:
        # just printing status_code here but it can be used for retry workflows, etc
        print(e.status_code)
        print(e.content)
        print(e.intuit_tid)
    except Exception as e:
        print(e)
    return redirect('app:connected')

def connected(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
        id_token=request.session.get('id_token', None),
    )

    if auth_client.id_token is not None:
        return render(request, 'connected.html', context={'openid': True})
    else:
        return render(request, 'connected.html', context={'openid': False})

def qbo_customer(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
        realm_id=request.session.get('realm_id', None),
    )

    organization = models.Organization.objects.get(code='1')

    if auth_client.access_token is not None:
        access_token = auth_client.access_token

    if auth_client.realm_id is None:
        raise ValueError('Realm id not specified.')

    response = qbo_api_call_customer(auth_client.access_token, auth_client.realm_id)
    # print(response)
    customer_pulled = json.loads(response.content)
    # print(len(invoices_pulled['QueryResponse']['Customer']))
    for i in range(0,len(customer_pulled['QueryResponse']['Customer'])):
        # print(invoices_pulled['QueryResponse']['Customer'][i]['DisplayName'],' ID: ',invoices_pulled['QueryResponse']['Customer'][i]['Id'])
        customer_id = customer_pulled['QueryResponse']['Customer'][i].get('Id')
        company_name = customer_pulled['QueryResponse']['Customer'][i].get('DisplayName')
        display_name = customer_pulled['QueryResponse']['Customer'][i].get('DisplayName')

        if customer_pulled['QueryResponse']['Customer'][i].get('PrimaryEmailAddr','') == '':
            email = ''
        else:
            email = customer_pulled['QueryResponse']['Customer'][i]['PrimaryEmailAddr']['Address']
        company_code = organization
        models.Customers.objects.create(customer_id=customer_id, company_name=company_name, display_name= display_name,email=email,company_code=company_code)

    if not response.ok:
        return HttpResponse(' '.join([response.content, str(response.status_code)]))
    else:
        return HttpResponse(response.content)


def qbo_request(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
        realm_id=request.session.get('realm_id', None),
    )

    if auth_client.access_token is not None:
        access_token = auth_client.access_token

    if auth_client.realm_id is None:
        raise ValueError('Realm id not specified.')
    response = qbo_api_call(auth_client.access_token, auth_client.realm_id)
    Organization_pulled = json.loads(response.content)
    company_name = Organization_pulled['CompanyInfo']['CompanyName']
    code = Organization_pulled['CompanyInfo']['Id']
    email = Organization_pulled['CompanyInfo']['Email']['Address']

    print(code)
    print(company_name)
    print(email)

    models.Organization.objects.create(code=code, company_name=company_name,email=email)

    response2 = qbo_api_call_invoice(auth_client.access_token, auth_client.realm_id)
    # print(response2)
    invoices_pulled = json.loads(response2.content)
    # print(len(invoices_pulled['QueryResponse']['Customer']))
    # for i in range(0,len(invoices_pulled['QueryResponse']['Customer'])):
        # print(invoices_pulled['QueryResponse']['Customer'][i]['DisplayName'],' ID: ',invoices_pulled['QueryResponse']['Customer'][i]['Id'])
    # print(invoices_pulled['QueryResponse']['Invoice'][0].keys())
    # print(invoices_pulled['QueryResponse']['Invoice'][1].keys())
    # print(invoices_pulled['QueryResponse']['Invoice'][2].keys())

    if not response.ok:
        return HttpResponse(' '.join([response.content, str(response.status_code)]))
    else:
        return HttpResponse(response.content)
    

def user_info(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
        id_token=request.session.get('id_token', None),
    )

    try:
        response = auth_client.get_user_info()
    except ValueError:
        return HttpResponse('id_token or access_token not found.')
    except AuthClientError as e:
        print(e.status_code)
        print(e.intuit_tid)
    return HttpResponse(response.content)
        
def refresh(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
    )

    try:
        auth_client.refresh() 
    except AuthClientError as e:
        print(e.status_code)
        print(e.intuit_tid)
    return HttpResponse('New refresh_token: {0}'.format(auth_client.refresh_token))

def revoke(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT, 
        access_token=request.session.get('access_token', None), 
        refresh_token=request.session.get('refresh_token', None), 
    )
    try:
        is_revoked = auth_client.revoke()
    except AuthClientError as e:
        print(e.status_code)
        print(e.intuit_tid)
    return HttpResponse('Revoke successful')


def migration(request):
    auth_client = AuthClient(
        settings.CLIENT_ID, 
        settings.CLIENT_SECRET, 
        settings.REDIRECT_URI, 
        settings.ENVIRONMENT,
    )
    try:
        migrate(
            settings.CONSUMER_KEY, 
            settings.CONSUMER_SECRET, 
            settings.ACCESS_KEY, 
            settings.ACCESS_SECRET, 
            auth_client, 
            [Scopes.ACCOUNTING]
        )
    except AuthClientError as e:
        print(e.status_code)
        print(e.intuit_tid)
    return HttpResponse('OAuth2 refresh_token {0}'.format(auth_client.refresh_token))
