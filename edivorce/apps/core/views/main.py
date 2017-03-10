from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone
from ..decorators import bceid_required
import datetime
from ..models import BceidUser
from ..utils.user_response import get_responses_from_db, get_responses_from_db_grouped_by_steps, \
    get_responses_from_session, copy_session_to_db, get_step_status
from edivorce.apps.core.utils.question_step_mapping import list_of_registries
from django.core.exceptions import ObjectDoesNotExist


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
    # if the user is returning from BCeID registration, then log them in to the site
    if request.bceid_user.is_authenticated and request.session.get('went-to-register', False) == True:
        request.session['went-to-register'] = False
        return redirect(settings.FORCE_SCRIPT_NAME[:-1] + '/login')

    return render(request, 'intro.html', context={'hide_nav': True})


def success(request):
    if request.bceid_user.is_authenticated:
        return redirect(settings.FORCE_SCRIPT_NAME[:-1] + '/overview')
    else:
        return render(request, 'success.html', context={'register_url': settings.REGISTER_URL})

@bceid_required
def legal(request):
    return render(request, 'legal.html', context={'active_page': 'legal'})

@bceid_required
def savepdf(request):
    return render(request, 'savepdf.html', context={'active_page': 'savepdf'})


def login(request):

    if settings.DEPLOYMENT_TYPE == 'localdev' and not request.session.get('fake-bceid-guid'):
        return redirect(settings.FORCE_SCRIPT_NAME[:-1] + '/bceid')
    else:
        guid = request.bceid_user.guid

        if guid is None:
            return render(request, 'localdev/debug.html')

        user = __get_bceid_user(request)

        if timezone.now() - user.last_login > datetime.timedelta(minutes=1):
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
        user = __get_bceid_user(request)

        responses_dict = get_responses_from_db(user)
        responses_dict['active_page'] = 'prequalification'
        responses_dict['step_status'] = get_step_status(get_responses_from_db_grouped_by_steps(user))

    return render(request, template_name=template, context=responses_dict)


def register(request):
    if settings.DEPLOYMENT_TYPE == 'localdev':
        return render(request, 'localdev/register.html')
    else:
        request.session['went-to-register'] = True
        return redirect(settings.REGISTER_URL)


@bceid_required
def question(request, step):
    """
    View rendering main questions
    For review page, use response grouped by step to render page
    """
    template = 'question/%s.html' % step
    user = __get_bceid_user(request)
    responses_dict_by_step = get_responses_from_db_grouped_by_steps(user)

    if step == "11_review":
        responses_dict = responses_dict_by_step
    else:
        responses_dict = get_responses_from_db(user)
    responses_dict['active_page'] = step
    # If page is filing location page, add registries dictionary for list of court registries
    if step == "10_location":
        responses_dict['registries'] = sorted(list_of_registries)

    # Add step status dictionary
    responses_dict['step_status'] = get_step_status(responses_dict_by_step)
    return render(request, template_name=template, context=responses_dict)


@bceid_required
def overview(request):
    """
    View rendering process overview page
    If user responded to questions for certain step,
    mark that step as "Started" otherwise "Not started"
    """
    user = __get_bceid_user(request)
    responses_dict_by_step = get_responses_from_db_grouped_by_steps(user)
    # step status dictionary
    status_dict = {'step_status': get_step_status(responses_dict_by_step),
                   'active_page': 'overview'}
    return render(request, 'overview.html', context=status_dict)


def __get_bceid_user(request):
    user, created = BceidUser.objects.get_or_create(user_guid=request.bceid_user.guid)

    # update the last_login timestamp if it was more than 2 hours ago
    # this ensures that it gets updated for users who bypass the /login url with a direct link
    if user.last_login is None or timezone.now() - user.last_login > datetime.timedelta(hours=2):
        user.last_login = timezone.now()
        user.save()

    return user


