from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path # This path is much easier to use without using regular expressions and supported in django 3.0 and higher
from welcome.views import index, health

urlpatterns = [
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    # Below commented urls will also work but the latest support for path function is much efficient to use
    # url(r'^$', index),
    # url(r'^health$', health),
    # url(r'^admin/', include(admin.site.urls)),

    path('',index),
    path('health/',health),
    path('admin/',include(admin.site.urls))
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
