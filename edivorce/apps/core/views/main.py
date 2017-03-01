from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from ..decorators import bceid_required
from ..models import BceidUser
from ..utils.user_response import get_responses_from_db, get_responses_from_db_grouped_by_steps, get_responses_from_session, copy_session_to_db


@bceid_required
def serve(request, path):
    if path[0:2] == 'f/':
        path = path[2:0]
    if (len(path) > 4 and path[-5:] != '.html') or len(path) == 0:
        path += '/intro.html'
    if path[:1] == '/':
        path = path[1:]
    return render(request, path)


def intro(request):
    return render(request, 'intro.html', context={'hide_nav': True})


def login(request):

    if settings.DEPLOYMENT_TYPE == 'localdev' and not request.session.get('fake-bceid-guid'):
        return redirect(settings.FORCE_SCRIPT_NAME[:-1] + '/bceid')
    else:
        guid = request.bceid_user.guid

        if guid == None:
            return render(request, 'localdev/debug.html')

        user, created = BceidUser.objects.get_or_create(user_guid=guid)

        user.last_login = timezone.now()
        user.save()

        copy_session_to_db(request, user)

        return redirect(settings.FORCE_SCRIPT_NAME[:-1] + '/overview')


def logout(request):
    request.session.flush()

    if settings.DEPLOYMENT_TYPE == 'localdev':
        return redirect(settings.FORCE_SCRIPT_NAME[:-1] + '/intro')
    else:
        return redirect(settings.LOGOUT_URL)

def prequalification(request, step):
    """
    View rendering pre-qualification questions
     If user is not authenticated with proper BCeID,
     temporarily store user responses to session
    """
    template = 'prequalification/step_%s.html' % step

    if not request.bceid_user.is_authenticated:
        responses_dict = get_responses_from_session(request)
    else:
        user = BceidUser.objects.get(user_guid=request.bceid_user.guid)
        responses_dict = get_responses_from_db(user)

    return render(request, template_name=template, context=responses_dict)


@bceid_required
def form(request, step):
    """
    View rendering main questions
    For review page, use response grouped by step to render page
    """
    template = 'question/%s.html' % step
    user = BceidUser.objects.get(user_guid=request.bceid_user.guid)
    if step == "11_review":
        responses_dict = get_responses_from_db_grouped_by_steps(user)
    else:
        responses_dict = get_responses_from_db(user)
    return render(request, template_name=template, context=responses_dict)


@bceid_required
def overview(request):
    """
    View rendering process overview page
    If user responded to questions for certain step,
    mark that step as "Started" otherwise "Not started"
    """
    user = BceidUser.objects.get(user_guid=request.bceid_user.guid)
    responses_dict = get_responses_from_db_grouped_by_steps(user)
    # To Show whether user has started to respond questions in each step
    started_dict = {}
    for step, lst in responses_dict.items():
        if not lst:
            started_dict[step] = "Not started"
        else:
            started_dict[step] = "Started"
    return render(request, 'overview.html', context=started_dict)



