#   python manage.py runserver

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import PortfolioCreateForm, TickerForm
from django.contrib.auth.decorators import login_required
from .scripts import (
    news_sentiment,
    PortfolioAllocation,
    MlPortfolioAllocation,
)
from .models import Portfolio, Tickers



def index(request):
    return render(request, "homepage.html")


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
        try:
            portfolio = Portfolio.objects.get(user=request.user)
            portfolio.tickers.add(*tickers)
        except Portfolio.DoesNotExist:
            return redirect("create_portfolio")
    return render(request, "users.html", context)


@login_required
def create_portfolio(request):
    portfolio_exists = Portfolio.objects.filter(user=request.user).exists()

    if request.method == "POST" and not portfolio_exists:
        form = PortfolioCreateForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            return redirect("portfolio_list")
    else:
        form = PortfolioCreateForm()

    context = {
        "form": form,
        "portfolio_exists": portfolio_exists,
    }
    return render(request, "portfolio.html", context)


@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, "portfolio_list.html", {"portfolios": portfolios})


@login_required
def choose_tickers(request):

    if request.method == "POST":
        form = TickerForm(request.POST)
        if form.is_valid():
            ticker_obj = form.save(commit=False)  # wait  for user auth
            ticker_obj.user = (
                request.user
            )  # ticker.user field =  user auth passed to  form
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


def get_prediction(request, ticker_id):
    # Preprocess the ticker symbol
    ticker = Tickers.objects.get(id=ticker_id, user=request.user)
    if ticker.prediction > 1:
        prediction = news_sentiment(ticker.ticker)
        ticker.prediction = prediction
        ticker.save()
        return redirect("dashboard")
    else:
        return redirect("dashboard")


def allocation(request):
    user = request.user
    portfolio = Portfolio.objects.get(user=user)
    if request.method == "POST":
        ml_portfolio = MlPortfolioAllocation(portfolio)  #
        request.session["ml_allocations"] = ml_portfolio.allocate()
    base_portfolio = PortfolioAllocation(portfolio)
    try:
        t_allocations = base_portfolio.allocate()
    except Exception as e:
        return render(request, "allocation_message.html")
    t_ml_allocations = request.session.pop("ml_allocations", [])
    return render(
        request,
        "allocation.html",
        {"allocations": t_allocations, "ml_allocations": t_ml_allocations},
    )
