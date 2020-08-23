from django.conf.urls import url

from .views import main, system, pdf, api, localdev


urlpatterns = [
    # url(r'^guide$', styleguide.guide),
    url(r'^api/response$', api.UserResponseHandler.as_view()),

    # url(r'^login/headers$', system.headers),

    url(r'^login$', main.login, name="login"),
    url(r'^bceid$', localdev.bceid, name="bceid"),
    url(r'^register$', main.register, name="register"),
    url(r'^register_sc$', main.register_sc, name="register_sc"),
    url(r'^logout$', main.logout, name="logout"),
    url(r'^overview$', main.overview, name="overview"),
    url(r'^success$', main.success, name="success"),
    url(r'^incomplete$', main.incomplete, name="incomplete"),
    url(r'^intercept$', main.intercept_page, name="intercept"),
    url(r'^dashboard/(?P<nav_step>.*)', main.dashboard_nav, name="dashboard_nav"),
    url(r'^health$', system.health),
    url(r'^legal$', main.legal, name="legal"),
    url(r'^acknowledgements$', main.acknowledgements, name="acknowledgements"),
    url(r'^contact$', main.contact, name="contact"),

    # url(r'^headers$', system.headers),

    url(r'^pdf-form(?P<form_number>[0-9]{1,3}(_we|_claimant1|_claimant2)?)$', pdf.form, name="pdf_form"),
    url(r'^prequalification/step_(?P<step>[0-9]{2})$', main.prequalification, name="prequalification"),
    url(r'^question/(?P<step>.*)/(?P<sub_step>.*)/$', main.question, name="question_steps"),
    url(r'^question/(?P<step>.*)$', main.question, name="question_steps"),
    url(r'^current$', system.current, name="current"),
    url(r'^$', main.home, name="home"),
]