
from pathlib import Path
from google.cloud import storage
import re 
import joblib
import yfinance as yf
import pandas as pd
BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "ml_artifacts"
print(ARTIFACTS_DIR)



def    get_version():
    bucket_name = "ml_buckets_a"
    file_name = "version.txt"

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    content = blob.download_as_text()

    return content.strip()


"""  f"vectorizer_v{int(content)+1}.pkl",
        f"pca_v{int(content)+1}.pkl",
        f"model_v{int(content)+1}.pkl", """






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

    # next trading day
    

    return  dates[1]-dates[0]

#



#print(get_prices_difference("AAPL", "2023-01-01"))


