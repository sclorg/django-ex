import datetime

from django.conf import settings
from django.shortcuts import render, redirect
from django.utils import timezone

from edivorce.apps.core.utils.derived import get_derived_data
from ..decorators import bceid_required, intercept
from ..utils.question_step_mapping import list_of_registries
from ..utils.step_completeness import get_step_status, is_complete, get_formatted_incomplete_list
from ..utils.template_step_order import template_step_order
from ..utils.user_response import get_responses_from_db, copy_session_to_db, \
    get_responses_from_db_grouped_by_steps, get_responses_from_session, \
    get_responses_from_session_grouped_by_steps


def home(request):
    """
    This is the homepage
    """
    # HTTP_SM_USER is available on both unsecure and secure pages.
    # If it has a value then we know the user is logged into BCeID/siteminder
    siteminder_is_authenticated = request.META.get('HTTP_SM_USER', '') != ''

    # if the user is returning from BCeID registration, then log them in to the site
    if siteminder_is_authenticated and request.session.get('went_to_register', False):
        request.session['went_to_register'] = False
        return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/login')

    return render(request, 'intro.html', context={'hide_nav': True})


def prequalification(request, step):
    """
    View for rendering pre-qualification questions.
    If user is not authenticated with BCeID, temporarily store user responses to session
    """
    template = 'prequalification/step_%s.html' % step

    if not request.user.is_authenticated:
        responses_dict = get_responses_from_session(request)
    else:
        responses_dict = get_responses_from_db(request.user, show_errors=True, step='prequalification', substep=step)
        responses_dict['active_page'] = 'prequalification'
        responses_by_step = get_responses_from_db_grouped_by_steps(request.user)
        responses_dict['step_status'] = get_step_status(responses_by_step)

    return render(request, template_name=template, context=responses_dict)


def success(request):
    """
    This page is shown if the user passes the qualification test
    """
    if request.user.is_authenticated:
        return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/overview')

    prequal_responses = get_responses_from_session_grouped_by_steps(request)['prequalification']
    complete, _ = is_complete('prequalification', prequal_responses)
    if complete:
        return render(request, 'success.html', context={'register_url': settings.REGISTER_URL,'register_sc_url': settings.REGISTER_SC_URL})
    return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/incomplete')


def incomplete(request):
    """
    This page is shown if the user misses any pre-qualification questions
    """
    prequal_responses = get_responses_from_session_grouped_by_steps(request)['prequalification']
    _, missed_question_keys = is_complete('prequalification', prequal_responses)
    missed_questions = get_formatted_incomplete_list(missed_question_keys)

    responses_dict = get_responses_from_session(request)
    responses_dict['debug'] = settings.DEBUG
    responses_dict['missed_questions'] = missed_questions

    return render(request, 'incomplete.html', context=responses_dict)


def register(request):
    """
    Sets a session variable and redirects users to register for BCeID
    """
    if settings.DEPLOYMENT_TYPE in ['localdev', 'minishift']:
        return render(request, 'localdev/register.html')

    request.session['went_to_register'] = True
    return redirect(settings.REGISTER_URL)

def register_sc(request):
    """
    Sets a session variable and redirects users to register for BC Services Card
    """
    if settings.DEPLOYMENT_TYPE in ['localdev', 'minishift']:
        return render(request, 'localdev/register.html')

    request.session['went_to_register'] = True
    return redirect(settings.REGISTER_SC_URL)

def login(request):
    """
    This page is proxy-protected by Siteminder.  Users who are not
    logged into BCeID will get a login page.  Users who are logged into
    BCeID will be redirected to the dashboard
    """
    if settings.DEPLOYMENT_TYPE in ['localdev', 'minishift'] and not request.session.get('fake_bceid_guid'):
        return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/bceid')

    if not request.user.is_authenticated:
        # Fix for weird siteminder behaviour......
        # If a user is logged into an IDIR then they can see the login page but
        # the SMGOV headers are missing.  If this is the case, then log them out
        # of their IDIR, and redirect them back to here again....

        # FUTURE DEV NOTE: The DC elements of HTTP_SM_USERDN header will tell us
        # exactly how the user is logged in. But it doesn't seem like a very
        # good idea at this time to rely on this magic string.  e.g. CN=Smith\,
        # John,OU=Users,OU=Attorney General,OU=BCGOV,DC=idir,DC=BCGOV

        if request.GET.get('noretry', '') != 'true':
            return redirect(settings.LOGOUT_URL_TEMPLATE % (
                settings.PROXY_BASE_URL,
                settings.FORCE_SCRIPT_NAME[:-1] + '/login%3Fnoretry=true'))

        return render(request, '407.html')

    if timezone.now() - request.user.last_login > datetime.timedelta(minutes=1):
        request.user.last_login = timezone.now()
        request.user.save()

    copy_session_to_db(request, request.user)

    return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/overview')


