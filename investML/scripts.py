from tavily import TavilyClient
import joblib
from .ml_model import preprocess_text
from dotenv import load_dotenv
import os
import yfinance as yf


load_dotenv(".venv/.env")
API_KEY = os.getenv("THE_KEY")  
tavily_client = TavilyClient(api_key=API_KEY)

cv = joblib.load("ml_artifacts/knn_count_vectorizer.pkl")
pca = joblib.load("ml_artifacts/knn_pca.pkl")
model = joblib.load("ml_artifacts/knn_model.pkl")

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

  

    def _compute_margins(self):
        margins = {}
        for t in self.tickers:
            margins[t.ticker] = get_profit_margin(t.ticker)
        return margins

  

    def allocate(self):
        proportion = margin_allocation_proportion(self.tickers, self.budget)
        allocations = []

        for t in self.tickers:
            margin = self.margins[t.ticker]
            allocation = round(proportion * 100 * margin, 3)

            allocations.append({
                "prediction" : t.prediction,
                "ticker": t.ticker,
                "margin": margin,
                "allocation": allocation
            })

        return allocations



class MlPortfolioAllocation(PortfolioAllocation):
    def __init__(self, portfolio):
        super().__init__(portfolio)
        self._update_predictions()
        self.count = self.tickers.filter(prediction=1).count()
        self.bonus = self.budget * 0.1 /self.count if self.count > 0 else 0
        self.base =   self.budget
        self.budget = self.budget * 0.9
    def _update_predictions(self):
        for t in self.tickers:
            if t.prediction > 1:
                t.prediction = news_sentiment(t.ticker)
                t.save()
    def allocate(self):
        base_allocations = super().allocate()
        if self.count > 0  :
            
            for allocation in base_allocations:
                   if allocation["prediction"] == 1 :
                    allocation["allocation"] +=  self.bonus  
        else:
            self.budget = self.base
            base_allocations = super().allocate()
        return base_allocations
       



