from django.http import HttpResponse
from django.shortcuts import render
from edivorce.apps.core.models import Profile


def serve(request, path):
    if path[0:2] == 'f/':
        path = path[2:0]
    if (len(path) > 4 and path[-5:] != '.html') or len(path) == 0:
        path += '/index.html'
    if path[:1] == '/':
        path = path[1:]
    return render(request, path)


def preview(request, form):
    """
    View showing template preview of rendered form
    """

    return render(request, 'preview/%s.html' % form)


def login(request):
    return render(request, 'login.html')


def logout(request):
    return render(request, 'logout.html')


def form(request, form, step):
    """
    View rendering form/step combo
    """
    return render(request, '%s/%s.html' % (form, step))


def dashboard(request):
    return render(request, 'dashboard.html')


def overview(request):
    return render(request, 'overview.html')


def prequalification(request):
    return render(request, 'prequalification.html')


def index(request):
    return render(request, 'index.html')


def health(request):
    return HttpResponse(Profile.objects.count())
