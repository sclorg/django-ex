""" Views for generated forms """

import json

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string

import requests

from ..decorators import bceid_required
from ..utils.derived import get_derived_data
from ..utils.user_response import get_responses_from_db

EXHIBITS = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[::-1])


@bceid_required
def form(request, form_number):
    """ View for rendering PDF's and previews """

    responses = get_responses_from_db(request.user)

    if (form_number == '1' or form_number.startswith('37') or
            form_number.startswith('38')):
        # Add an array of children that includes blanks for possible children
        under = int(responses.get('number_children_under_19') or 0)
        over = int(responses.get('number_children_under_19') or 0)
        actual = json.loads(responses.get('claimant_children', '[]'))
        total = len(actual)
        responses['children'] = [actual[i] if i < total else {}
                                 for i in range(0, max(under + over, total))]

    if form_number == "37":
        responses["which_claimant"] = 'both'
    elif form_number == "37_claimant1":
        form_number = "37"
        responses = __add_claimant_info(responses, '_you')
        responses['which_claimant'] = 'Claimant 1'
    elif form_number == '37_claimant2':
        form_number = '37'
        responses = __add_claimant_info(responses, '_spouse')
        responses['which_claimant'] = 'Claimant 2'

    if form_number == "38":
        responses["which_claimant"] = 'both'
    elif form_number == '38_claimant1':
        form_number = '38'
        responses = __add_claimant_info(responses, '_you')
        responses['which_claimant'] = 'Claimant 1'
    elif form_number == '38_claimant2':
        form_number = '38'
        responses = __add_claimant_info(responses, '_spouse')
        responses['which_claimant'] = 'Claimant 2'

    return __render_form(request, 'form%s' % form_number, {
        'css_root': settings.WEASYPRINT_CSS_LOOPBACK,
        'responses': responses,
        'derived': get_derived_data(responses),
        'exhibits': EXHIBITS[:],
    })


def __render_form(request, form_name, context):

    output_as_html = request.GET.get('html', None) is not None

    if output_as_html:
        context['css_root'] = settings.FORCE_SCRIPT_NAME[:-1]

    # render to form as HTML
    rendered_html = render_to_string('pdf/' + form_name + '.html',
                                     context=context, request=request)

    # if '?html' is in the querystring, then return the plain html
    if output_as_html:
        return HttpResponse(rendered_html)

    # post the html to the weasyprint microservice
    url = settings.WEASYPRINT_URL + '/pdf?filename=' + form_name + '.pdf'
    pdf = requests.post(url, data=rendered_html.encode('utf-8'))

    # return the response as a pdf
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline;filename=' + form_name + '.pdf'

    return response


def __add_claimant_info(responses, claimant):
    claimant_info = {}
    for key in responses:
        if key.endswith(claimant):
            claimant_key = key.replace(claimant, '_claimant')
            claimant_info[claimant_key] = responses[key]
    responses.update(claimant_info)
    return responses
