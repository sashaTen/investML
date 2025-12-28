#   python manage.py runserver

from django.shortcuts import render
import joblib
from django.http import HttpResponse
from .ml_model import preprocess_text
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm 
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import PortfolioCreateForm ,   TickerForm   
from django.contrib.auth.decorators import login_required
from .models import Portfolio ,  Tickers
import yfinance as yf
import numpy as np


cv = joblib.load("count_vectorizer.pkl")
pca = joblib.load("pca.pkl")
model = joblib.load("logreg_model.pkl")



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
    if request.user.is_anonymous:
         context = {"tickers": []}
    else:
        tickers = Tickers.objects.filter(user=request.user)
        context = {"tickers": tickers}
        try :
            portfolio = Portfolio.objects.get(user=request.user)
            portfolio.tickers.add(*tickers)
        except Portfolio.DoesNotExist:
            return redirect("create_portfolio")
    return render(request, "users.html", context)



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



@login_required
def choose_tickers(request):
    if request.method == "POST":    
        form = TickerForm(request.POST)
        if form.is_valid():
            ticker_obj = form.save(commit=False)    # wait  for user auth
            ticker_obj.user = request.user          # ticker.user field =  user auth passed to  form 
            ticker_obj = form.save()  # saves to DB   
            return redirect(reverse("dashboard"))
    else:
        form = TickerForm()  # 👈 VERY IMPORTANT

    return render(request, "choose_tickers.html", {"form": form})   



def delete_ticker(request, ticker_id):
    if request.method == "POST":
        try:
            ticker = Tickers.objects.get(id=ticker_id, user=request.user)
            ticker.delete()
        except Tickers.DoesNotExist:
            pass
    return redirect("dashboard")




def delete_portfolio(request, portfolio_id):
    if request.method == "POST":
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
            portfolio.delete()
        except Portfolio.DoesNotExist:
            pass
    return redirect("portfolio_list")


def   get_prediction(request, ticker_id):
    # Preprocess the ticker symbol
    ticker = Tickers.objects.get(id=ticker_id, user=request.user)
    clean_text = preprocess_text("bad bad market")
    X = cv.transform([clean_text]).toarray()
    X = pca.transform(X)

    prediction = model.predict(X)[0]
    ticker.prediction = prediction
    ticker.save()
    return redirect("dashboard")




def allocation(request):
    user = request.user
    try:
        portfolio = Portfolio.objects.get(user=user)
        allocations = allocate_portfolio(portfolio)
        # Here you would typically save the allocations to the database or pass them to the template
    except Portfolio.DoesNotExist:
        allocations = {}
    return render(request, 'allocation.html', {'allocations': allocations})









def allocate_portfolio(portfolio):
    """
    Returns a dict: {ticker_symbol: allocation_amount}
    """

    budget = portfolio.budget
    risk_score = portfolio.risk / 100  # normalize to 0–1
    tickers = portfolio.tickers.all()

    scores = {}
    
    for symbol in tickers:
        try:
            data = yf.download(symbol, period="1y", progress=False)

            if data.empty:
                continue  # ticker not found

            prices = data["Adj Close"]
            returns = prices.pct_change().dropna()

            expected_return = returns.mean() * 252
            volatility = returns.std() * np.sqrt(252)

            if volatility == 0:
                continue

            # Risk-adjusted score (Sharpe-style, no risk-free rate)
            score = expected_return / volatility

            # Blend with user risk tolerance
            score = risk_score * score + (1 - risk_score) * 0.5

            scores[symbol] = max(score, 0)

        except Exception:
            continue  # any error → skip ticker

    if not scores:
        return {}

    # Normalize weights
    total_score = sum(scores.values())
    allocations = {
        symbol: round((score / total_score) * budget, 2)
        for symbol, score in scores.items()
    }

    return allocations
