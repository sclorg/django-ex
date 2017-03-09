from django.template.loader import render_to_string
from django.http import HttpResponse
import requests

from django.conf import settings

from edivorce.apps.core.decorators import bceid_required
from edivorce.apps.core.models import BceidUser
from ..utils.user_response import get_responses_from_db


@bceid_required
def form(request, form_number):
    user = BceidUser.objects.get(user_guid=request.bceid_user.guid)
    responses = get_responses_from_db(user)
    key = 'form38_dummy_together'

    if form_number == '38' and key in responses and responses[key] == 'together':
        form_number += '_we'
    return render_form(request, 'form%s' % form_number,
                       {
                           "css_root": settings.WEASYPRINT_CSS_LOOPBACK,
                           "responses" : responses
                       })


def render_form(request, form_name, context):

    output_as_html = request.GET.get('html', None) is not None

    if output_as_html:
        context["css_root"] = settings.FORCE_SCRIPT_NAME[:-1]

    # render to form as HTML
    rendered_html = render_to_string('pdf/' + form_name + '.html', context=context)

    # if '?html' is in the querystring, then return the plain html
    if output_as_html:
        return HttpResponse(rendered_html)

    else:
        # post the html to the weasyprint microservice
        url = settings.WEASYPRINT_URL + '/pdf?filename=' + form_name + '.pdf'
        pdf = requests.post(url, data=rendered_html)

        # return the response as a pdf
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=' + form_name + '.pdf'

        return response
