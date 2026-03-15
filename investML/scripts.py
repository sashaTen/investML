import re 
from tavily import TavilyClient
import joblib
from dotenv import load_dotenv
import os
import yfinance as yf
from pathlib  import Path
from google.cloud import storage
from .models import Sentiment
import pandas  as pd
import random
import requests

loaded = load_dotenv()

if not loaded:
    load_dotenv("venv/.env")

API_KEY = os.getenv("THE_KEY")  
tavily_client = TavilyClient(api_key=API_KEY)

BASE_DIR = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = BASE_DIR / "ml_artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)



github_key = os.getenv("KEY_GITHUB") 
#

def trigger_github_workflow(github_key):
    url = "https://api.github.com/repos/sashaTen/investML/actions/workflows/retrain.yaml/dispatches"

    import json

    # The name of your workflow file
    token = github_key


    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = json.dumps({
        "ref": "main", # The branch the workflow should run on
    
    })

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 204:
        print("GitHub Actions workflow triggered successfully!")
    else:
        print(f"Failed to trigger workflow. Status code: {response.status_code}, Response: {response.text}")








def   download_blob(bucket_name, blob_name, destination_file):
# create client
    client = storage.Client()

    # get bucket
    bucket = client.bucket(bucket_name)

    # get file (blob)
    blob = bucket.blob(blob_name)

    # download
    blob.download_to_filename(destination_file)




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



def get_version(file_name):
    bucket_name = "ml_buckets_a"
    

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    content = blob.download_as_text()


    return content



def  get_artifact_version(content, type):
    for line in content.splitlines():
        key, value = line.split("=")
        if key.strip() == type:
            return int(value.strip())
        



current_version = find_latest_model_version(
    ARTIFACTS_DIR,
    r"model"
)
content = get_version(file_name="version.txt")
cloud_version  = get_artifact_version(content, "ml_artifacts")

#########

def update_version(content, version ,type="ml_artifacts"):
    lines = content.splitlines()
    new_lines = []

    for line in lines:
        key, value = line.split("=")

        if key.strip() == type:
            new_lines.append(f"{type} = {version+1}")
        else:
            new_lines.append(line)

    return "\n".join(new_lines)



def upload_version(blob_name , new_content):
    bucket_name = "ml_buckets_a"
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    # download file
    blob.upload_from_string(new_content)

    print("Version updated.")






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



def get_prices_difference(ticker_symbol, start_date):
    ticker = yf.Ticker(ticker_symbol)

    start = pd.Timestamp(start_date)
    end = start + pd.Timedelta(days=10)

    data = ticker.history(start=start, end=end)

    if data.empty:
        return None, None

    # first trading day on or after start_date
    dates  =  []
    for  i  in range(1, len(data)):
         if data.iloc[i]["Close"] != None and data.iloc[i]["Close"] != 0:
                dates.append(data.iloc[i]["Close"])
                if  len(dates) == 2:
                    break
    
    if dates[1]-dates[0] >= 0:
        return 1
    else:
        return 0
    

def   turn_db_into_pd(model):
    qs = model.objects.all().values()

    df = pd.DataFrame(list(qs))
    df["date"] = pd.to_datetime("2023-01-01")
    df["date"] = pd.to_datetime(df["date"])
    cutoff = pd.Timestamp.today() - pd.Timedelta(days=5)  
    df = df[df["date"] <= cutoff]

    return  df 


def save_pd_to_csv(df, directory, filename):
    directory = Path(directory)
    
    # create directory if it does not exist
    directory.mkdir(parents=True, exist_ok=True)

    path = directory / filename

    df.to_csv(path, index=False)

    return path

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name, if_generation_match=generation_match_precondition)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )


# 

def compute_label(row):
        diff = get_prices_difference(row["ticker"], row["date"])
        return diff



def add_label_column(model):

    df = turn_db_into_pd(model) 
    
    
    df["label"] = df.apply(compute_label, axis=1)
    return df


def  get_ticker_news(ticker):
    response = tavily_client.search("latest news about  " + ticker)
    Sentiment.objects.create(
            ticker=ticker,
            sentiment_text=response["results"][0]["content"]  # Assuming you have the sentiment text available
        )
    \
    if Sentiment.objects.count() > 0 :
        current_data_version = find_latest_model_version(
    ARTIFACTS_DIR,
    r"data"
)
        new_content = update_version(content, current_data_version, "data")
        print("hi")
        df = add_label_column(Sentiment)
        csv_path = save_pd_to_csv(df, ARTIFACTS_DIR, f"data_v{current_data_version + 1}.csv")
        upload_version("version.txt", new_content)
        upload_blob("ml_buckets_a", csv_path, f"data_v{current_data_version + 1}.csv")
        trigger_github_workflow(github_key)
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
       



