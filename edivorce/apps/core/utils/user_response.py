from edivorce.apps.core.models import UserResponse, Question
from edivorce.apps.core.utils.question_step_mapping import question_step_mapping, complete_state_for_step
from copy import deepcopy
import json

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
        responses_dict[step] = responses.filter(question_id__in=questions).exclude(value__in=['', '[]']).order_by('question').values('question_id', 'value', 'question__name')
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
    if not lst:
        return False
    required_dict = deepcopy(complete_state_for_step)
    if step in required_dict:
        required_list = required_dict[step]['required']
        conditional_list = required_dict[step]['conditional'] if 'conditional' in required_dict[step] else []

        for question in lst:
            q_id = question['question_id']
            value = question['value']
            if value != '[]' and value.strip() != '':
                if q_id in required_list:
                    required_list.remove(q_id)
                elif q_id in conditional_list:
                    if q_id in conditional_list and value == conditional_list[q_id][0]:
                        key_in_list = False
                        hidden_q_id = conditional_list[q_id][1]
                        for key in lst:
                            if key['question_id'] == hidden_q_id:
                                if (hidden_q_id == 'other_name_you' or hidden_q_id == 'other_name_spouse') and not json.loads(key['value'])[0][1]:
                                    break
                                else:
                                    key_in_list = True
                                    break
                        if key_in_list is False:
                            return False
                        conditional_list.pop(q_id, None)
                    else:
                        conditional_list.pop(q_id, None)
        if not required_list and not conditional_list:
            return True
    return False
