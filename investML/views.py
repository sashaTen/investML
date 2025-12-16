from django.shortcuts import render

from django.http import HttpResponse

def index(request):
    return HttpResponse("investML stock   management  app ")




#   python manage.py runserver
