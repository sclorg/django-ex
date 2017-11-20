from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = []

if settings.DEPLOYMENT_TYPE == 'localdev':
    urlpatterns.append(url(r'^admin/', admin.site.urls))

urlpatterns.append(url(r'^', include('edivorce.apps.core.urls')))
