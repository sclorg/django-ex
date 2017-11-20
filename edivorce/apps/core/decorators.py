from django.conf import settings
from django.shortcuts import redirect

base_url = settings.PROXY_BASE_URL + settings.FORCE_SCRIPT_NAME[:-1]


def bceid_required(function=None):
    """
    View decorator to check if the user is logged in to BCEID

    This decorator has a dependency on bceid_middleware.py
    """

    def _dec(view_func):
        def _view(request, *args, **kwargs):
            if not request.user.is_authenticated():
                return redirect(base_url + '/login')
            return view_func(request, *args, **kwargs)

        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    return _dec if function is None else _dec(function)


def intercept(function=None):
    """
    Decorator to redirect to intercept page
    """
    terms = {'question__key': 'want_which_orders'}

    def _dec(view_func):
        def _view(request, *args, **kwargs):
            if (request.user.is_authenticated() and
                    not request.user.has_seen_orders_page and
                    not request.user.responses.filter(**terms).exists()):
                request.user.has_seen_orders_page = True
                request.user.save()
                return redirect(base_url + '/intercept')
            return view_func(request, *args, **kwargs)

        _view.__name__ = view_func.__name__
        _view.__dict__ = view_func.__dict__
        _view.__doc__ = view_func.__doc__

        return _view

    return _dec if function is None else _dec(function)
