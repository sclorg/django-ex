from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from edivorce.apps.core.utils.user_response import save_to_session, save_to_db
from ..models import Question, BceidUser
from ..serializer import UserResponseSerializer


class UserResponseHandler(APIView):
    def post(self, request):
        serializer = UserResponseSerializer(data=request.data)

        try:
            question = Question.objects.get(pk=request.data['question'])
            value = request.data['value']
            if request.bceid_user.is_authenticated:
                user = BceidUser.objects.get(user_guid=request.bceid_user.guid)
                save_to_db(serializer, question, value, user)
            else:
                save_to_session(request, question, value)

        except Question.DoesNotExist:
            return Response(data="Question: '%s' does not exist" % request.data['question'], status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_200_OK)
