from edivorce.apps.core.models import UserResponse, Question
from edivorce.apps.core.utils import conditional_logic
from edivorce.apps.core.utils.conditional_logic import get_cleaned_response_value
from edivorce.apps.core.utils.question_step_mapping import page_step_mapping, question_step_mapping
from edivorce.apps.core.utils.step_completeness import evaluate_numeric_condition
from collections import OrderedDict


REQUIRED = 0
HIDDEN = 1
OPTIONAL = 2


def get_data_for_user(bceid_user):
    """
    Return a dictionary of {question_key: user_response_value}
    """
    responses = UserResponse.objects.filter(bceid_user=bceid_user)
    responses_dict = {}
    for response in responses:
        if response.value.strip('[').strip(']'):
            responses_dict[response.question_id] = response.value

    return responses_dict


def get_step_responses(responses_by_key):
    """
    Accepts a dictionary of {question_key: user_response_value} <-- from get_data_for_user
    Returns a dictionary of {step: [{question__name, question_id, value, error}]}
    """
    responses_by_step = {}
    for step in page_step_mapping.values():
        step_responses = questions_dict_for_step(responses_by_key, step)
        responses_by_step[step] = step_responses
    return responses_by_step


def questions_dict_for_step(responses_by_key, step):
    questions_dict = _get_questions_dict_set_for_step(step)
    step_responses = []
    for question in questions_dict:
        question_details = _get_question_details(question, questions_dict, responses_by_key)
        if question_details['show']:
            question_dict = questions_dict[question]
            question_dict['value'] = question_details['value']
            question_dict['error'] = question_details['error']

            step_responses.append(question_dict)
    return step_responses


def _get_questions_dict_set_for_step(step):
    questions = Question.objects.filter(key__in=question_step_mapping[step])
    questions_dict = {}
    for question in questions:
        question_dict = {
            'question__conditional_target': question.conditional_target,
            'question__reveal_response': question.reveal_response,
            'question__name': question.name,
            'question__required': question.required,
            'question_id': question.key,
        }
        questions_dict[question.pk] = question_dict
    return questions_dict


def _condition_met(target_response, reveal_response):
    # check whether using a numeric condition
    numeric_condition_met = evaluate_numeric_condition(target_response, reveal_response)
    if numeric_condition_met is None:
        # handle special negation options. ex) '!NO' matches anything but 'NO'
        if reveal_response.startswith('!'):
            if target_response == "" or target_response.lower() == reveal_response[1:].lower():
                return False
        elif str(target_response).lower() != reveal_response.lower():
            return False
    elif numeric_condition_met is False:
        return False
    return True


def _get_question_details(question, questions_dict, responses_by_key):
    """
    Return details for a question given the set of question details and user responses.
      value: The user's response to a question (or None if unanswered)
      error: True if the question has an error (e.g. required but not answered)
      show: False if the response shouldn't be displayed (e.g. don't show 'Also known as' name, but 'Does your spouse go by any other names' is NO)
    """
    required = False
    show = True
    question_required = _is_question_required(question, questions_dict, responses_by_key)
    if question_required == REQUIRED:
        required = True
        show = True
    elif question_required == HIDDEN:
        required = False
        show = False
    elif question_required == OPTIONAL:
        required = False
        show = True

    if show:
        value = None
        response = responses_by_key.get(question)
        if response:
            value = get_cleaned_response_value(response)
        error = required and not value
        if not error:
            error = _other_errors(question, value)
    else:
        value = None
        error = None

    details = {
        'value': value,
        'error': error,
        'show': show
    }
    return details


def _other_errors(question, value):
    if question == 'want_which_orders' and 'A legal end to the marriage' not in value:
        return True
    return False


def _is_question_required(question, questions_dict, responses_by_key):
    """
    returns REQUIRED, HIDDEN, or OPTIONAL
    raises KeyError if the question is conditional and improperly configured (for development testing purposes)
    """
    question_dict = questions_dict[question]
    if question_dict['question__required'] == 'Required':
        return REQUIRED
    elif question_dict['question__required'] == 'Conditional':
        target = question_dict.get('question__conditional_target')
        reveal_response = question_dict.get('question__reveal_response')
        if not target or not reveal_response:
            raise KeyError(f"Improperly configured question '{question}'. Needs target and reveal response")

        if target.startswith('determine_'):
            # Look for the right function to evaluate conditional logic
            derived_condition = getattr(conditional_logic, target)
            if not derived_condition:
                raise NotImplemented(target)
            result = derived_condition(responses_by_key)
            if result and _condition_met(result, reveal_response):
                return REQUIRED
            else:
                return HIDDEN
        elif target in questions_dict:
            target_question_requirement = _is_question_required(target, questions_dict, responses_by_key)
            if target_question_requirement == REQUIRED:
                target_response = responses_by_key.get(target)
                if target_response and _condition_met(target_response, reveal_response):
                    return REQUIRED
            return HIDDEN
        else:
            raise KeyError(f"Invalid conditional target '{target}' for question '{question}'")
    else:
        return OPTIONAL


def get_responses_from_session(request):
    return OrderedDict(sorted(request.session.items()))


def get_responses_from_session_grouped_by_steps(request):
    step_questions_dict = _get_questions_dict_set_for_step('prequalification')
    step_questions_list = []
    for question_key, question_dict in step_questions_dict.items():
        question_details = _get_question_details(question_key, step_questions_dict, request.session)
        question_dict['value'] = question_details['value']
        question_dict['error'] = question_details['error']
        step_questions_list.append(question_dict)

    return {'prequalification': step_questions_list}


def save_to_db(serializer, question, value, bceid_user):
    """ Saves form responses to the database """
    data = {'bceid_user': bceid_user,
            'question': question,
            'value': value.strip()}
    try:
        instance = UserResponse.objects.get(bceid_user=bceid_user, question=question)
        serializer.update(instance=instance, validated_data=data)
    except UserResponse.DoesNotExist:
        serializer.create(validated_data=data)


def save_to_session(request, question, value):
    """ Saves prequalifying responses to the user's session """
    request.session[question.pk] = value


def copy_session_to_db(request, bceid_user):
    """ Copies responses to pre-qualification questions from the user's session to the db """
    questions = Question.objects.all()

    for q in questions:
        if request.session.get(q.key) is not None:
            # copy the response to the database
            UserResponse.objects.update_or_create(
                bceid_user=bceid_user,
                question=q,
                defaults={'value': request.session.get(q.key)},
            )

            # clear the response from the session
            request.session[q.key] = None
