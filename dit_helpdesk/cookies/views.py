from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required

def show(request):
    return render(request, 'cookies/index.html')