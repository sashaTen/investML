from django.urls import path
from .views import index,  predict ,  dashboard

urlpatterns = [
    path("", index, name="index"),
    path("dashboard/", dashboard, name="dashboard"),
    path("predict/", predict, name="predict"),
]
