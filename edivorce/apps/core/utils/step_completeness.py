from django.urls import reverse

from edivorce.apps.core.models import Question
from edivorce.apps.core.utils.question_step_mapping import children_substep_question_mapping, page_step_mapping, pre_qual_step_question_mapping, question_step_mapping
from edivorce.apps.core.utils.conditional_logic import get_cleaned_response_value


class Status:
    STARTED = "Started"
    COMPLETED = "Completed"
    SKIPPED = "Skipped"
    NOT_STARTED = "Not started"
    HIDDEN = "Hidden"


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
    Accepts a dictionary of {step: [{question__name, question_id, value, error}]} <-- from get_step_responses
    Returns {step: status, substep: status}
    """
    status_dict = {}
    has_responses = False
    reversed_steps = list(question_step_mapping.keys())[::-1]
    for step in reversed_steps:
        question_dicts = questions_by_step[step]
        status, has_responses = _get_step_status(question_dicts, has_responses)
        status_dict[step] = status

    has_responses = False
    reversed_substeps = list(children_substep_question_mapping.keys())[::-1]
    for substep in reversed_substeps:
        substep_questions = children_substep_question_mapping[substep]
        question_dicts = [question_data for question_data in questions_by_step['your_children'] if question_data['question_id'] in substep_questions]
        status, has_responses = _get_step_status(question_dicts, has_responses)
        status_dict[f'children__{substep}'] = status

    return status_dict


def has_required_questions(question_dicts):
    return any([question for question in question_dicts if question['question__required'] != ''])


def _get_step_status(question_dicts, has_responses):
    if not step_started(question_dicts):
        if not has_required_questions(question_dicts):
            status = Status.HIDDEN
        elif not has_responses:
            status = Status.NOT_STARTED
        else:
            status = Status.SKIPPED
    else:
        has_responses = True
        complete = is_complete(question_dicts)
        if complete:
            status = Status.COMPLETED
        else:
            status = Status.STARTED
    return status, has_responses


def step_started(question_list):
    for question_dict in question_list:
        if get_cleaned_response_value(question_dict['value']):
            return True
    return False


def is_complete(question_list):
    for question_dict in question_list:
        if question_dict['error']:
            return False
    return True


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


def get_error_dict(questions_by_step, step=None, substep=None):
    """
    Accepts questions dict of {step: [{question_dict}]} and a step (and substep)
    Returns a dict of {question_key_error: True} for missing questions that are part of that step (and substep)
    """
    responses_dict = {}
    if step:
        question_step = page_step_mapping[step]
        step_questions = questions_by_step.get(question_step)
    else:
        step_questions = []
        for questions in questions_by_step.values():
            step_questions.extend(questions)
    # Since the Your children substep only has one question, show error if future children questions have been answered
    children_substep_and_step_started = substep == 'your_children' and step_started(step_questions)

    if substep:
        substep_questions = children_substep_question_mapping[substep]
        step_questions = list(filter(lambda question_dict: question_dict['question_id'] in substep_questions, step_questions))

    show_section_errors = step_started(step_questions) and not is_complete(step_questions)
    if show_section_errors or children_substep_and_step_started:
        for question_dict in step_questions:
            if question_dict['error']:
                field_error_key = question_dict['question_id'] + '_error'
                responses_dict[field_error_key] = True
    return responses_dict


def get_missed_question_keys(questions_by_step, step):
    """
    Accepts questions dict of {step: [{question_dict}]} and a step
    Returns a list of [question_key] for missing questions that are part of that step
    """
    missed_questions = []
    question_step = page_step_mapping[step]
    step_questions = questions_by_step.get(question_step)
    for question_dict in step_questions:
        if question_dict['error']:
            missed_questions.append(question_dict['question_id'])
    return missed_questions
