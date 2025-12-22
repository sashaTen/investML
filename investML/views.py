#   python manage.py runserver

from django.shortcuts import render
import joblib
from django.http import HttpResponse
from .ml_model import preprocess_text
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import PortfolioCreateForm
from django.contrib.auth.decorators import login_required
from .models import Portfolio

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



@login_required
def create_portfolio(request):
    if request.method == "POST":
        form = PortfolioCreateForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            return redirect("portfolio_list")
    else:
        form = PortfolioCreateForm()

    return render(request, "portfolio.html", {"form": form})


@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(
        request,
        "portfolio_list.html",
        {"portfolios": portfolios}
    )

