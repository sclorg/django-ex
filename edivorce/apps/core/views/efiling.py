from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from ..decorators import prequal_completed
from ..utils.cso_filing import file_documents, after_file_documents
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
    responses_dict = get_data_for_user(request.user)

    errors, hub_redirect_url = file_documents(request, responses_dict, initial=initial)

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

    after_file_documents(request, initial=initial)

    responses_dict['active_page'] = next_page

    return redirect(reverse('dashboard_nav', kwargs={'nav_step': next_page}), context=responses_dict)
