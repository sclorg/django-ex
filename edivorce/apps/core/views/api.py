from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from ..models import Question
from ..serializer import UserResponseSerializer
from ..utils.question_step_mapping import question_step_mapping
from ..utils.user_response import save_to_session, save_to_db


class UserResponseHandler(APIView):
    def post(self, request):
        if request.data == {}:
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = UserResponseSerializer(data=request.data)
        question_key = request.data['question']

        try:
            question = Question.objects.get(pk=question_key)
            # As a result of discussion, decide to escape < and > only
            value = request.data['value'].replace('<', '&lt;').replace('>', '&gt;')
            if request.user.is_authenticated():
                save_to_db(serializer, question, value, request.user)
            else:
                # only prequalification questions can be answered when you
                # aren't logged into BCeID
                if question_key not in question_step_mapping['prequalification']:
                    return Response(data="Not logged in",
                                    status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)
                save_to_session(request, question, value)
        except Question.DoesNotExist:
            return Response(data="Question: '%s' does not exist" % question_key,
                            status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
