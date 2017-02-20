from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^f/(?P<path>.*)', views.serve),
    url(r'^preview/(?P<form>.*)', views.preview),
    url(r'^(?P<form>.*)/(?P<step>.*)', views.form),
    url(r'^dashboard', views.dashboard),
    url(r'^login', views.login),
    url(r'^logout', views.logout),
    url(r'^overview', views.overview),
    url(r'^prequalification', views.prequalification),
    url(r'^', views.index),
    url(r'^health$', views.health),
]
