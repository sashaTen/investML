from tavily import TavilyClient
import joblib
from .ml_model import preprocess_text
from dotenv import load_dotenv
import os
import yfinance as yf
load_dotenv(".venv/.env")

API_KEY = os.getenv("THE_KEY")  



tavily_client = TavilyClient(api_key=API_KEY )


"random_count_vectorizer.pkl" , "random_pca.pkl" , "random_forest_model.pkl"
cv = joblib.load("random_count_vectorizer.pkl")
pca = joblib.load("random_pca.pkl")
model = joblib.load("random_forest_model.pkl")

def  get_ticker_news(ticker):
    response = tavily_client.search("latest news about  " + ticker)
    return response["results"][0]["content"]

def make_prediction(text):
    clean_text = preprocess_text(text)
    X = cv.transform([clean_text]).toarray()
    X = pca.transform(X)
    prediction = model.predict(X)[0]
    return prediction

def  news_sentiment(ticker):
    news_content = get_ticker_news(ticker)
    prediction = make_prediction(news_content)
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





class PortfolioAllocation:
    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.tickers = portfolio.tickers.all()
        self.risk = portfolio.risk
        self.budget = portfolio.budget * (self.risk / 100)

        # cache margins once
        self.margins = self._compute_margins()

    def get_profit_margin(self, symbol):
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get("profitMargins", 0)

    def _compute_margins(self):
        margins = {}
        for t in self.tickers:
            margins[t.ticker] = self.get_profit_margin(t.ticker)
        return margins

    def margin_allocation_proportion(self):
        total_margin = sum(self.margins.values())
        if total_margin == 0:
            return 0
        return round(self.budget / (total_margin * 100), 2)

    def allocate(self):
        proportion = self.margin_allocation_proportion()
        allocations = []

        for t in self.tickers:
            margin = self.margins[t.ticker]
            allocation = round(proportion * 100 * margin, 3)

            allocations.append({
                "ticker": t.ticker,
                "margin": margin,
                "allocation": allocation
            })

        return allocations



