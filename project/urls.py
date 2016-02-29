from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    # Examples:
    # url(r'^$', 'project.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', 'welcome.views.index'),
    url(r'^health$', 'welcome.views.health'),
    url(r'^admin/', include(admin.site.urls)),
]
