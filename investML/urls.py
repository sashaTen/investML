from django.urls import path
from .views import index,  predict ,  dashboard , sign_up

urlpatterns = [
    path("", index, name="index"),
    path("dashboard/", dashboard, name="dashboard"),
     path("sign_up/", sign_up, name="sign_up"),
    path("predict/", predict, name="predict"),
]
