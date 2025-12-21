#   python manage.py runserver

from django.shortcuts import render
import joblib
from django.http import HttpResponse
from .ml_model import preprocess_text

cv = joblib.load("count_vectorizer.pkl")
pca = joblib.load("pca.pkl")
model = joblib.load("logreg_model.pkl")
#  python   manage.py runserver

def index(request):
    
    return render(request, 'homepage.html')

def dashboard(request):
    return render(request, "users.html")



def    predict(request):

    clean_text = preprocess_text("bad bad market")
    X = cv.transform([clean_text]).toarray()
    X = pca.transform(X)

    prediction = model.predict(X)[0]

    return HttpResponse(f"Prediction: {prediction}")




