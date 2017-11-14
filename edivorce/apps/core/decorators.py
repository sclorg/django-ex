from django.conf import settings
from django.shortcuts import redirect


def bceid_required(function=None):
    """
    View decorator to check if the user is logged in to BCEID

    This decorator has a dependency on bceid_middleware.py
    """

    def _dec(view_func):
        def _view(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return redirect(settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1] + '/login')
            return view_func(request, *args, **kwargs)

        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    return _dec if function is None else _dec(function)
