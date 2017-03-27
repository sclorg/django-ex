from django.shortcuts import render


def guide(request):
    """
    Visual design styles
    """
    return render(request, 'styleguide/guide.html')
