#     pytest  -m   unit


from   investML.ml_model  import  preprocess_text , split
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
def test_preprocess_text():
    raw_text = "This is a Sample TEXT! With numbers 123 and symbols #@$."
    processed = preprocess_text(raw_text)

    assert processed is not None
    assert isinstance(processed, str)

    assert "sample" in processed
    assert "text" in processed
    assert "number" in processed
    assert "symbol" in processed

    assert processed.islower()



@pytest.mark.unit
def test_split_function():
    # ---- Arrange ----
    df = pd.DataFrame({
        "Text": [
            "Stock prices are rising",
            "Market crashes badly",
            "Investors are optimistic",
            "Economic slowdown fears",
            "Tech stocks rally",
            "Inflation worries continue",
        ],
        "label": [1, 0, 1, 0, 1, 0],
    })

    # ---- Act ----
    X_train, X_test, y_train, y_test = split(df, "label")

    # ---- Assert ----
    # sizes
    assert len(X_train) > 0
    assert len(X_test) > 0

    assert len(X_train) + len(X_test) == len(df)
    assert len(y_train) + len(y_test) == len(df)

    # types
    assert all(isinstance(x, str) for x in X_train)
    assert all(isinstance(x, str) for x in X_test)

    # stratification preserved
    assert set(y_train.unique()) == set(df["label"].unique())
    assert set(y_test.unique()) == set(df["label"].unique())

