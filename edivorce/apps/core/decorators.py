from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse

from edivorce.apps.core.utils.question_step_mapping import pre_qual_step_question_mapping
from edivorce.apps.core.utils.step_completeness import get_missed_question_keys, is_complete
from edivorce.apps.core.utils.user_response import get_data_for_user, get_step_responses, questions_dict_for_step

base_url = settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1]


def intercept(function=None):
    """
    Decorator to redirect to intercept page
    """
    terms = {'question__key': 'want_which_orders'}

    def _dec(view_func):
        def _view(request, *args, **kwargs):
            if (request.user.is_authenticated and
                    not request.user.has_seen_orders_page and
                    not request.user.responses.filter(**terms).exists()):
                request.user.has_seen_orders_page = True
                request.user.save()
                return redirect(base_url + '/intercept')
            return view_func(request, *args, **kwargs)

        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    return _dec if function is None else _dec(function)


def prequal_completed(function=None):
    """
    View decorator to check if the user has completed the prequalification questions
    """
    def _dec(view_func):
        def _view(request, *args, **kwargs):
            if request.user.is_authenticated:
                responses = get_data_for_user(request.user)
                prequal_questions = questions_dict_for_step(responses, 'prequalification')
                complete = is_complete(prequal_questions)
                if complete:
                    return view_func(request, *args, **kwargs)
                else:
                    missing_questions = [question_dict['question_id'] for question_dict in prequal_questions if question_dict['error']]
                    for step, questions in pre_qual_step_question_mapping.items():
                        if missing_questions[0] in questions:
                            return redirect(reverse('prequalification', kwargs={'step': step}))
                    return redirect(reverse('prequalification', kwargs={'step': '01'}))
            else:
                return redirect('oidc_authentication_init')

        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    return _dec if function is None else _dec(function)
