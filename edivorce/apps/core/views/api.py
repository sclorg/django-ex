from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from edivorce.apps.core.utils.question_step_mapping import question_step_mapping
from edivorce.apps.core.utils.user_response import save_to_session, save_to_db
from ..models import Question, BceidUser
from ..serializer import UserResponseSerializer


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
            if request.bceid_user.is_authenticated:
                user = BceidUser.objects.get(user_guid=request.bceid_user.guid)
                save_to_db(serializer, question, value, user)
            else:
                # only prequalification questions can be answered when you aren't logged into BCeID
                if not question_key in question_step_mapping['prequalification']:
                    return Response(data="Not logged in", status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)
                
                save_to_session(request, question, value)

        except Question.DoesNotExist:
            return Response(data="Question: '%s' does not exist" % question_key, status=status.HTTP_400_BAD_REQUEST)

        response = Response(status=status.HTTP_200_OK)
        response['X-Debug-Auth-Type'] = request.bceid_user.type

        return response
