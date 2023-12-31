from django.shortcuts import render
from django.conf import settings

# Create your views here.


def home_view(request):
    context = {}
    context['is_debug'] = settings.DEBUG
    context['room_id'] = 1
    return render(request, 'personal/home.html', context)
