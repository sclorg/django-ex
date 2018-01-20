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
        password = request.POST.get('password', '')

        # just in case anyone from the general public discovers the dev server
        # make sure they don't accidentally login and think this is production
        if password.lower() != 'divorce':
            return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/bceid')

        # convert the login name to a guid
        hex_name = decode(binascii.hexlify(str.encode(login_name)))[0]
        fake_guid = hex_name.rjust(32, '0')

        # save the guid in a session variable
        request.session['login_name'] = login_name
        request.session['fake_bceid_guid'] = fake_guid

        return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/login')

    else:
        return render(request, 'localdev/bceid.html')
