
from pathlib import Path
from google.cloud import storage
import re 
import joblib
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






