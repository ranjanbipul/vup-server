from django.shortcuts import render

# Create your views here.
from django.conf import settings
from django.shortcuts import redirect,render


def index(request):
    if request.user.is_authenticated:
        return redirect('%s' % (settings.APP_URL,))
    else:
        return render(request,'home/login.html')
