from django.conf.urls import url

from .views import main, system, styleguide, pdf, api, localdev

urlpatterns = [
    url(r'^guide$', styleguide.guide),
    url(r'^f/(?P<path>.*)', main.serve),
    url(r'^api/response$', api.UserResponseHandler.as_view()),
    url(r'^login', main.login, name="login"),
    url(r'^bceid', localdev.bceid, name="bceid"),
    url(r'^logout', main.logout, name="logout"),
    url(r'^overview', main.overview, name="overview"),
    url(r'^health$', system.health),
    url(r'^pdf-form(?P<form_number>[0-9]{1,3})$', pdf.form, name="pdf_form"),
    url(r'^prequalification/step_(?P<step>[0-9]{2})$', main.prequalification, name="prequalification"),
    url(r'^question/(?P<step>.*)', main.form, name="question_steps"),
    url(r'^', main.intro, name="intro"),
]


