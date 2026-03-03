
import re
from pathlib import Path
from google.cloud import storage
import joblib

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "ml_artifacts"
print(ARTIFACTS_DIR)
'''
cv = joblib.load("ml_code/ml_artifacts/knn_count_vectorizer_v1.pkl")
pca = joblib.load("ml_code/ml_artifacts/knn_pca_v1.pkl")
model = joblib.load("ml_code/ml_artifacts/knn_model_v1.pkl")
'''











def download_blob(bucket_name,  destination_folder):
   

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

  
    blobs = list(bucket.list_blobs())
    blobs.sort(key=lambda x: x.time_created, reverse=True)
    for blob in blobs[:3]:
        
         destination_file = destination_folder / blob.name

         blob.download_to_filename(str(destination_file))
        

   


#download_blob("ml_buckets_a",  ARTIFACTS_DIR )
if __name__ == "__main__":
    download_blob("ml_buckets_a",  ARTIFACTS_DIR )



