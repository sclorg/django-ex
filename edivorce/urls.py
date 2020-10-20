from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .apps.core.views import main
from .apps.core.views.graphql import PrivateGraphQLView, graphql_schema

urlpatterns = []

if settings.ENVIRONMENT in ['localdev', 'dev', 'test', 'minishift']:
    import debug_toolbar
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)),)
    urlpatterns.append(url(r'^poc/', include('edivorce.apps.poc.urls')))
    urlpatterns.append(path('api/graphql/', csrf_exempt(PrivateGraphQLView.as_view(graphiql=True, schema=graphql_schema)), name='graphql'))
else:
    urlpatterns.append(path('api/graphql/', csrf_exempt(PrivateGraphQLView.as_view(graphiql=False, schema=graphql_schema)), name='graphql'))

if settings.ENVIRONMENT in ['localdev', 'minishift']:
    urlpatterns.append(url(r'^admin/', admin.site.urls))
    urlpatterns.append(url(r'^404/$', main.page_not_found, {'exception': Exception()}))
    urlpatterns.append(url(r'^500/$', main.server_error))

urlpatterns.append(url(r'^oidc/', include('mozilla_django_oidc.urls')))

urlpatterns.append(url(r'^', include('edivorce.apps.core.urls')))

handler404 = main.page_not_found
handler500 = main.server_error
