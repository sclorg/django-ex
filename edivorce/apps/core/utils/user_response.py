from edivorce.apps.core.models import UserResponse, Question
from edivorce.apps.core.utils.question_step_mapping import question_step_mapping
from edivorce.apps.core.utils.step_completeness import evaluate_numeric_condition
from collections import OrderedDict


def get_responses_from_db(bceid_user, show_errors=False, step=None, substep=None):
    """ Get UserResponses from the database for a user."""
    married, married_questions, responses = __get_data(bceid_user)
    responses_dict = {}
    for answer in responses:
        if not married and answer.question_id in married_questions:
            responses_dict[answer.question.key] = ''
        elif answer.value.strip('[').strip(']'):
            responses_dict[answer.question.key] = answer.value
    if show_errors:
        step_questions = question_step_mapping.get(step, [])
        questions = Question.objects.filter(key__in=step_questions)
        for question in questions:
            if responses_dict.get(question.key):
                error = False
            elif question.required == 'Required':
                error = True
            elif question.required == 'Conditional':
                conditional_response = UserResponse.objects.filter(question=question.conditional_target).first()
                error = conditional_response and conditional_response.value == question.reveal_response
            else:
                error = False
            responses_dict[f'{question.key}_error'] = error
    return responses_dict


def get_responses_from_db_grouped_by_steps(bceid_user, hide_failed_conditionals=False):
    """
    Group questions and responses by steps to which they belong

    `hide_failed_conditionals` goes through the responses after grouping and
    tests their conditionality.  If they fail, the response is blanked (this is
    to hide conditional responses that are no longer applicable but haven't been
    erased, mainly for the question review page).
    """
    married, married_questions, responses = __get_data(bceid_user)
    responses_dict = {}

    for step, questions in question_step_mapping.items():

        lst = []
        step_responses = responses.filter(question_id__in=questions).exclude(
            value__in=['', '[]', '[["",""]]']).order_by('question')

        for answer in step_responses:
            if not married and answer.question_id in married_questions:
                value = ''
            else:
                value = answer.value

            lst += [{'question__conditional_target': answer.question.conditional_target,
                     'question__reveal_response': answer.question.reveal_response,
                     'value': value,
                     'question__name': answer.question.name,
                     'question__required': answer.question.required,
                     'question_id': answer.question.pk}]

        # This was added for DIV-514, where the user entered a name change for
        # their spouse but then said 'no', they won't be changing their name.
        # Since we don't blank related answers, we need to hide it dynamically.
        # This only works for questions in the same step.
        if hide_failed_conditionals:
            values = {q['question_id']: q['value'] for q in lst}
            for q in lst:
                if q['question__required'] != 'Conditional':
                    continue
                target = q['question__conditional_target']
                if target.startswith('['):
                    targets = target.strip('[]').split(',')
                    filtered_targets = [t for t in targets if t not in values]
                    # filtered_targets = list(filter(lambda t: t not in values, targets))
                    if len(filtered_targets):
                        continue

                    reveal_responses = dict(zip(targets, q['question__reveal_response'].strip('[]').split(',')))
                    present = [val for key, val in reveal_responses.items() if val != values[key]]
                    if len(present):
                        q['value'] = ''
                    continue

                if target not in values:
                    continue
                numeric_condition = evaluate_numeric_condition(values[target], q['question__reveal_response'])
                if numeric_condition is None:
                    if q['question__reveal_response'].startswith('!'):
                        if values[target] == "" or values[target] == q['question__reveal_response'][1:]:
                            q['value'] = ''
                    elif q['question__reveal_response'] and q['question__reveal_response'] != values[target]:
                        q['value'] = ''
                elif numeric_condition is False:
                    q['value'] = ''

        responses_dict[step] = lst

    return responses_dict


def get_responses_from_session(request):
    return OrderedDict(sorted(request.session.items()))


def get_responses_from_session_grouped_by_steps(request):
    question_list = Question.objects.filter(key__in=question_step_mapping['prequalification'])

    lst = []

    for question in question_list:
        lst += [{'question__conditional_target': question.conditional_target,
                 'question__reveal_response': question.reveal_response,
                 'value': request.session.get(question.pk, ''),
                 'question__name': question.name,
                 'question__required': question.required,
                 'question_id': question.pk}]

    return {'prequalification': lst}


def save_to_db(serializer, question, value, bceid_user):
    """ Saves form responses to the database """
    data = {'bceid_user': bceid_user,
            'question': question,
            'value': value}
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


def __get_data(bceid_user):
    """
    Gets UserResponses from the database for a user, plus a boolean indicating
    if the user is married or common-law, and a list of questions that only apply to
    married couples
    """
    COMMON_LAW = 'Living together in a marriage like relationship'
    MARRIED = 'Legally married'

    responses = UserResponse.objects.filter(bceid_user=bceid_user).select_related('question')
    married_status = responses.filter(question_id='married_marriage_like')

    if married_status.count() > 0:
        married = married_status[0].value != COMMON_LAW
    else:
        married = False

    married_questions = list(
        Question.objects.filter(reveal_response=MARRIED).values_list("key", flat=True))
    return married, married_questions, responses
