print('hello retrain world')
#c:/Users/HP/Desktop/investML/ml_code/retrain.py
from google.cloud import storage
import re
import  pandas as pd
from nltk.corpus import stopwords
from nltk import word_tokenize, WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib
from sklearn.neighbors import KNeighborsClassifier

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "ml_artifacts"
ARTIFACTS_DIR.mkdir(exist_ok=True)


lemma = WordNetLemmatizer()
stopwordSet = set(stopwords.words("english"))
path = ARTIFACTS_DIR / "stock_data.csv"

target_column = "Sentiment"


def load_df(path):
    data = pd.read_csv(path)
    return data


def preprocess_text(text):
    text = re.sub("[^a-zA-Z]", " ", text)
    text = text.lower()
    tokens = word_tokenize(text, language="english")
    tokens = [lemma.lemmatize(w) for w in tokens if w not in stopwordSet]
    return " ".join(tokens)



def split(df, target_column):
    data = df
    y = data[target_column]
    textList = [preprocess_text(t) for t in data["Text"]]
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        textList, y, test_size=0.2, random_state=21, stratify=y
    )
    return X_train_text, X_test_text, y_train, y_test


def preprocess(X_train_text):
    cv = CountVectorizer(max_features=5001)
    X_train = cv.fit_transform(X_train_text).toarray()
    pca = PCA(n_components=256)
    X_train = pca.fit_transform(X_train)
    return cv, pca, X_train


def modelling(X_train, y_train, model):
    model.fit(X_train, y_train)
    return model


def evaluate_model(X_test_text, y_test, cv, pca, model):

    X_test = cv.transform(X_test_text).toarray()
    X_test = pca.transform(X_test)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print("Accuracy:", acc)
    return acc


def save_model(cv, pca, model, cv_name, pca_name, model_name):
    joblib.dump(cv, ARTIFACTS_DIR /cv_name)
    joblib.dump(pca, ARTIFACTS_DIR /pca_name)
    joblib.dump(model, ARTIFACTS_DIR /model_name)
    print("Model, vectorizer, and PCA saved successfully.")


def pipeline(path, target_column, cv_name, pca_name, model_name, model):
    #with mlflow.start_run():
        df = load_df(path)
        X_train_text, X_test_text, y_train, y_test = split(df, target_column)
        cv, pca, X_train = preprocess(X_train_text)
        model = modelling(X_train, y_train, model)
        accuracy = evaluate_model(X_test_text, y_test, cv, pca, model)
       # mlflow.log_metric("accuracy", accuracy)
       # mlflow.sklearn.log_model(model, "model")
        save_model(cv, pca, model, cv_name, pca_name, model_name)





#knn_model = KNeighborsClassifier(n_neighbors=5)
#pipeline(path, target_column, "knn_count_vectorizer.pkl", "knn_pca.pkl", "knn_model.pkl", knn_model)









'''
'''
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




def clean_folder_except(folder_path: str, file_to_keep: str):
    """
    Deletes all files in folder_path except file_to_keep.
    
    :param folder_path: Path to the folder
    :param file_to_keep: Filename (not full path) to preserve
    """
    folder = Path(folder_path)

    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"{folder_path} is not a valid directory")

    for item in folder.iterdir():
        # Skip the file we want to keep
        if item.name == file_to_keep:
            continue

        # Delete files
        if item.is_file():
            item.unlink()

        # Optional: delete subdirectories too
        elif item.is_dir():
            for sub in item.rglob("*"):
                if sub.is_file():
                    sub.unlink()
            sub.rmdir()  # remove empty dir
            item.rmdir()

    print(f"Folder cleaned. Kept: {file_to_keep}")


def  get_version_number(filename):
    num = filename.split("_v")[1].split(".")[0]
    return int(num) 



def overwrite_version():
    with open("version.txt", "r") as f:
        content = f.read()
    
    # modify content
    content = content.replace(f"{content}", f"{int(content) + 1}")

    with open("version.txt", "w") as f:
        f.write(content)
    



if __name__ == "__main__":
    overwrite_version()
    with open("version.txt", "r") as f:
        content = f.read()
            
    

    knn_model = KNeighborsClassifier(n_neighbors=5)

    pipeline(
        path,
        target_column,
        f"vectorizer_v{int(content)}.pkl",
        f"pca_v{int(content)}.pkl",
        f"model_v{int(content)}.pkl",
        knn_model
    )

    bucket_name = "ml_buckets_a"
    artifact_dir = Path("ml_artifacts")

    artifacts = [
        (f"vectorizer_v{int(content)}.pkl", f"vectorizer_v{int(content)}.pkl"),
        (f"pca_v{int(content)}.pkl", f"pca_v{int(content)}.pkl"),
        (f"model_v{int(content)}.pkl", f"model_v{int(content)}.pkl"),
    ]

    for source_name, destination_name in artifacts:

        source_path = artifact_dir / source_name

        upload_blob(
            bucket_name,
            str(source_path),
            destination_name
        )
    


    clean_folder_except(
    folder_path=str(ARTIFACTS_DIR),
    file_to_keep="stock_data.csv"
)
 