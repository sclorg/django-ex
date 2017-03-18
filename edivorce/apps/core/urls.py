from django.conf.urls import url

from .views import main, system, styleguide, pdf, api, localdev

urlpatterns = [
    url(r'^guide$', styleguide.guide),
    url(r'^f/(?P<path>.*)', main.serve),
    url(r'^api/response$', api.UserResponseHandler.as_view()),
    url(r'^login', main.login, name="login"),
    url(r'^bceid', localdev.bceid, name="bceid"),
    url(r'^register$', main.register, name="register"),
    url(r'^logout', main.logout, name="logout"),
    url(r'^overview', main.overview, name="overview"),
    url(r'^success', main.success, name="success"),
    url(r'^dashboard/(?P<nav_step>.*)', main.dashboard_nav, name="dashboard_nav"),
    url(r'^health$', system.health),
    url(r'^legal', main.legal, name="legal"),

    # todo: remove these 'headers' lines once SMGOV headers are working
    url(r'^divorce/headers$', system.headers),
    url(r'^divorce-test/headers$', system.headers),
    url(r'^divorce-dev/headers$', system.headers),
    url(r'^headers$', system.headers),

    url(r'^pdf-form(?P<form_number>[0-9]{1,3}(_we|_claimant1|_claimant2)?)$', pdf.form, name="pdf_form"),
    url(r'^prequalification/step_(?P<step>[0-9]{2})$', main.prequalification, name="prequalification"),
    url(r'^question/(?P<step>.*)$', main.question, name="question_steps"),
    url(r'^', main.intro, name="intro"),
]


