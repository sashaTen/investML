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


lemma = WordNetLemmatizer()
stopwordSet = set(stopwords.words("english"))


def preprocess_text(text ):
        text = re.sub("[^a-zA-Z]", " ", text)
        text = text.lower()
        tokens = word_tokenize(text, language="english")
        tokens = [lemma.lemmatize(w) for w in tokens if w not in stopwordSet]
        return " ".join(tokens)



def  train_and_save_model():

    data = pd.read_csv('C:\\Users\\HP\\Desktop\\investML\\stock_data.csv')
    y = data["Sentiment"]


    


    textList = [preprocess_text(t) for t in data["Text"]]


    X_train_text, X_test_text, y_train, y_test = train_test_split(
        textList,
        y,
        test_size=0.2,
        random_state=21,
        stratify=y
    )



    cv = CountVectorizer(max_features=5001)

    X_train = cv.fit_transform(X_train_text).toarray()
    X_test = cv.transform(X_test_text).toarray()



    pca = PCA(n_components=256)

    X_train = pca.fit_transform(X_train)
    X_test = pca.transform(X_test)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)

    print("Accuracy:", acc)
    joblib.dump(cv, "count_vectorizer.pkl")
    joblib.dump(pca, "pca.pkl")
    joblib.dump(model, "logreg_model.pkl")

    print("Model, vectorizer, and PCA saved successfully.")
