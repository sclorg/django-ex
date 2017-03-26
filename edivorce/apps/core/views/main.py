from django.conf import settings
from django.shortcuts import render, redirect, render_to_response
from django.utils import timezone
from django.template import RequestContext
from edivorce.apps.core.utils.template_step_order import template_step_order
from ..decorators import bceid_required
import datetime
from ..models import BceidUser
from ..utils.user_response import get_responses_from_db, get_responses_from_db_grouped_by_steps, \
    get_responses_from_session, copy_session_to_db, get_step_status, is_complete, \
    get_responses_from_session_grouped_by_steps
from edivorce.apps.core.utils.question_step_mapping import list_of_registries


def home(request):
    """
    This is the homepage
    """
    # if the user is returning from BCeID registration, then log them in to the site
    if request.bceid_user.is_authenticated and request.session.get('went-to-register', False) == True:
        request.session['went-to-register'] = False
        return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/login')

    return render(request, 'intro.html', context={'hide_nav': True})


def prequalification(request, step):
    """
    View for rendering pre-qualification questions.
    If user is not authenticated with BCeID, temporarily store user responses to session
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


def success(request):
    """
    This page is shown if the user passes the qualification test
    """
    if request.bceid_user.is_authenticated:
        return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/overview')
    else:
        prequal_responses = get_responses_from_session_grouped_by_steps(request)['prequalification']
        complete, missed_questions = is_complete('prequalification', prequal_responses)

        if complete:
            return render(request, 'success.html', context={'register_url': settings.REGISTER_URL})
        else:
            return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/incomplete')


def incomplete(request):
    """
    This page is shown if the user misses any pre-qualification questions
    """
    prequal_responses = get_responses_from_session_grouped_by_steps(request)['prequalification']
    complete, missed_questions = is_complete('prequalification', prequal_responses)
    return render(request, 'incomplete.html',
                            context={'missed_questions': missed_questions, 'debug': settings.DEBUG })


def register(request):
    """
    Sets a session variable and redirects users to register for BCeID
    """
    if settings.DEPLOYMENT_TYPE == 'localdev':
        return render(request, 'localdev/register.html')
    else:
        request.session['went-to-register'] = True
        return redirect(settings.REGISTER_URL)


def login(request):
    """
    This page is proxy-protected by Siteminder.  Users who are not
    logged into BCeID will get a login page.  Users who are logged into
    BCeID will be redirected to the dashboard
    """
    if settings.DEPLOYMENT_TYPE == 'localdev' and not request.session.get('fake-bceid-guid'):
        return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/bceid')
    else:
        guid = request.bceid_user.guid

        if guid is None:
            return render(request, 'localdev/debug.html')

        user = __get_bceid_user(request)

        if timezone.now() - user.last_login > datetime.timedelta(minutes=1):
            user.last_login = timezone.now()
            user.save()

        copy_session_to_db(request, user)

        return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/overview')


def logout(request):
    """
    Clear session and log out of BCeID
    """
    request.session.flush()

    if settings.DEPLOYMENT_TYPE == 'localdev':
        return redirect('/')
    else:
        return redirect(settings.LOGOUT_URL)


@bceid_required
def overview(request):
    """
    Dashboard: Process overview page.
    """
    user = __get_bceid_user(request)
    responses_dict_by_step = get_responses_from_db_grouped_by_steps(user)

    # Add step status dictionary
    responses_dict_by_step['step_status'] = get_step_status(responses_dict_by_step)

    responses_dict_by_step['active_page'] = 'overview'
    return render(request, 'overview.html', context=responses_dict_by_step)


@bceid_required
def dashboard_nav(request, nav_step):
    """
    Dashboard: All other pages
    """
    template_name = 'dashboard/%s.html' % nav_step
    return render(request, template_name=template_name, context={'active_page': nav_step})


@bceid_required
def question(request, step):
    """
    View for rendering main divorce questionaire questions
    """
    template = 'question/%02d_%s.html' % (template_step_order[step], step)

    user = __get_bceid_user(request)
    responses_dict_by_step = get_responses_from_db_grouped_by_steps(user)

    if step == "review":
        responses_dict = responses_dict_by_step
    else:
        responses_dict = get_responses_from_db(user)

    # Add step status dictionary
    responses_dict['step_status'] = get_step_status(responses_dict_by_step)

    responses_dict['active_page'] = step
    # If page is filing location page, add registries dictionary for list of court registries
    if step == "location":
        responses_dict['registries'] = sorted(list_of_registries)

    return render(request, template_name=template, context=responses_dict)


def page_not_found(request):
    """
    404 Error Page
    """
    response = render_to_response('404.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 404
    return response


def server_error(request):
    """
    500 Error Page
    """
    response = render_to_response('500.html', {},
                                  context_instance=RequestContext(request))
    response.status_code = 500
    return response


def legal(request):
    """
    Legal Information page
    """
    return render(request, 'legal.html', context={'active_page': 'legal'})


def __get_bceid_user(request):
    user, created = BceidUser.objects.get_or_create(user_guid=request.bceid_user.guid)

    # update the last_login timestamp if it was more than 2 hours ago
    # this ensures that it gets updated for users who bypass the /login url with a direct link
    if user.last_login is None or timezone.now() - user.last_login > datetime.timedelta(hours=2):
        user.last_login = timezone.now()
        user.save()

    return user
