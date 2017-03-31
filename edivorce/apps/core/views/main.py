from django.conf import settings
from django.shortcuts import render, redirect, render_to_response
from django.utils import timezone
from django.template import RequestContext
from edivorce.apps.core.utils.template_step_order import template_step_order
from ..decorators import bceid_required
import datetime
from ..models import BceidUser
from ..utils.user_response import get_responses_from_db, get_responses_from_db_grouped_by_steps, \
    get_responses_from_session, copy_session_to_db, get_responses_from_session_grouped_by_steps
from ..utils.step_completeness import get_step_status, is_complete
from edivorce.apps.core.utils.question_step_mapping import list_of_registries


def home(request):
    """
    This is the homepage
    """
    # HTTP_SM_USER is available on both unsecure and secure pages.
    # If it has a value then we know the user is logged into BCeID/siteminder
    siteminder_is_authenticated = request.META.get('HTTP_SM_USER', '') != ''

    # if the user is returning from BCeID registration, then log them in to the site
    if siteminder_is_authenticated and request.session.get('went_to_register', False) == True:
        request.session['went_to_register'] = False
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
        user, _ = __get_bceid_user(request)

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

    responses_dict = get_responses_from_session(request)
    responses_dict.append(('debug', settings.DEBUG, ))
    responses_dict.append(('missed_questions', str(missed_questions), ))

    return render(request, 'incomplete.html', context=responses_dict)


def register(request):
    """
    Sets a session variable and redirects users to register for BCeID
    """
    if settings.DEPLOYMENT_TYPE == 'localdev':
        return render(request, 'localdev/register.html')
    else:
        request.session['went_to_register'] = True
        return redirect(settings.REGISTER_URL)


def login(request):
    """
    This page is proxy-protected by Siteminder.  Users who are not
    logged into BCeID will get a login page.  Users who are logged into
    BCeID will be redirected to the dashboard
    """
    if settings.DEPLOYMENT_TYPE == 'localdev' and not request.session.get('fake_bceid_guid'):
        return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/bceid')
    else:

        # get the Guid that was set in the middleware
        if request.bceid_user.guid is None:
            # Fix for weird siteminder behaviour......
            # If a user is logged into an IDIR then they can see the login page
            # but the SMGOV headers are missing.  If this is the case, then log them out
            # of their IDIR, and redirect them back to here again....

            # FUTURE DEV NOTE: The DC elements of HTTP_SM_USERDN header will tell us exactly how the user is
            # logged in. But it doesn't seem like a very good idea at this time to rely on this magic string.
            # e.g. CN=Smith\, John,OU=Users,OU=Attorney General,OU=BCGOV,DC=idir,DC=BCGOV

            if request.GET.get('noretry','') != 'true':
                return redirect(settings.LOGOUT_URL_TEMPLATE % (
                    settings.PROXY_BASE_URL, settings.FORCE_SCRIPT_NAME[:-1] + '/login%3Fnoretry=true'))
            else:
                return render(request, '407.html')

        user, created = __get_bceid_user(request)

        # some later messaging needs to be shown or hidden based on whether
        # or not this is a returning user
        request.session["first_login"] = created

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

    response = redirect(settings.LOGOUT_URL)

    if settings.DEPLOYMENT_TYPE == 'localdev':
        response = redirect('/')

    return response


@bceid_required
def overview(request):
    """
    Dashboard: Process overview page.
    """
    user, _ = __get_bceid_user(request)
    responses_dict_by_step = get_responses_from_db_grouped_by_steps(user)

    # Add step status dictionary
    responses_dict_by_step['step_status'] = get_step_status(responses_dict_by_step)
    responses_dict_by_step['active_page'] = 'overview'

    response = render(request, 'overview.html', context=responses_dict_by_step)

    # set this session variable after the page is already rendered
    request.session['viewed_dashboard_during_session'] = True

    return response


@bceid_required
def dashboard_nav(request, nav_step):
    """
    Dashboard: All other pages
    """
    user, _ = __get_bceid_user(request)
    responses_dict = get_responses_from_db(user)
    responses_dict['active_page'] = nav_step
    template_name = 'dashboard/%s.html' % nav_step
    return render(request, template_name=template_name, context=responses_dict)


@bceid_required
def question(request, step):
    """
    View for rendering main divorce questionaire questions
    """
    template = 'question/%02d_%s.html' % (template_step_order[step], step)

    user, _ = __get_bceid_user(request)
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

    return user, created
