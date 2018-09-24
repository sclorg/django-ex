from django.urls import reverse

from edivorce.apps.core.models import Question
from edivorce.apps.core.utils.question_step_mapping import question_step_mapping, pre_qual_step_question_mapping


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


def get_step_status(responses_by_step):
    status_dict = {}
    for step, lst in responses_by_step.items():
        if not lst:
            status_dict[step] = "Not started"
        else:
            if is_complete(step, lst)[0]:
                status_dict[step] = "Complete"
            else:
                status_dict[step] = "Started"
    return status_dict


def is_complete(step, lst):
    """
    Check required field of question for complete state
    Required: question is always require user response to be complete
    Conditional: Optional question needed depends on reveal_response value of conditional_target.
    """
    if not lst:
        return False, []
    question_list = Question.objects.filter(key__in=question_step_mapping[step])
    required_list = list(question_list.filter(required='Required').values_list("key", flat=True))
    conditional_list = list(question_list.filter(required='Conditional'))

    complete = True
    missing_responses = []

    for question_key in required_list:
        # everything in the required_list is required
        if not __has_value(question_key, lst):
            complete = False
            missing_responses += [question_key]

    for question in conditional_list:
        # find the response to the conditional target
        for target in lst:
            if target["question_id"] == question.conditional_target:
                if __condition_met(question.reveal_response, target, lst):
                    # the condition was met then the question is required.
                    # ... so check if it has a value
                    if not __has_value(question.key, lst):
                        complete = False
                        missing_responses += [question.key]

    return complete, missing_responses


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


def __condition_met(reveal_response, target, lst):
    # check whether using a numeric condition
    numeric_condition_met = evaluate_numeric_condition(target["value"], reveal_response)
    if numeric_condition_met is None:
        if target["value"] != reveal_response:
            return False
    elif numeric_condition_met is False:
        return False

    # return true if the target is not Conditional
    if target['question__required'] != 'Conditional':
        return True
    else:
        # if the target is Conditional and the condition was met, check the target next
        reveal_response = target["question__reveal_response"]
        conditional_target = target["question__conditional_target"]
        for new_target in lst:
            if new_target["question_id"] == conditional_target:
                # recursively search up the tree
                return __condition_met(reveal_response, new_target, lst)

        # if the for loop above didn't find the target, then the target question
        # is unanswered and the condition was not met
        return False


def __has_value(key, lst):
    for user_response in lst:
        if user_response["question_id"] == key:
            answer = user_response["value"]
            if answer != "" and answer != "[]" and answer != '[["",""]]':
                return True
    return False
