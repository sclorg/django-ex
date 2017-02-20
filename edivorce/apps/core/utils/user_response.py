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
        responses_dict[step] = responses.filter(question_id__in=questions)
    return responses_dict


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
            if UserResponse.objects.filter(bceid_user=bceid_user, question=q).exists():
                UserResponse.objects.update(bceid_user=bceid_user,
                                            question=q,
                                            value=request.session.get(q.key))
            else:
                UserResponse.objects.create(bceid_user=bceid_user,
                                            question=q,
                                            value=request.session.get(q.key))


                # clear the response from the session
            request.session[q.key] = None
