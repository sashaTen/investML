#   python manage.py runserver

from django.shortcuts import render
import joblib
from django.http import HttpResponse
from .ml_model import preprocess_text
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse


cv = joblib.load("count_vectorizer.pkl")
pca = joblib.load("pca.pkl")
model = joblib.load("logreg_model.pkl")
#  python   manage.py runserver

def index(request):
    
    return render(request, 'homepage.html')



def sign_up(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(reverse("dashboard"))
    else:
        form = UserCreationForm()
    return render(request, "sign_up.html", {"form": form})
    

def dashboard(request):
    return render(request, "users.html")



def    predict(request):

    clean_text = preprocess_text("bad bad market")
    X = cv.transform([clean_text]).toarray()
    X = pca.transform(X)

    prediction = model.predict(X)[0]

    return HttpResponse(f"Prediction: {prediction}")




