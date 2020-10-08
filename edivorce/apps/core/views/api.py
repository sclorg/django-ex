import json
import re

from django.http import Http404, HttpResponse, HttpResponseGone, HttpResponseNotFound
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from PIL import Image

from ..models import Document, Question
from ..serializer import CreateDocumentSerializer, DocumentMetadataSerializer, UserResponseSerializer
from ..utils.question_step_mapping import question_step_mapping
from ..utils.user_response import save_to_session, save_to_db


class UserResponseHandler(APIView):
    def post(self, request):
        if request.data == {}:
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = UserResponseSerializer(data=request.data)
        question_key = request.data['question']

        value = request.data['value'].replace('<', '&lt;').replace('>', '&gt;')
        user_attribute_updated = False
        try:
            try:
                question = Question.objects.get(pk=question_key)
            except Question.DoesNotExist:
                question = None

            if question is not None:
                # As a result of discussion, decide to escape < and > only
                if request.user.is_authenticated:
                    save_to_db(serializer, question, value, request.user)
                else:
                    # only prequalification questions can be answered when you
                    # aren't logged into BCeID
                    if question_key not in question_step_mapping['prequalification']:
                        return Response(data="Not logged in",
                                        status=status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED)
                    save_to_session(request, question, value)
            else:
                if request.user.is_authenticated and hasattr(request.user, question_key):
                    setattr(request.user, question_key, value == 'true')
                    request.user.save()
                    user_attribute_updated = True
        except Exception as e:
            if question is None and not user_attribute_updated:
                return Response(data="Question: '%s' does not exist" % question_key,
                                status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_500_INTERNAL_ERROR)

        return Response(status=status.HTTP_200_OK)


def court_location(request, city):
    data = {
        'city': city,
        'address': f'123 {city} St',
        'postal_code': 'V0A 0A0',
    }
    return HttpResponse(content=json.dumps(data), status=status.HTTP_200_OK)


class DocumentCreateView(CreateAPIView):
    serializer_class = CreateDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Document.objects.all()


class DocumentView(RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentMetadataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        doc = Document.objects.filter(bceid_user=self.request.user, **self.kwargs).first()
        if not doc:
            raise Http404("Document not found")
        elif not doc.file_exists():
            doc.get_documents_in_form().delete()
            raise Http404("Document no longer exists")
        else:
            return doc

    def retrieve(self, request, *args, **kwargs):
        """ Return the file instead of meta data """
        document = self.get_object()
        content_type = Document.content_type_from_filename(document.filename)

        # If file doesn't exist anymore, delete it
        try:
            file_contents = document.file.read()
        except TypeError:
            document.delete()
            return HttpResponseGone('File no longer exists')
        return HttpResponse(file_contents, content_type=content_type)


def get_document_file_by_key(request, file_key, rotation):
    file = Document.get_file(file_key)
    if not file:
        return HttpResponseNotFound()
    content_type = Document.content_type_from_filename(file.name)

    # if it's a PDF or it doesn't require rotation
    if content_type == 'application/pdf' or rotation == 0:
        try:
            return HttpResponse(file, content_type=content_type)
        except TypeError:
            raise Http404("File not found")

    # if the file needs to be rotated
    rot_img = __rotate_image(file, rotation)
    extension = __get_file_extension(file)

    try:
        response = HttpResponse(content_type=content_type)
        rot_img.save(response, extension)
        return response
    except TypeError:
        raise Http404("File not found")


def __get_file_extension(file):
    extension = re.split(r'[\._]', file.name.upper())[-1]
    if extension == "JPG" or extension == "JPE":
        return "JPEG"
    return extension


def __rotate_image(file, rotation):
    im = Image.open(file)

    if rotation == 90:
        return im.transpose(Image.ROTATE_270)
    elif rotation == 270:
        return im.transpose(Image.ROTATE_90)
    else:
        return im.transpose(Image.ROTATE_180)
