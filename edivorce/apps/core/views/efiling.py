from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from ..decorators import prequal_completed
from ..utils.cso_filing import file_documents
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
    if initial:
        original_step = 'initial_filing'
        next_page = 'wait_for_number'
    else:
        original_step = 'final_filing'
        next_page = 'next_steps'

    missing_forms, hub_redirect_url = file_documents(request, responses_dict, initial=initial)

    if hub_redirect_url:
        return redirect(hub_redirect_url)

    if missing_forms:
        next_page = original_step
        for form_name in missing_forms:
            messages.add_message(request, messages.ERROR, f'Missing documents for {form_name}')
    responses_dict['active_page'] = next_page

    return redirect(reverse('dashboard_nav', kwargs={'nav_step': next_page}), context=responses_dict)