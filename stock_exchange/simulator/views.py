from django.contrib.auth import views as auth_views
from django.shortcuts import render, HttpResponse



def index(request):
    msg = f"Hello"
    if request.user:
        msg += f", {request.user.username}"
    return HttpResponse(msg)

