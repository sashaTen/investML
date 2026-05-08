#   python manage.py runserver
import requests
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
from .models import Portfolio, Tickers ,Sentiment
from .agentic import research_stock  , extract_stock_data


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




from django.shortcuts import render

def research_ticker(request, ticker):

    final_brief = research_stock(ticker, stream=True) 
    #final_brief = [{'type': 'text', 'text': '## Investment Brief: MSFT - Microsoft Corporation\n**Date:** 2024-05-15\n**Recommendation:** BUY\n**Conviction:** HIGH\n### The Bull Case\nMicrosoft demonstrates strong fundamentals with a 0.183 YoY revenue growth and a healthy profit margin of 0.3934. The company\'s forward P/E of 21.45 is considered attractive by analysts, who also highlight a significant implied upside of 35.36% from the current price, with a mean price target of $562.07. Continued innovation in AI and cloud services positions Microsoft for future growth.\n### The Bear Case\nDespite strong fundamentals, the technical picture shows some bearish signals, including a Death Cross (SMA50 below SMA200) and MACD below its signal line. Recent news sentiment is neutral, with mixed signals, indicating some uncertainty in the near term. The current volume is also below average, suggesting a lack of strong buying interest.\n### Fundamental Snapshot\n* **P/E Ratio (TTM):** 24.73, **Forward P/E:** 21.45\n* **Revenue Growth (YoY):** 0.183, **Earnings Growth (YoY):** 0.234\n* **Profit Margin:** 0.3934, **Operating Margin:** 0.46326\n* **Debt-to-Equity Ratio:** 30.271 (relatively low)\n### Technical Picture\n* **RSI (14-day):** 53.97 (Neutral)\n* **MACD:** 5.9002, **Signal Line:** 6.9785 (Bearish - MACD below signal line)\n* **Moving Averages:** SMA50 ($398.15) is below SMA200 ($464.37), indicating a Death Cross (bearish).\n* **Volume:** Today\'s volume (7,390,184) is significantly below the 30-day average (33,404,206), suggesting below-average trading activity.\n### News Sentiment\nOverall news sentiment is NEUTRAL, driven by mixed signals (23 bullish, 19 bearish). Some headlines suggest the current valuation offers a rare entry point and that Microsoft is perfectly poised for 2026 after underperforming in 2025. Other articles provide various price forecasts for 2026 and beyond.\n### Analyst Consensus\nOut of 54 analysts, 44 recommend "Buy" and 10 recommend "Strong Buy", with only 3 "Hold" ratings. The consensus recommendation is "STRONG BUY". The mean price target is $562.07, implying an upside of 35.36% from the current price of $415.24.\n### Final Verdict\nDespite some bearish technical signals and neutral near-term news sentiment, Microsoft\'s strong fundamentals, including robust revenue and earnings growth, healthy profit margins, and a manageable debt-to-equity ratio, make it an attractive long-term investment. The overwhelming "STRONG BUY" consensus from Wall Street analysts, coupled with a significant implied upside to the mean price target, reinforces a positive outlook. The current forward P/E also suggests a reasonable valuation. Therefore, a **BUY** recommendation with **HIGH** conviction is warranted for MSFT.', 'extras': {'signature': 'CpsBAQw51sdq9t0PBmLJ8EPcXye20IVISVRqae4ZVN779QTIM1vlGGGBH34HeuMBFcoxaKLlQ7G1XrGbQSxfPdlpN05/p2gYqYxO80vH7QUHAD65qO00AUSSaW+nwMD6lvUhpbJyhNreXKemNsaPImd/R4pThBkDI6AYQiZHF+udtoYOzSmONpqYwB5zFbQXEFhvKC/BQwTYPv/Tbvs='}}]

    text = final_brief[0]['text']
    extracted_data = extract_stock_data(text)

    return render(
        request,
        "ticker_analysis.html",
        {
            "ticker": ticker.upper(),
            "data": extracted_data
        }
    )



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




