from django.conf.urls import url
from django.views.generic.base import RedirectView
from . import views
from django.urls import path, include

app_name = 'app'

favicon_view = RedirectView.as_view(url='/static/favicon.ico', permanent=True)

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^oauth/?$', views.oauth, name='oauth'),
    url(r'^openid/?$', views.openid, name='openid'),
    url(r'^callback/?$', views.callback, name='callback'),
    url(r'^connected/?$', views.connected, name='connected'),
    url(r'^qbo_request/?$', views.qbo_request, name='qbo_request'),
    url(r'^qbo_customer/?$', views.qbo_customer, name='qbo_customer'),
    url(r'^revoke/?$', views.revoke, name='revoke'),
    url(r'^refresh/?$', views.refresh, name='refresh'),
    url(r'^user_info/?$', views.user_info, name='user_info'),
    url(r'^migration/?$', views.migration, name='migration'),
    path('list/',views.list, name = 'list'),
    path('delete/',views.delete, name = 'delete'),
    path('qbo_invoice/',views.qbo_invoice, name = 'invoice'),
    path('index/',views.index, name = 'index'),
 
]
