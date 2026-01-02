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
from dotenv import load_dotenv
import os
from tavily import TavilyClient
import numpy as np
import random

load_dotenv(".venv/.env")

API_KEY = os.getenv("THE_KEY")  



tavily_client = TavilyClient(api_key=API_KEY )



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



   
    response = tavily_client.search("Who is Leo Messi?")
    clean_text = preprocess_text(response["results"][0]["content"])
    X = cv.transform([clean_text]).toarray()
    X = pca.transform(X)
    prediction = model.predict(X)[0]



    return HttpResponse( clean_text + "      the prediction is: " + str(prediction))



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
    portfolio = Portfolio.objects.get(user=user)
    allocations = []
    budget = portfolio.budget
    budget_10_percent = budget*0.1
    ml_budget =  budget-budget_10_percent
    tickers   =   portfolio.tickers.all()
    proportion =  margin_allocation_proportion(tickers, budget)
    ml_proportion =  margin_allocation_proportion(tickers, ml_budget)
    prediction_list=[]
    for  i in tickers:
        if   ticker_sentiment(i.ticker)  == 1:
            prediction_list.append( i.ticker)

    if prediction_list:
       prediction_bonus = budget_10_percent / len(prediction_list)
    else:
       prediction_bonus = 0
       ml_budget = budget
   
    for  i  in  tickers:
        allocations.append({   "ticker" :    i.ticker    , "profit_margin":  get_profit_margin(i.ticker), "allocation": round(proportion*100*get_profit_margin(i.ticker),3 ) })
   
    ml_allocations = []

    for i in tickers:
        profit_margin = get_profit_margin(i.ticker)

        base_allocation = ml_proportion * 100 * profit_margin

        # Add bonus only if ticker is predicted to rise
        if i.ticker in prediction_list:
            final_allocation = base_allocation + prediction_bonus
        else:
            final_allocation = base_allocation

        ml_allocations.append({
            "ticker": i.ticker,
            "profit_margin": profit_margin,
            "allocation": round(final_allocation, 3)
        })

    return render(request, 'allocation.html', {'allocations': allocations, 'ml_allocations': ml_allocations}) 




def  get_profit_margin(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return info.get("profitMargins")
 

def margin_allocation_proportion(tickers, budget):
    sum = 0 
    for  i  in  tickers:
        sum  +=   get_profit_margin(i.ticker)
    return  round(budget/(sum*100),2)


def  ticker_sentiment(ticker):
    response = tavily_client.search("latest news about  " + ticker)
    clean_text = preprocess_text(response["results"][0]["content"])
    X = cv.transform([clean_text]).toarray()
    X = pca.transform(X)
    prediction = model.predict(X)[0]
    value = random.randint(0, 1)
    return prediction




