import re 
from tavily import TavilyClient
import joblib
from dotenv import load_dotenv
import os
import yfinance as yf
from pathlib  import Path
from google.cloud import storage
from .models import Sentiment
loaded = load_dotenv()

if not loaded:
    load_dotenv("venv/.env")

API_KEY = os.getenv("THE_KEY")  
tavily_client = TavilyClient(api_key=API_KEY)

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / "ml_artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)

def find_latest_model_version(folder_path, pattern):

    folder = Path(folder_path)

    matched_files = [
        f for f in folder.iterdir()
        if f.is_file() and re.search(pattern, f.name)
    ]

    if not matched_files:
        return None

    # latest by modification time
    latest = max(matched_files, key=lambda f: f.stat().st_mtime)
    

    p = Path(latest)

    new_path = Path("ml_artifacts") / p.name
    s = new_path.as_posix() 

    num = int(re.search(r'v(\d+)', s).group(1))

    print(num)

    return num



def    get_version():
    bucket_name = "ml_buckets_a"
    file_name = "version.txt"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    content = blob.download_as_text()

    return content.strip()


current_version = find_latest_model_version(
    ARTIFACTS_DIR,
    r"model"
)

cloud_version = int(get_version())

if cloud_version > current_version:
    print("New model version available. Downloading...")

    download_blob(
        "ml_buckets_a",
        f"model_v{cloud_version}.pkl",
        ARTIFACTS_DIR / f"model_v{cloud_version}.pkl"
    )

    download_blob(
        "ml_buckets_a",
        f"vectorizer_v{cloud_version}.pkl",
        ARTIFACTS_DIR / f"vectorizer_v{cloud_version}.pkl"
    )

    download_blob(
        "ml_buckets_a",
        f"pca_v{cloud_version}.pkl",
        ARTIFACTS_DIR / f"pca_v{cloud_version}.pkl"
    )

    cv = joblib.load(ARTIFACTS_DIR / f"vectorizer_v{cloud_version}.pkl")
    pca = joblib.load(ARTIFACTS_DIR / f"pca_v{cloud_version}.pkl")
    model = joblib.load(ARTIFACTS_DIR / f"model_v{cloud_version}.pkl")

else:
    print("No new model version available.")

    cv = joblib.load(f"ml_artifacts/vectorizer_v{current_version}.pkl")
    pca = joblib.load(f"ml_artifacts/pca_v{current_version}.pkl")
    model = joblib.load(f"ml_artifacts/model_v{current_version}.pkl")






def  get_ticker_news(ticker):
    response = tavily_client.search("latest news about  " + ticker)
    Sentiment.objects.create(
            ticker=ticker,
            sentiment_text=response["results"][0]["content"]  # Assuming you have the sentiment text available
        )
    \
    if Sentiment.objects.count() % 1000 == 0:
        print("hi")
    return response["results"][0]["content"]

def make_prediction(text):
   
    X = cv.transform([text]).toarray()
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
       



