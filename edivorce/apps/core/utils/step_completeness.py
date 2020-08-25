from django.urls import reverse

from edivorce.apps.core.models import Question
from edivorce.apps.core.utils.question_step_mapping import page_step_mapping, pre_qual_step_question_mapping
from edivorce.apps.core.utils.conditional_logic import get_cleaned_response_value


def evaluate_numeric_condition(target, reveal_response):
    """
    Tests whether the reveal_response contains a numeric condition.  If so, it will
    evaluate the numeric condition and return the results of that comparison.

    :param target: the questions value being tested against
    :param reveal_response: the numeric condition that will be evaluated against
    :return: boolean result of numeric condition evaluation or None if there is no
    numeric condition to evaluate.
    """
    if target == '':  # cannot evaluate if answer is blank
        return None

    if reveal_response.startswith('>='):
        return float(target) >= float(reveal_response[2:])
    elif reveal_response.startswith('<='):
        return float(target) <= float(reveal_response[2:])
    elif reveal_response.startswith('=='):
        return float(target) == float(reveal_response[2:])
    elif reveal_response.startswith('<'):
        return float(target) < float(reveal_response[1:])
    elif reveal_response.startswith('>'):
        return float(target) > float(reveal_response[1:])

    return None


def get_step_completeness(questions_by_step):
    """
    Accepts a dictionary of {step: {question_id: {question__name, question_id, value, error}}} <-- from get_step_responses
    Returns {step: status}, {step: [missing_question_key]}
    """
    status_dict = {}
    missing_response_dict = {}
    for step, question_list in questions_by_step.items():
        if not_started(question_list):
            status_dict[step] = "Not started"
        else:
            complete, missing_responses = is_complete(question_list)
            if complete:
                status_dict[step] = "Complete"
            else:
                missing_response_dict[step] = missing_responses
                status_dict[step] = "Started"
    return status_dict, missing_response_dict


def not_started(question_list):
    for question_dict in question_list:
        if get_cleaned_response_value(question_dict['value']):
            return False
    return True


def is_complete(question_list):
    missing_responses = []
    for question_dict in question_list:
        if question_dict['error']:
            missing_responses.append(question_dict)
    return len(missing_responses) == 0, missing_responses


def get_formatted_incomplete_list(missed_question_keys):
    """
    Returns a list of dicts that contain the following information for the question
    that was not answered.  Each dict contains the name of the question, as stored in
    the database, and the url of the page where the question is found.

    :param missed_question_keys:
    :return: list of dicts.
    """
    missed_questions = []
    for missed_question in Question.objects.filter(key__in=missed_question_keys):
        for step, questions in pre_qual_step_question_mapping.items():
            if missed_question.key in questions:
                missed_questions.append({
                    'title': missed_question.name,
                    'step_url': reverse('prequalification', kwargs={'step': step})
                })
    return missed_questions


def get_error_dict(step, missing_questions):
    """
    Returns a dict of {question_key_error: True} for any
    """
    responses_dict = {}
    question_step = page_step_mapping[step]
    for question_dict in missing_questions.get(question_step, []):
        field_error_key = question_dict['question_id'] + '_error'
        responses_dict[field_error_key] = True
    return responses_dict
