
from pathlib import Path
from google.cloud import storage

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

def   download_blob(bucket_name, blob_name, destination_file):
# create client
    client = storage.Client()

    # get bucket
    bucket = client.bucket(bucket_name)

    # get file (blob)
    blob = bucket.blob(blob_name)

    # download
    blob.download_to_filename(destination_file)






""" 

#download_blob("ml_buckets_a",  ARTIFACTS_DIR )
if __name__ == "__main__":
    bucket_name = "ml_buckets_a"
    artifact_dir = Path("ml_artifacts")

    artifacts = [
        f"vectorizer_v{int(get_version())}.pkl",  
        
    ]

    for artifact in artifacts:
        download_blob(bucket_name, artifact, artifact_dir / artifact)



from google.cloud import storage

 """





#   gcloud storage cp version.txt gs://ml_buckets_a/version.txt

content = get_version()
print("Current version:", content)





