from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from edivorce.apps.core.utils.derived import get_derived_data
from ..decorators import intercept, prequal_completed
from ..utils.efiling_documents import forms_to_file
from ..utils.question_step_mapping import list_of_registries
from ..utils.step_completeness import get_error_dict, get_missed_question_keys, get_step_completeness, is_complete, get_formatted_incomplete_list
from ..utils.template_step_order import template_step_order
from ..utils.user_response import (
    get_data_for_user,
    copy_session_to_db,
    get_step_responses,
    get_responses_from_session,
    get_responses_from_session_grouped_by_steps,
)


def home(request):
    """
    This is the homepage
    """
    # if the user is returning from BCeID registration, then log them in to the site
    if request.user.is_authenticated and request.session.get('went_to_register', False):
        request.session['went_to_register'] = False
        return redirect('oidc_authentication_init')

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
        responses_dict = get_data_for_user(request.user)
        responses_dict['active_page'] = 'prequalification'
        responses_dict['derived'] = get_derived_data(responses_dict)
        responses_by_step = get_step_responses(responses_dict)
        step_status = get_step_completeness(responses_by_step)
        responses_dict['step_status'] = step_status

    return render(request, template_name=template, context=responses_dict)


def success(request):
    """
    This page is shown if the user passes the qualification test
    """
    if request.user.is_authenticated:
        responses = get_data_for_user(request.user)
        prequal_responses = get_step_responses(responses)['prequalification']
    else:
        prequal_responses = get_responses_from_session_grouped_by_steps(request)['prequalification']
    complete = is_complete(prequal_responses)

    if complete:
        if request.user.is_authenticated:
            return redirect(reverse('overview'))
        else:
            return render(request, 'success.html', context={'register_url': settings.REGISTER_BCEID_URL, 'register_sc_url': settings.REGISTER_BCSC_URL})
    return redirect(reverse('incomplete'))


def incomplete(request):
    """
    This page is shown if the user misses any pre-qualification questions
    """
    if request.user.is_authenticated:
        responses = get_data_for_user(request.user)
        prequal_responses = get_step_responses(responses)
    else:
        prequal_responses = get_responses_from_session_grouped_by_steps(request)
    missed_question_keys = get_missed_question_keys(prequal_responses, 'prequalification')
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
    return redirect(settings.REGISTER_BCEID_URL)


def register_sc(request):
    """
    Sets a session variable and redirects users to register for BC Services Card
    """
    if settings.DEPLOYMENT_TYPE in ['localdev', 'minishift']:
        return render(request, 'localdev/register.html')

    request.session['went_to_register'] = True
    return redirect(settings.REGISTER_BCSC_URL)


def after_login(request):
    if not request.user.is_authenticated:
        return render(request, '407.html')

    copy_session_to_db(request, request.user)

    return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/overview')


@login_required
@prequal_completed
@intercept
def overview(request):
    """
    Dashboard: Process overview page.
    """
    responses_dict = get_data_for_user(request.user)
    responses_dict_by_step = get_step_responses(responses_dict)

    # Add step status dictionary
    step_status = get_step_completeness(responses_dict_by_step)
    responses_dict_by_step['step_status'] = step_status
    responses_dict_by_step['active_page'] = 'overview'
    responses_dict_by_step['derived'] = get_derived_data(responses_dict)

    # Dashnav needs filing option to determine which steps to show
    for question in responses_dict_by_step['signing_filing']:
        responses_dict_by_step[question['question_id']] = question['value']

    response = render(request, 'overview.html', context=responses_dict_by_step)

    # set this session variable after the page is already rendered
    request.session['viewed_dashboard_during_session'] = True

    return response


@login_required
@prequal_completed
def dashboard_nav(request, nav_step):
    """
    Dashboard: All other pages
    """
    responses_dict = get_data_for_user(request.user)
    responses_dict['active_page'] = nav_step
    template_name = 'dashboard/%s.html' % nav_step
    if nav_step in ('print_form', 'swear_forms', 'next_steps', 'final_filing') and responses_dict.get('court_registry_for_filing'):
        _add_court_registry_address(responses_dict)
    if nav_step in ('print_form', 'initial_filing', 'final_filing'):
        _add_question_errors(responses_dict)
    if nav_step in ('initial_filing', 'final_filing'):
        _add_error_messages(nav_step, request, responses_dict)

    responses_dict['derived'] = get_derived_data(responses_dict)
    return render(request, template_name=template_name, context=responses_dict)


def _add_court_registry_address(responses_dict):
    responses_dict['court_registry_for_filing_address'] = f"123 {responses_dict.get('court_registry_for_filing')} St"
    responses_dict['court_registry_for_filing_postal_code'] = 'V0A 1A1'


def _add_question_errors(responses_dict):
    responses_dict_by_step = get_step_responses(responses_dict)
    responses_dict.update(get_error_dict(responses_dict_by_step))


def _add_error_messages(nav_step, request, responses_dict):
    initial = 'initial' in nav_step
    uploaded, _ = forms_to_file(responses_dict, initial=initial)
    responses_dict['form_types'] = uploaded
    if request.GET.get('cancelled'):
        messages.add_message(request, messages.ERROR,
                             'You have cancelled the filing of your documents. '
                             'You can complete the filing process at your convenience.')
    elif request.GET.get('no_connection'):
        messages.add_message(request, messages.ERROR,
                             'The connection to the BC Government’s eFiling Hub is currently not working. '
                             'This is a temporary problem. '
                             'Please try again now and if this issue persists try again later.')
    elif request.GET.get('message'):
        messages.add_message(request, messages.ERROR, request.GET.get('message'))


@login_required
@prequal_completed
def question(request, step, sub_step=None):
    """
    View for rendering main divorce questionaire questions
    """
    sub_page_template = '_{}'.format(sub_step) if sub_step else ''
    template = 'question/%02d_%s%s.html' % (template_step_order[step], step, sub_page_template)

    if step == "review":
        data_dict = get_data_for_user(request.user)
        responses_dict_by_step = get_step_responses(data_dict)
        step_status = get_step_completeness(responses_dict_by_step)
        data_dict.update(get_error_dict(responses_dict_by_step))
        derived = get_derived_data(data_dict)
        responses_dict = responses_dict_by_step
    else:
        responses_dict = get_data_for_user(request.user)
        responses_dict_by_step = get_step_responses(responses_dict)
        step_status = get_step_completeness(responses_dict_by_step)
        responses_dict.update(get_error_dict(responses_dict_by_step, step, sub_step))
        derived = get_derived_data(responses_dict)

    # Add step status dictionary
    responses_dict['step_status'] = step_status

    responses_dict['active_page'] = step
    # If page is filing location page, add registries dictionary for list of court registries
    if step == "location":
        responses_dict['registries'] = sorted(list_of_registries.keys())

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


@login_required
def intercept_page(request):
    """
    On intercept, show the Orders page to get the requested orders before the
    user sees the nav on the left, so that it's already customized to their
    input.
    """
    template = 'question/%02d_%s.html' % (template_step_order['orders'], 'orders')
    responses_dict = get_data_for_user(request.user)
    responses_dict['intercepted'] = True

    return render(request, template_name=template, context=responses_dict)
