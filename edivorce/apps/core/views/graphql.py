import graphene
import graphene_django
from django.http import HttpResponseForbidden
from graphene_django.views import GraphQLView
from graphql import GraphQLError

from edivorce.apps.core.models import Document


class PrivateGraphQLView(GraphQLView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)


class DocumentType(graphene_django.DjangoObjectType):
    file_url = graphene.String(source='get_file_url')
    content_type = graphene.String(source='get_content_type')

    class Meta:
        model = Document
        exclude = ('id', 'file')


class Query(graphene.ObjectType):
    documents = graphene.List(DocumentType, doc_type=graphene.String(required=True), party_code=graphene.Int(required=True))

    def resolve_documents(self, info, **kwargs):
        if info.context.user.is_anonymous:
            raise GraphQLError('Unauthorized')
        q = Document.objects.filter(bceid_user=info.context.user, **kwargs)
        for doc in q:
            if not doc.file_exists():
                q.delete()
                return Document.objects.none()
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
        input_ = kwargs['input']
        documents = Document.objects.filter(bceid_user=info.context.user, doc_type=input_['doc_type'], party_code=input_['party_code'])

        unique_files = [dict(s) for s in set(frozenset(d.items()) for d in input_['files'])]
        if documents.count() != len(input_['files']) or documents.count() != len(unique_files):
            raise GraphQLError("Invalid input: there must be the same number of files")

        for i, file in enumerate(input_['files']):
            try:
                doc = documents.get(filename=file['filename'], size=file['size'])
                doc.sort_order = i + 1
                doc.width = file.get('width', doc.width)
                doc.height = file.get('height', doc.height)
                doc.rotation = file.get('rotation', doc.rotation)
                if doc.rotation not in [0, 90, 180, 270]:
                    raise GraphQLError(f"Invalid rotation {doc.rotation}, must be 0, 90, 180, 270")
                doc.save()
            except Document.DoesNotExist:
                raise GraphQLError(f"Couldn't find document '{file['filename']}' with size '{file['size']}'")
        return UpdateMetadata(documents=documents.all())


class Mutations(graphene.ObjectType):
    update_metadata = UpdateMetadata.Field()


graphql_schema = graphene.Schema(query=Query, mutation=Mutations)
