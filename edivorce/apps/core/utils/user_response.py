from edivorce.apps.core.models import UserResponse, Question
from edivorce.apps.core.utils.question_step_mapping import question_step_mapping


def get_responses_from_db(bceid_user):
    responses = UserResponse.objects.filter(bceid_user=bceid_user)
    responses_dict = {}
    for answer in responses:
        responses_dict[answer.question.key] = answer.value
    return responses_dict


def get_responses_from_db_grouped_by_steps(bceid_user):
    """ Group questions and responses by steps they belong to """
    responses = UserResponse.objects.filter(bceid_user=bceid_user)
    responses_dict = {}
    for step, questions in question_step_mapping.items():
        responses_dict[step] = responses.filter(question_id__in=questions).exclude(value__in=['', '[]', '[["",""]]']).order_by('question').values('question_id', 'value', 'question__name', 'question__required', 'question__conditional_target', 'question__reveal_response')
    return responses_dict


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


def get_responses_from_session(request):
    return sorted(request.session.items())


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


def is_complete(step, lst):
    """
    Check required field of question for complete state
    Required: question is always require user response to be complete
    Conditional: question itself is required and depends on the response to this question,
                 optional question may be also required
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
        if not has_value(question_key, lst):
            complete = False
            missing_responses += [question_key]

    for question in conditional_list:
        # find the response to the conditional target
        for target in lst:
            if target["question_id"] == question.conditional_target:
                if condition_met(question.reveal_response, target, lst):
                    # question is required
                    if not has_value(question.key, lst):
                        complete = False
                        missing_responses += [question.key]

    return complete, missing_responses


def condition_met(reveal_response, target, lst):

    # return false if the condition was not met
    if target["value"] != reveal_response:
        return False

    # return true if the target is not Conditional
    if target['question__required'] != 'Conditional':
        return True
    else:
        # if the target is Conitional and the condition was met, check the target next
        reveal_response = target["question__reveal_response"]
        conditional_target = target["question__conditional_target"]
        for new_target in lst:
            if new_target["question_id"] == conditional_target:
                # recursively search up the tree
                return condition_met(reveal_response, new_target, lst)

        # if the for loop above didn't find the target, then the target question
        # is unanswered and the condition was not met
        return False

def has_value(key, lst):
    for user_response in lst:
        if user_response["question_id"] == key:
            answer = user_response["value"]
            if answer != "" and answer != "[]" and answer != '[["",""]]':
                return True
    return False

