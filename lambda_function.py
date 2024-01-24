import os

import nltk
import numpy as np
import pandas as pd
from codecarbon import EmissionsTracker
from loguru import logger
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import (hamming_loss, accuracy_score, precision_score,
                             recall_score, f1_score, jaccard_score,
                             label_ranking_average_precision_score,
                             classification_report)
from sklearn.model_selection import train_test_split
from sklearn.multioutput import MultiOutputClassifier
from sklearn.svm import LinearSVC

from utils.preprocessing import preprocess, diets_category_fixed

current_path = os.path.dirname(os.path.realpath(__file__))
nltk.data.path.append(current_path + "/nltk_data")


def handler(event, context):
    tracker = EmissionsTracker()
    tracker.start()

    if not os.path.exists("/tmp/codecarbon"):
        os.makedirs("/tmp/codecarbon")

    df = pd.read_json(current_path + "/bbc_recipes.json")
    all_tags = [item for sublist in df["diets"].tolist() for item in sublist]
    all_tags = [diets_category_fixed(tag) for tag in all_tags]

    unique_tags = list(set(all_tags))

    df["diets"] = df["diets"].apply(lambda x: [diets_category_fixed(tag) for tag in x])
    for tag in unique_tags:
        df[tag] = df["diets"].apply(lambda x: 1 if tag in x else 0)

    df['ingredients'] = df['ingredients'].apply(preprocess)

    df = df.drop(['title', 'directions', 'nutrition', 'diets', 'link', 'serve'], axis=1)

    x = df["ingredients"]
    y = np.asarray(df.drop(['ingredients'], axis=1))

    vectorizer = TfidfVectorizer(max_features=2500, max_df=0.9)
    vectorizer.fit(x)

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=101)

    x_train_tfidf = vectorizer.transform(x_train)
    x_test_tfidf = vectorizer.transform(x_test)

    calibrated_svc = CalibratedClassifierCV(base_estimator=LinearSVC())
    clf = MultiOutputClassifier(calibrated_svc).fit(x_train_tfidf, y_train)
    prediction = clf.predict(x_test_tfidf)

    logger.info("Accuracy score: {}".format(accuracy_score(y_test, prediction)))
    logger.info("Hamming loss: {}".format(hamming_loss(y_test, prediction)))
    logger.info("Precision score: {}".format(precision_score(y_test, prediction, average='micro')))
    logger.info("Recall score: {}".format(recall_score(y_test, prediction, average='micro')))
    logger.info("F1 score: {}".format(f1_score(y_test, prediction, average='micro')))
    logger.info("Jaccard score: {}".format(jaccard_score(y_test, prediction, average='micro')))
    logger.info(
        "Label ranking average precision score: {}".format(label_ranking_average_precision_score(y_test, prediction)))

    report = classification_report(y_test, prediction, target_names=unique_tags)
    logger.info(report)

    emission = tracker.stop()
    logger.info(emission)
