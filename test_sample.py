#     pytest  -m   unit
from investML.scripts import print_any
import pytest
import pandas as pd





"""@pytest.mark.slow
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
def  test_news_sentiment():
    ticker = 'TSLA'
    sentiment = news_sentiment(ticker)
    if sentiment is None:
        raise AssertionError("news_sentiment returned None")
    assert sentiment in [0, 1]  # Assuming binary classification



@pytest.mark.slow
def   test_make_prediction():
    sample_text = "The company's performance has been outstanding this quarter."
    prediction = make_prediction(sample_text)
    if prediction is None:
        raise AssertionError("make_prediction returned None")
    assert prediction in [0, 1]  # Assuming binary classification
    
"""








############# DATA PIPE  TESTS  #####################


@pytest.mark.unit
def test_print_any():

    test_word = "Hello, InvestML!"
    print_any(test_word)  # Just ensure it runs without error
    assert True  # If no exception, the test passes



