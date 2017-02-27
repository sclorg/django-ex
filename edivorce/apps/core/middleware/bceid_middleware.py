import uuid

from django.conf import settings


class BceidUser(object):
    def __init__(self, guid, first_name, last_name, type, is_authenticated):
        self.guid = guid
        self.first_name = first_name
        self.last_name = last_name
        self.type = type
        self.is_authenticated = is_authenticated


class BceidMiddleware(object):
    def process_request(self, request):

        # make the FORCE_SCRIPT_NAME available in templates
        request.proxy_root_path = settings.FORCE_SCRIPT_NAME

        if settings.DEPLOYMENT_TYPE != 'localdev' and not request.META.get('HTTP_SM_USERDN', False):

            # 1. Real BCeID user / logged in

            # todo: Make sure the request is coming from the justice proxy (via IP/host check)

            request.bceid_user = BceidUser(
                guid=request.META.get('HTTP_SM_USERDN', ''),
                is_authenticated=True,
                type='BCEID',
                first_name='Bud',
                last_name='Bundy'
            )
        elif request.session.get('fake-bceid-guid', False):

            # 2. Fake BCeID user / logged in
            request.bceid_user = BceidUser(
                guid=request.session.get('fake-bceid-guid', ''),
                is_authenticated=True,
                type='FAKE',
                first_name='Kelly',
                last_name='Bundy'
            )
        else:

            # 3.  Anonymous User / not logged in
            if request.session.get('anon-guid', False):
                request.session['anon-guid'] = uuid.uuid4().urn[9:]

            request.bceid_user = BceidUser(
                guid=request.session.get('anon-guid'),
                is_authenticated=False,
                type='ANONYMOUS',
                first_name='',
                last_name=''
            )

    def process_response(self, request, response):
        return response
