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
            if step != 'prequalification':
                if is_complete(step, lst):
                    status_dict[step] = "Complete"
                else:
                    status_dict[step] = "Started"
    return status_dict


def get_responses_from_session(request):
    return sorted(request.session.items())


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
        return False
    question_list = Question.objects.filter(key__in=question_step_mapping[step])
    required_list = list(question_list.filter(required='Required').values_list("key", flat=True))
    conditional_list = list(question_list.filter(required='Conditional').values_list("key", flat=True))
    for question in lst:
        q_val = question['value']
        if q_val != "" and q_val != "[]" and q_val != '[["",""]]':
            q_id = question['question_id']
            if q_id in required_list:
                required_list.remove(q_id)
            elif q_id in conditional_list:
                if q_val == question['question__reveal_response']:
                    key_in_list = False
                    for key in lst:
                        k_val = key['value']
                        if key['question_id'] == question['question__conditional_target']:
                            if k_val != "" and k_val != "[]" and k_val != '[["",""]]':
                                key_in_list = True
                                break
                    if key_in_list is False:
                        return False
                conditional_list.remove(q_id)
    if not required_list and not conditional_list:
        return True
    return False
