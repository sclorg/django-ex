from django.conf.urls import url
from django.urls import path

from .views import main, system, pdf, api, efiling

urlpatterns = [
    # url(r'^guide$', styleguide.guide),
    url(r'^api/response$', api.UserResponseHandler.as_view()),
    path('api/documents/', api.DocumentCreateView.as_view(), name='documents'),
    path('api/documents/<file_key>/<int:rotation>/', api.get_document_file_by_key, name='file_by_key'),
    path('api/court_location/<city>/', api.court_location, name='court-location'),

    # we add an extra 'x' to the file extension so the siteminder proxy doesn't treat it as an image
    path('api/documents/<doc_type>/<int:party_code>/<filename>x/<int:size>/', api.DocumentView.as_view(), name='document'),

    url(r'^signin$', main.after_login, name="signin"),
    url(r'^register$', main.register, name="register"),
    url(r'^register_sc$', main.register_sc, name="register_sc"),
    url(r'^overview$', main.overview, name="overview"),
    url(r'^success$', main.success, name="success"),
    url(r'^incomplete$', main.incomplete, name="incomplete"),
    url(r'^intercept$', main.intercept_page, name="intercept"),
    url(r'^dashboard/(?P<nav_step>.*)', main.dashboard_nav, name="dashboard_nav"),
    path('submit/initial', efiling.submit_initial_files, name="submit_initial_files"),
    path('submit/final', efiling.submit_final_files, name="submit_final_files"),
    path('after-submit/initial', efiling.after_submit_initial_files, name="after_submit_initial_files"),
    path('after-submit/final', efiling.after_submit_final_files, name="after_submit_final_files"),    
    url(r'^health$', system.health),
    url(r'^legal$', main.legal, name="legal"),
    url(r'^acknowledgements$', main.acknowledgements, name="acknowledgements"),
    url(r'^contact$', main.contact, name="contact"),

    # url(r'^headers$', system.headers),

    url(r'^pdf-form(?P<form_number>[0-9]{1,3}(_we|_claimant1|_claimant2)?)$', pdf.pdf_form, name="pdf_form"),
    path('pdf-images/<doc_type>/<int:party_code>/', pdf.images_to_pdf, name='pdf_images'),
    url(r'^prequalification/step_(?P<step>[0-9]{2})$', main.prequalification, name="prequalification"),
    url(r'^question/(?P<step>.*)/(?P<sub_step>.*)/$', main.question, name="question_steps"),
    url(r'^question/(?P<step>.*)$', main.question, name="question_steps"),
    url(r'^current$', system.current, name="current"),
    url(r'^$', main.home, name="home"),
]
