"""
Generate the dataset with:

SELECT d.relevant, j.url, j.url_tokens, j.anchor_text_tokens, j.surrounding_text_tokens
FROM jobs j JOIN documents d
WHERE j.id = d.job_id
AND j.done = 1;
"""
import json
import os

import pandas as pd
from dotenv import load_dotenv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

from crawler import utils
from crawler.utils import get_logger

LOG = get_logger(__name__)
load_dotenv()

N_ESTIMATOR = int(os.getenv("CRAWLER_URL_ML_N_ESTIMATOR"))
MAX_DEPTH = int(os.getenv("CRAWLER_URL_ML_MAX_DEPTH"))
CRAWLER_URL_ML_CLASSIFIER_MIN_QUALITY = float(os.getenv("CRAWLER_URL_ML_CLASSIFIER_MIN_QUALITY"))

def prepare_urls_for_models(url_tokens_batch: list[list[str]], anchor_text_tokens_batch: list[list[str]]) -> list[str]:
    """
    Function to prepare URLs
    """
    batch_return = []
    for url_tokens, anchor_text_tokens in zip(url_tokens_batch, anchor_text_tokens_batch):
        url_tokens = [
            token.replace("/", " ").replace("https:", "").replace("http:", "").replace("www", "").replace("tuebingen",
                                                                                                          "tubingen").lower().replace(
                "%c3%bc", "u").replace("_", " ").replace("-", " ").replace("&", " ").replace(",", " ") for token in url_tokens]
        batch_return.append(" ".join(url_tokens) + " " + " ".join(anchor_text_tokens))
    return batch_return


def train_model():
    """
    Train and save the model.
    """

    def prepare_input_to_train(column_url_tokenized, column_anchor_text_tokenized) -> list[str]:
        """
        Prepare input to train.
        """
        url_tokenized = column_url_tokenized.apply(lambda x: json.loads(x))
        anchor_text_tokenized = column_anchor_text_tokenized.apply(lambda x: json.loads(x))
        return prepare_urls_for_models(url_tokenized, anchor_text_tokenized)

    x_data = []
    y_data = []
    for file in os.listdir("data/url_relevance_classification_data"):
        df = pd.read_csv(f"data/url_relevance_classification_data/{file}")
        x_data.extend(prepare_input_to_train(df['url_tokens'], df['anchor_text_tokens']))
        y_data.extend(list(df['relevant']))

    x_train, x_test, y_train, y_test = train_test_split(x_data, y_data, test_size=0.2, random_state=42)

    # Create a CountVectorizer to convert text into numerical features
    vectorizer = CountVectorizer()

    # Fit and transform the training data
    x_train_vectorized = vectorizer.fit_transform(x_train)
    x_test_vectorized = vectorizer.transform(x_test)

    # Train an Extreme Gradient Boosting (XGBoost) classifier
    xgb_classifier = XGBClassifier(n_estimators=N_ESTIMATOR, max_depth=MAX_DEPTH)
    xgb_classifier.fit(x_train_vectorized, y_train)

    # Predict the relevance of the documents
    y_pred = xgb_classifier.predict(x_test_vectorized)

    # Calculate evaluation metrics
    report_dict = classification_report(y_test, y_pred, output_dict=True)
    report = classification_report(y_test, y_pred)
    LOG.info("Training Report:")
    LOG.info(report)
    all_greater_than_09 = all(value > CRAWLER_URL_ML_CLASSIFIER_MIN_QUALITY for value in report_dict['weighted avg'].values())

    if not all_greater_than_09:
        raise Exception(f"Some metrics in the report are not greater than {CRAWLER_URL_ML_CLASSIFIER_MIN_QUALITY}.")

    # Train on every thing
    vectorizer = CountVectorizer()
    x_total = vectorizer.fit_transform(x_data)
    xgb_classifier = XGBClassifier(n_estimators=N_ESTIMATOR, max_depth=MAX_DEPTH)
    xgb_classifier.fit(x_total, y_data)
    report = classification_report(y_data, xgb_classifier.predict(x_total))
    LOG.info("Final model Report:")
    LOG.info(report)

    utils.io.write_pickle_file((xgb_classifier, vectorizer), os.getenv("CRAWLER_URL_ML_CLASSIFIER_FILE"))


if __name__ == '__main__':
    train_model()
