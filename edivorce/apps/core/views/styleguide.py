from django.shortcuts import render


def guide(request):
    return render(request, 'styleguide/guide.html')
