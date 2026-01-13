from investML.scripts import (
    get_ticker_news,
    make_prediction, 
    news_sentiment,
    margin_allocation_proportion,
    get_profit_margin,
    
)
import pytest
from tavily import TavilyClient
from dotenv import load_dotenv
import os
import yfinance as yf

load_dotenv(".venv/.env")

API_KEY = os.getenv("THE_KEY")  



tavily_client = TavilyClient(api_key=API_KEY )



@pytest.mark.unit
def test_get_ticker_news():
    ticker = 'NVDA'
    result = get_ticker_news(ticker)
    if result is None:
        raise AssertionError("get_ticker_news returned None")
    assert isinstance(result, str)


@pytest.mark.slow
def test_profit_margin():
    symbol = 'AAPL'
    margin = get_profit_margin(symbol)
    if margin is None:
        raise AssertionError("get_profit_margin returned None")
    assert isinstance(margin, float) or margin is None


@pytest.mark.slow
def   test_make_prediction():
    sample_text = "The company's performance has been outstanding this quarter."
    prediction = make_prediction(sample_text)
    if prediction is None:
        raise AssertionError("make_prediction returned None")
    assert prediction in [0, 1]  # Assuming binary classification



@pytest.mark.slow
def  test_news_sentiment():
    ticker = 'TSLA'
    sentiment = news_sentiment(ticker)
    if sentiment is None:
        raise AssertionError("news_sentiment returned None")
    assert sentiment in [0, 1]  # Assuming binary classification