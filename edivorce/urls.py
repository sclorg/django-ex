from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from graphene_django.views import GraphQLView

from .apps.core.views import main

urlpatterns = []

if settings.ENVIRONMENT in ['localdev', 'dev', 'test', 'minishift']:
    import debug_toolbar
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)),)
    urlpatterns.append(url(r'^poc/', include('edivorce.apps.poc.urls')))
    urlpatterns.append(path('api/graphql/', GraphQLView.as_view(graphiql=True))),
else:
    urlpatterns.append(path('api/graphql/', GraphQLView.as_view(graphiql=False))),

if settings.ENVIRONMENT in ['localdev', 'minishift']:
    urlpatterns.append(url(r'^admin/', admin.site.urls))
    urlpatterns.append(url(r'^404/$', main.page_not_found, {'exception': Exception()}))
    urlpatterns.append(url(r'^500/$', main.server_error))

urlpatterns.append(url(r'^', include('edivorce.apps.core.urls')))

handler404 = main.page_not_found
handler500 = main.server_error
