from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.urls import reverse

from edivorce.apps.core.models import Question


def health(request):  # pylint: disable=unused-argument
    """
    OpenShift health check
    """
    return HttpResponse(Question.objects.count())


def current(request):
    """
    Debug tool usable in dev and test environments, available at /current
    """
    if settings.ENVIRONMENT not in ['localdev', 'dev', 'test', 'minishift']:
        raise Http404()

    if request.GET.get('reset', False):
        if not request.user.is_anonymous:
            request.user.responses.all().delete()
            request.user.delete()
        request.session.flush()
        return redirect(reverse('current'))

    if request.GET.get('intercept', False) and request.user.is_authenticated:
        request.user.has_seen_orders_page = False
        request.user.save()
        request.user.responses.filter(question__key='want_which_orders').delete()
        return redirect(reverse('current'))

    if request.GET.get('terms', False) and request.user.is_authenticated:
        request.user.has_accepted_terms = not request.user.has_accepted_terms
        request.user.save()
        return redirect(reverse('current'))

    context = {
        'hide_nav': True,
        'is_anonymous': request.user.is_anonymous,
    }

    return render(request, 'dashboard/current.html', context=context)
