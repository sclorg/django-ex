import base64
import random

from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from ..decorators import prequal_completed
from ..models import Document, UserResponse
from ..utils.efiling_documents import forms_to_file
from ..utils.efiling_packaging import EFilingPackaging
from ..utils.efiling_submission import EFilingSubmission
from ..utils.user_response import get_data_for_user


@login_required
@prequal_completed
def submit_initial_files(request):
    return _submit_files(request, initial=True)


@login_required
@prequal_completed
def submit_final_files(request):
    return _submit_files(request, initial=False)


def _submit_files(request, initial=False):
    """ App flow logic """
    responses_dict = get_data_for_user(request.user)

    return_val = _validate_and_submit_documents(request, responses_dict, initial=initial)
    # Inelegant way to handle eFiling enabled flag. If one value was returned, it's a redirect.
    if not isinstance(return_val, tuple):
        return return_val
    errors, hub_redirect_url = return_val

    if hub_redirect_url:
        return redirect(hub_redirect_url)

    if initial:
        original_step = 'initial_filing'
        next_page = 'wait_for_number'
    else:
        original_step = 'final_filing'
        next_page = 'next_steps'

    if errors:
        next_page = original_step
        if not isinstance(errors, list):
            errors = [errors]
        for error in errors:
            messages.add_message(request, messages.ERROR, error)

    responses_dict['active_page'] = next_page

    return redirect(reverse('dashboard_nav', kwargs={'nav_step': next_page}), context=responses_dict)


def _validate_and_submit_documents(request, responses, initial=False):
    """ Validation and submission logic """
    user = request.user
    errors = []
    if not initial:
        user_has_submitted_initial = responses.get('initial_filing_submitted') == 'True'
        if not user_has_submitted_initial:
            errors.append(
                "You must file the initial filing first before submitting the final filing.")
        court_file_number = responses.get('court_file_number')
        if not court_file_number:
            errors.append("You must input your Court File Number")

    uploaded, generated = forms_to_file(responses, initial)
    for form in uploaded:
        docs = Document.objects.filter(
            bceid_user=user, doc_type=form['doc_type'], party_code=form.get('party_code', 0))
        if docs.count() == 0:
            errors.append(f"Missing documents for {Document.form_types[form['doc_type']]}")

    if errors:
        return errors, None

    if not settings.EFILING_HUB_ENABLED:
        return _after_submit_files(request, initial)

    msg, redirect_url = _package_and_submit(request, uploaded, generated, responses, initial)

    if msg != 'success':
        errors.append(msg)
        return errors, None

    if redirect_url:
        return None, redirect_url

    return None, None


def _package_and_submit(request, uploaded, generated, responses, initial):
    """ Build the efiling package and submit it to the efiling hub """
    hub = EFilingSubmission(initial_filing=initial)
    packaging = EFilingPackaging(initial_filing=initial)
    post_files, documents = packaging.get_files(request, responses, uploaded, generated)
    redirect_url, msg = hub.upload(
        request,
        post_files,
        documents,
        parties=packaging.get_parties(responses),
        location=packaging.get_location(responses)
    )
    return msg, redirect_url


@login_required
@prequal_completed
def after_submit_initial_files(request):
    return _after_submit_files(request, initial=True)


@login_required
@prequal_completed
def after_submit_final_files(request):
    return _after_submit_files(request, initial=False)


def _after_submit_files(request, initial=False):
    responses_dict = get_data_for_user(request.user)
    if initial:
        next_page = 'wait_for_number'
    else:
        next_page = 'next_steps'

    user = request.user

    prefix = 'initial' if initial else 'final'
    _save_response(user, f'{prefix}_filing_submitted', 'True')

    if not initial:
        _save_response(user, f'final_filing_status', 'Submitted')

    package_number = _get_package_number(request)

    _save_response(user, f'{prefix}_filing_package_number', package_number)

    if settings.DEPLOYMENT_TYPE == 'localdev':
        base_url = 'https://dev.justice.gov.bc.ca'
    else:
        base_url = settings.PROXY_BASE_URL

    receipt_link = base_url + '/cso/filing/status/viewDocument.do?actionType=viewReceipt&packageNo=' + package_number
    _save_response(user, f'{prefix}_filing_receipt_link', receipt_link)

    package_link = base_url + '/cso/accounts/bceidNotification.do?packageNo=' + package_number
    _save_response(user, f'{prefix}_filing_package_link', package_link)

    responses_dict['active_page'] = next_page

    return redirect(reverse('dashboard_nav', kwargs={'nav_step': next_page}), context=responses_dict)


def _get_package_number(request):
    if settings.EFILING_HUB_ENABLED:
        base64_message = request.GET.get('packageRef', '')
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        parts = message.split('=')
        if len(parts) == 2:
            return parts[1]
    else:
        # Generate a random string in format 000-000-000
        package_number_parts = []
        for _ in range(3):
            num = ''
            for _ in range(3):
                num += str(random.randint(0, 9))
            package_number_parts.append(num)
        return '-'.join(package_number_parts)


def _save_response(user, question, value):
    response, _ = UserResponse.objects.get_or_create(bceid_user=user, question_id=question)
    response.value = value
    response.save()
