print('hello retrain world')
#c:/Users/HP/Desktop/investML/ml_code/retrain.py

from google.cloud import storage

def find_blob(bucket_name ):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(bucket_name)

    print(f"Blobs in bucket '{bucket_name}':")
    for blob in blobs:
       
            print(blob.name)
            # Return the specific blob if found

# Example usage:
#find_blob("ml_buckets_a")



def download_blob(bucket_name, source_blob_name, destination_file_name):
    """Downloads a blob from the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # source_blob_name = "storage-object-name"

    # The path to which the file should be downloaded
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )


#download_blob("ml_buckets_a", "knn_model.pkl", r"C:\Users\HP\Desktop\investML\ml_artifacts\knn_model.pkl") 
#download_blob("ml_buckets_a", "knn_count_vectorizer.pkl", r"C:\Users\HP\Desktop\investML\ml_artifacts\knn_count_vectorizer.pkl") 
#download_blob("ml_buckets_a", "knn_pca.pkl", r"C:\Users\HP\Desktop\investML\ml_artifacts\knn_pca.pkl") 

