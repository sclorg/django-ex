from django.conf.urls import url

from .views import main, system, styleguide, pdf, api, localdev

urlpatterns = [
    url(r'^f/(?P<path>.*)', main.serve),
    url(r'^preview/(?P<form>.*)', main.preview),
    url(r'^prequalification/step_(?P<step>[0-9]{2})$', main.prequalification, name="prequalification"),
    url(r'^api/response$', api.UserResponseHandler.as_view()),
    url(r'^dashboard', main.dashboard),
    url(r'^login', main.login, name="login"),
    url(r'^bceid', localdev.bceid, name="bceid"),
    url(r'^logout', main.logout, name="logout"),
    url(r'^overview', main.overview, name="overview"),
    url(r'^intro', main.intro, name="intro"),
    url(r'^health$', system.health),
    url(r'^(?P<form>.*)/(?P<step>.*)', main.form, name="form_steps"),
    url(r'^', main.index, name="index"),
]


