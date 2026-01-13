import numpy as np
import pandas as pd
import re
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk import word_tokenize, WordNetLemmatizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.linear_model import LogisticRegression
import joblib
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier


lemma = WordNetLemmatizer()
stopwordSet = set(stopwords.words("english"))
path = "C:\\Users\\HP\\Desktop\\investML\\stock_data.csv"
target_column = "Sentiment"


def preprocess_text(text):
    text = re.sub("[^a-zA-Z]", " ", text)
    text = text.lower()
    tokens = word_tokenize(text, language="english")
    tokens = [lemma.lemmatize(w) for w in tokens if w not in stopwordSet]
    return " ".join(tokens)

def load_df(path):
    data = pd.read_csv(path)
    return data

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
    joblib.dump(cv, cv_name)
    joblib.dump(pca, pca_name)
    joblib.dump(model, model_name)
    print("Model, vectorizer, and PCA saved successfully.")


def pipeline(path, target_column, cv_name, pca_name, model_name, model):
    df = load_df(path)
    X_train_text, X_test_text, y_train, y_test = split(df, target_column)
    cv, pca, X_train = preprocess(X_train_text)
    model = modelling(X_train, y_train, model)
    evaluate_model(X_test_text, y_test, cv, pca, model)
    save_model(cv, pca, model, cv_name, pca_name, model_name)


model = LogisticRegression()
pipeline(path , target_column ,"logistic_count_vectorizer.pkl" , "logistic_pca.pkl" , "logistic_model.pkl" , model )
