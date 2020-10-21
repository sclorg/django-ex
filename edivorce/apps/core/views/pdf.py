""" Views for generated forms """

import json

from django.conf import settings
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

import requests

from ..models import Document
from ..utils.derived import get_derived_data
from ..utils.user_response import get_data_for_user

EXHIBITS = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[::-1])


@login_required
def pdf_form(request, form_number):
    """ View for rendering PDF's and previews """

    responses = get_data_for_user(request.user)

    if (form_number == '1' or form_number.startswith('37') or
            form_number.startswith('38') or
            form_number.startswith('35')):
        # Add an array of children that includes blanks for possible children
        children = json.loads(responses.get('claimant_children', '[]'))
        responses['num_actual_children'] = len(children)
        responses['children'] = children

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

    if form_number == '96_claimant1':
        form_number = '96'
        responses = __add_claimant_info(responses, '_you')
        responses['which_claimant'] = 'Claimant 1'
    elif form_number == '96_claimant2':
        form_number = '96'
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
    output_as_debug = request.GET.get('debug', None) is not None    

    if output_as_html:
        context['css_root'] = settings.FORCE_SCRIPT_NAME[:-1]
        context['image_root'] = settings.FORCE_SCRIPT_NAME[:-1]        

    template_name = form_name
    if not form_name.startswith('form'):
        template_name = 'images_to_pdf'

    # render to form as HTML
    rendered_html = render_to_string('pdf/' + template_name + '.html',
                                     context=context, request=request)

    # if '?html' is in the querystring, then return the plain html
    if output_as_html or output_as_debug:
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


@login_required
def images_to_pdf(request, doc_type, party_code):
    documents = Document.objects.filter(
        bceid_user=request.user, doc_type=doc_type, party_code=party_code)

    if not documents:
        return HttpResponse(status=204)

    if party_code == 1:
        form_name = doc_type + "_claimant1"
    elif party_code == 2:
        form_name = doc_type + "_claimant2"
    else:
        form_name = doc_type

    if documents[0].filename.endswith(('.pdf', '.PDF')):
        response = HttpResponse(documents[0].file.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=' + form_name + '.pdf'
        return response

    return __render_form(request, form_name, {
        'image_root': settings.WEASYPRINT_IMAGE_LOOPBACK,
        'css_root': settings.WEASYPRINT_CSS_LOOPBACK,
        'images': documents,
        'form': form_name
    })
