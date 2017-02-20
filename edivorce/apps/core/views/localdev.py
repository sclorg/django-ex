import uuid
import binascii
from encodings.utf_8 import decode
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def bceid(request):
    """ fake bceid login for developer workstation environment """
    if request.method == "POST":
        login_name = request.POST.get('user', '')

        # convert the login name to a guid
        hex_name = decode(binascii.hexlify(str.encode(login_name)))[0]
        fake_guid = uuid.UUID(hex_name.rjust(32, '0')).urn[9:]

        # save the guid in a session variable
        request.session['fake-bceid-guid'] = fake_guid

        return redirect(settings.FORCE_SCRIPT_NAME[:-1] + '/login')

    else:
        return render(request, 'localdev/bceid.html')
