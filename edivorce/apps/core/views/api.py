import re

import graphene
import graphene_django
from django.http import Http404, HttpResponse, HttpResponseGone, HttpResponseNotFound
from graphql import GraphQLError
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

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


class DocumentCreateView(CreateAPIView):
    serializer_class = CreateDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Document.objects.all()


class DocumentMetaDataView(ListAPIView):
    serializer_class = DocumentMetadataSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        doc_type = self.kwargs['doc_type']
        party_code = self.kwargs['party_code']
        q = Document.objects.filter(doc_type=doc_type, party_code=party_code, bceid_user=self.request.user).order_by('sort_order')
        for doc in q:
            if not doc.file_exists():
                q.delete()
                return Document.objects.none()
        return q


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
        content_type = _content_type_from_filename(document.filename)

        # If file doesn't exist anymore, delete it
        try:
            file_contents = document.file.read()
        except TypeError:
            document.delete()
            return HttpResponseGone('File no longer exists')
        return HttpResponse(file_contents, content_type=content_type)


def get_document_file_by_key(request, file_key):
    file = Document.get_file(file_key)
    if not file:
        return HttpResponseNotFound()
    content_type = _content_type_from_filename(file.name)
    return HttpResponse(file, content_type=content_type)


def _content_type_from_filename(filename):
    content_types = {
        "pdf": "application/pdf",
        "gif": "image/gif",
        "png": "image/png",
        "jpe": "image/jpeg",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg"
    }
    extension = re.split(r'[\._]', filename.lower())[-1]
    content_type = content_types.get(extension)
    if not content_type:
        raise TypeError(f'Filetype "{extension}" not supported')
    return content_type


class DocumentType(graphene_django.DjangoObjectType):
    file_url = graphene.String(source='get_file_url')

    class Meta:
        model = Document


class Query(graphene.ObjectType):
    documents = graphene.List(DocumentType, doc_type=graphene.String(required=True), party_code=graphene.Int(required=True))

    def resolve_documents(self, info, **kwargs):
        if info.context.user.is_anonymous:
            raise GraphQLError('Unauthorized')
        q = Document.objects.filter(bceid_user=info.context.user, **kwargs)
        return q


class DocumentInput(graphene.InputObjectType):
    filename = graphene.String(required=True)
    size = graphene.Int(required=True)
    width = graphene.Int()
    height = graphene.Int()
    rotation = graphene.Int()


class DocumentMetaDataInput(graphene.InputObjectType):
    files = graphene.List(DocumentInput, required=True)
    doc_type = graphene.String(required=True)
    party_code = graphene.Int(required=True)


class UpdateMetadata(graphene.Mutation):
    class Arguments:
        input = DocumentMetaDataInput(required=True)

    documents = graphene.List(DocumentType)

    def mutate(self, info, **kwargs):
        if info.context.user.is_anonymous:
            raise GraphQLError('Unauthorized')
        input_ = kwargs['input']
        documents = Document.objects.filter(bceid_user=info.context.user, doc_type=input_['doc_type'], party_code=input_['party_code'])

        unique_files = [dict(s) for s in set(frozenset(d.items()) for d in input_['files'])]
        if documents.count() != len(input_['files']) or documents.count() != len(unique_files):
            raise GraphQLError("Invalid input: there must be the same number of files")

        for i, file in enumerate(input_['files']):
            try:
                doc = documents.get(filename=file['filename'], size=file['size'])
                doc.sort_order = i + 1
                doc.width = file.get('width', file.width)
                doc.height = file.get('height', file.height)
                doc.rotation = file.get('rotation', file.rotation)
                if doc.rotation not in [0, 90, 180, 270]:
                    raise GraphQLError(f"Invalid rotation {doc.rotation}, must be 0, 90, 180, 270")
                doc.save()
            except Document.DoesNotExist:
                raise GraphQLError(f"Couldn't find document '{file['filename']}' with size '{file['size']}'")
        return UpdateMetadata(documents=documents.all())


class Mutations(graphene.ObjectType):
    update_metadata = UpdateMetadata.Field()


graphql_schema = graphene.Schema(query=Query, mutation=Mutations)
