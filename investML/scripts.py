from tavily import TavilyClient
import joblib
from .ml_model import preprocess_text
from dotenv import load_dotenv
import os
import yfinance as yf
load_dotenv(".venv/.env")

API_KEY = os.getenv("THE_KEY")  



tavily_client = TavilyClient(api_key=API_KEY )

cv = joblib.load("count_vectorizer.pkl")
pca = joblib.load("pca.pkl")
model = joblib.load("logreg_model.pkl")



def  news_sentiment(ticker):
    response = tavily_client.search("latest news about  " + ticker)
    clean_text = preprocess_text(response["results"][0]["content"])
    X = cv.transform([clean_text]).toarray()
    X = pca.transform(X)
    prediction = model.predict(X)[0]
    return prediction





def  get_profit_margin(symbol):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return info.get("profitMargins")
 

def margin_allocation_proportion(tickers, budget):
    sum = 0 
    for  i  in  tickers:
        sum  +=   get_profit_margin(i.ticker)
    return  round(budget/(sum*100),2)