def logout(request):
    """
    Clear session and log out of BCeID
    """
    request.session.flush()

    response = redirect(settings.LOGOUT_URL)

    if settings.DEPLOYMENT_TYPE in ['localdev', 'minishift']:
        response = redirect('/')

    return response


@bceid_required
@intercept
def overview(request):
    """
    Dashboard: Process overview page.
    """
    responses_dict_by_step = get_responses_from_db_grouped_by_steps(request.user)

    # Add step status dictionary
    responses_dict_by_step['step_status'] = get_step_status(responses_dict_by_step)
    responses_dict_by_step['active_page'] = 'overview'
    responses_dict_by_step['derived'] = get_derived_data(get_responses_from_db(request.user))

    response = render(request, 'overview.html', context=responses_dict_by_step)

    # set this session variable after the page is already rendered
    request.session['viewed_dashboard_during_session'] = True

    return response


@bceid_required
def dashboard_nav(request, nav_step):
    """
    Dashboard: All other pages
    """
    responses_dict = get_responses_from_db(request.user)
    responses_dict['active_page'] = nav_step
    template_name = 'dashboard/%s.html' % nav_step
    return render(request, template_name=template_name, context=responses_dict)


@bceid_required
def question(request, step, sub_step=None):
    """
    View for rendering main divorce questionaire questions
    """
    sub_page_template = '_{}'.format(sub_step) if sub_step else ''
    template = 'question/%02d_%s%s.html' % (template_step_order[step], step, sub_page_template)

    responses_dict_by_step = get_responses_from_db_grouped_by_steps(request.user, True)
    step_status = get_step_status(responses_dict_by_step)
    if step == "review":
        responses_dict = responses_dict_by_step
        derived = get_derived_data(get_responses_from_db(request.user))
    else:
        show_errors = step_status.get(step) == 'Started'
        responses_dict = get_responses_from_db(request.user, show_errors=show_errors, step=step, substep=sub_step)
        derived = get_derived_data(responses_dict)

    # Add step status dictionary
    responses_dict['step_status'] = step_status

    responses_dict['active_page'] = step
    # If page is filing location page, add registries dictionary for list of court registries
    if step == "location":
        responses_dict['registries'] = sorted(list_of_registries)

    responses_dict['sub_step'] = sub_step
    responses_dict['derived'] = derived

    return render(request, template_name=template, context=responses_dict)


def page_not_found(request, exception, template_name='404.html'):
    """
    404 Error Page
    """
    return render(request, template_name, status=404)


def server_error(request, template_name='500.html'):
    """
    500 Error Page
    """
    return render(request, template_name, status=500)


def legal(request):
    """
    Legal Information page
    """
    return render(request, 'legal.html', context={'active_page': 'legal'})


def acknowledgements(request):
    """
    Acknowledgements page
    """
    return render(request, 'acknowledgements.html', context={'active_page': 'acknowledgements'})

def contact(request):
    """
    Contact Us page
    """
    return render(request, 'contact-us.html', context={'active_page': 'contact'})

@bceid_required
def intercept_page(request):
    """
    On intercept, show the Orders page to get the requested orders before the
    user sees the nav on the left, so that it's already customized to their
    input.
    """
    template = 'question/%02d_%s.html' % (template_step_order['orders'], 'orders')
    responses_dict = get_responses_from_db(request.user)
    responses_dict['intercepted'] = True

    return render(request, template_name=template, context=responses_dict)

