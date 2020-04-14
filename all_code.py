# -*- coding: utf-8 -*-
"""a2-4900.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dGjhDWnApf0T5orDfLqcy1j24w5nQuKe

# Assignment 2 -- COMP 4900
### Student: Tri Cao (100971065) & Hien Le (101044264)

---

# 1. Summary

This notebook contains implementations and data analysis details for the second homework, as a detailed reference for our finding. For more compact result please refer to the report.pdf

---

# 2. Data Analysis

## 1. Import data

- Make sure to upload the `train.csv` and `test.csv` data
- Import python libraries
"""

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.pipeline import Pipeline

"""- Using `Pandas` to read the _csv_ files"""

train_df = pd.read_csv("./train.csv")
test_df = pd.read_csv("./test.csv")

train_df.head(5)

test_df.head(5)

"""## 2. Prepare data-cleaning models for the pipeline

  - There are multiple techniques to analyze and prepare the data to achieve the best results for our models
  - Here we are creating a Sklearn's Pipeline to preprocess the data
"""

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.pipeline import Pipeline
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer

nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

"""### 1. Remove non-word characters

- This model will remove non-word character from the whole dataset
- This includes removing punctuations and numeric characters
"""

class ExtractNonwordCharacters(BaseEstimator):
    """ remove numbers and non-word characters, such as, < > _
    """
    def __init__(self, number=True, non_words=True):
        self.number = number
        self.non_words = non_words

    def fit(self, x, y=None):
        return self

    def transform(self, x):
        # remove numbers
        if self.number:
            x = x.str.replace("\d+", "")

        # remove non-word characters
        if self.non_words:
            x = x.str.replace("<br />", "", regex=False)
            x = x.str.replace("[^\w\s]", "")
            x = x.replace(r"_", "", regex=True)
        return x

print("Before: \n", train_df.review[:1][0])
print("\nAfter:\n", ExtractNonwordCharacters().transform(train_df.review[:1])[0])

"""### 2. Remove stopwords

- Stopwords don't help us to find the context or the true meaning of a sentence.
- Thus, they need to to be removed from our datasets
"""

class ExtractStopwords(BaseEstimator):
    """ 
    Remove stopwords from dataset and words that have less than 2 letters
    for example, 'the car' --> 'car'
    """
    def __init__(self):
        self.stop_words = set(stopwords.words("english"))

    def fit(self, x, y=None):
        return self

    def remove_stopwords(self, doc):
        words_list = [w for w in doc.split() if (w not in self.stop_words) and len(w) > 2]
        return " ".join(words_list)

    def transform(self, x):
        x = map(self.remove_stopwords, x)
        x = np.array(list(x))
        return x

print("Before: \n", train_df.review[:1][0])
print("\nAfter:\n", ExtractStopwords().transform(train_df.review[:1])[0])



"""### 3. Lemmatize reviews

- Since some words mean the same but have different part of speech and in different tense. For example, `am`, `is`, `are`
- we need to lemmatize them to reduce the size of the dataset
"""

class Lemmatizer(BaseEstimator):
    """ Lemmatize dataset
    for example, convert 'is', 'am', 'are' --> 'be'
    """
    def __init__(self):
        self.wnl = WordNetLemmatizer()

    def get_wordnet_pos(self, word):
        tag = nltk.pos_tag([word])[0][1][0].upper()
        tag_dict = {
            "J": wordnet.ADJ,
            "N": wordnet.NOUN,
            "V": wordnet.VERB,
            "R": wordnet.ADV,
        }
        return tag_dict.get(tag, wordnet.NOUN)

    def fit(self, x, y=None):
        return self

    def lemma(self, doc):
        words_list = [
            self.wnl.lemmatize(w, self.get_wordnet_pos(w)) for w in doc.split()
        ]
        return " ".join(words_list)

    def transform(self, x):
        x = map(self.lemma, x)
        x = np.array(list(x))
        return x

print("Before: \n", train_df.review[:1][0])
print("\nAfter:\n", Lemmatizer().transform(train_df.review[:1])[0])

"""### 4. Stem reviews

- Similar to lemmatization, Stemming is the process to reduce inflected (or sometimes derived) words to their word stem
"""

class Stemmer(BaseEstimator):
    """ 
    stem words by removing some characters at the end of the wood
    for example, 'beautiful'  -->  'beauti'
    """
    def __init__(self):
        self.stemmer = PorterStemmer()

    def fit(self, x, y=None):
        return self

    def stem(self, doc):
        words_list = [
            self.stemmer.stem(w) for w in doc.split()
        ]
        return " ".join(words_list)

    def transform(self, x):
        x = map(self.stem, x)
        x = np.array(list(x))
        return x

print("Before: \n", train_df.review[:1][0])
print("\nAfter:\n", Stemmer().transform(train_df.review[:1])[0])

"""### 5. Finally, Run the Pipeline
- We have created both stemmed data and lemmztized data, however the result show no difference, thus here we only create a Pipeline for the `Lemmatizer()`

- Convert the label (sentiment) to `1` and `0`
"""

train_df.sentiment = train_df.sentiment.astype("category").cat.codes
train_df.sentiment

"""- Initialize the Pipeline with desired models"""

review_pipeline = Pipeline([("Extract-Nonwords", ExtractNonwordCharacters()),
                            ("Extract-Stopwords", ExtractStopwords()),
                            ("Lemmatizer", Lemmatizer())])

"""- Fit and transform both train and test sets"""

train_df.review = review_pipeline.fit_transform(train_df.review)
test_df.review = review_pipeline.transform(test_df.review)

# cleaned train data
train_df.head(5)

# clean test data
test_df.head(5)

"""# 3. Vectorization

### 1. Split the train data
"""

from sklearn.model_selection import train_test_split, cross_val_score

X_train_df, X_test_df, y_train_df, y_test_df = train_test_split(train_df.review, train_df.sentiment, test_size=0.2, random_state=111)

print("X_train: ", X_train_df.shape)
print("X_test : ", X_test_df.shape)
print("y_train: ", y_train_df.shape)
print("y_test: ", y_test_df.shape)

"""### 2. Vectorize the train and test data

- Here we taking the top 20,000 words inluding unigram and bigram
- Set binaty to `True` and ignores words that occur less than 4 times
"""

from sklearn.feature_extraction.text import CountVectorizer

count_vec = CountVectorizer(max_features=20000, ngram_range=(1, 2), binary=True, min_df=4, max_df=0.7)

X_train = count_vec.fit_transform(X_train_df)
X_test = count_vec.transform(X_test_df)
actual_test = count_vec.transform(test_df.review)

print("X_train: ", X_train.shape)
print("X_test: ", X_test.shape)
print("Actual Test: ", actual_test.shape)

"""- Convert test sets to numpy array"""

y_train = y_train_df.to_numpy()
y_test = y_test_df.to_numpy()

print("y_train: ", y_train.shape)
print("y_test: ", y_test.shape)

"""### 3. Data vocabulary"""

import matplotlib.pyplot as plt

count_vec.vocabulary_

"""#  4. Naive Bayes Classifier Implementation"""

class MyNaiveBayes(BaseEstimator, ClassifierMixin):

    def fit(self, X, y):
        theta_y = sum(y) / len(y)
        sum_X = np.array([np.array(np.sum(X[y == k], axis=0)).flatten() for k in range(2)]).T
        sum_y = np.array([len(y) - sum(y), sum(y)])
        self.theta_X = (sum_X + 1) / (sum_y + 2)
        self.log_1 = np.log(theta_y / (1 - theta_y))
        self.log_2 = np.log(self.theta_X[:, 1] / self.theta_X[:, 0])
        self.log_3 = np.log((1 - self.theta_X[:, 1]) / (1 - self.theta_X[:, 0]))
        return self

    def predict(self, X):
        X_arr = X.toarray()
        self.logits = np.full(X.shape[0], self.log_1) + X @ self.log_2 + (1 - X_arr) @ self.log_3
        return (self.logits > 0).astype(int)


    def predict_proba(self, X):
        pred = np.random.rand(X.shape[0], self.classes_.size)
        return pred / np.sum(pred, axis=1)[:, np.newaxis]

"""# 5. Experiments

- The function is implemented in order to make it eaiser for testing different  classification models
"""

from sklearn.metrics import classification_report
import time

def test_model(clf, train_data, test_data):
    X_train, y_train = train_data
    X_test, y_test = test_data
    scores = cross_val_score(clf, X_train, y_train, cv=5)
    print(f"Training score: {scores}")

    start_time = time.time()
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    runtime = time.time() - start_time

    target_names = ["positive", "negative"]
    reports = classification_report(y_test, y_pred, target_names=target_names)
    print(reports)
    return y_pred, runtime

def calculate_accuracy(labels, pred):
  correct = (labels == pred)
  return correct.sum() / correct.size

# store the results
test_results = []

"""### 1. Test with our Naive Bayes Model"""

train_data = [X_train, y_train]
test_data = [X_test, y_test]

nb = MyNaiveBayes()

nb_y_pred, nb_runtime = test_model(nb, train_data, test_data)

nb_accu = calculate_accuracy(y_test, nb_y_pred)
test_results.append({'accuracy': nb_accu, 'runtime': nb_runtime})

"""### 2. Test with Sklearn's LinearSVC model"""

from sklearn.svm import LinearSVC

svc = LinearSVC(max_iter=3000, C=0.05)

svc_y_pred, svc_runtime = test_model(svc, train_data, test_data)

svc_accu = calculate_accuracy(y_test, svc_y_pred)
test_results.append({'accuracy': svc_accu, 'runtime': svc_runtime})

"""### 2. Test with Sklearn's Logistic Regression Model"""

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV

lr = LogisticRegression(max_iter=3000, C=0.05)

lr_y_pred, lr_runtime = test_model(lr, train_data, test_data)

lr_accu = calculate_accuracy(y_test, lr_y_pred)
test_results.append({'accuracy': lr_accu, 'runtime': lr_runtime})

"""# 5. Results and conclusions:

### 1. Accuracy of Classification models
"""

import matplotlib.pyplot as plt

x_axis_labels = ['Naive Bayes', 'LinearSVC', 'Logistic Regresion']
y_axis = [t['accuracy'] for t in test_results]
plt.bar([1,2,3], y_axis, color="blue")
plt.xlabel("Training models")
plt.ylabel("Accuracy")
plt.title("Accuracy comparison")
plt.xticks([1, 2, 3], x_axis_labels)
plt.savefig('accu.png')
plt.show()

"""### 2. Runtime of Classification models"""

y_runtime = [t['runtime'] for t in test_results]
plt.bar([1,2,3], y_runtime, color="blue")
plt.xlabel("Training models")
plt.ylabel("Runtime")
plt.title("Runtime comparison")
plt.xticks([1, 2, 3], x_axis_labels)
plt.savefig('runtime.png')
plt.show()

"""### 3. Export Kaggle test result

### 1. Compute predictions using Logistic Regression
"""

kaggle_pred = lr.predict(actual_test)

"""### 2. Format and Export the results"""

result_df = pd.DataFrame()
result_df["id"] = list(range(len(kaggle_pred)))
result_df["sentiment"] = kaggle_pred
result_df["sentiment"] = result_df["sentiment"].astype("category")
result_df["sentiment"].cat.categories = ["negative", "positive"]
result_df.to_csv("kaggle_submission.csv", index=False)
result_df

"""## Extra: GloVe: Global Vectors for Word Representation

For this extra section, we describe our attempts to use pretrained Glove word embedding to vectorize the sentences.

[Download the trained word embedding here](http://nlp.stanford.edu/data/glove.twitter.27B.zip)

Extract and upload the 200 dimensions word embedding to colab environment.

Using this model, we have each word to map with a 200 dimensional vector, which can be used to create the feature matrix
"""

from keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import normalize

# load embedding
def load(filename):
	with open(filename,'r') as f:
	  lines = f.readlines()

	embedding = dict()
	for line in lines:
		features = line.split()
		embedding[features[0]] = np.asarray(features[1:], dtype='float32')
	return embedding

embedding = load('glove.twitter.27B.200d.txt')

# Tokenize all words in the train and test data
all_reviews=train_df['review'].append(test_df['review'])
tokenizer = Tokenizer()
tokenizer.fit_on_texts(all_reviews)

vocab = list(tokenizer.word_index.keys())
vocab_filtered = [word for word in vocab if len(word) > 2]

# Vectorize all sentences using the pretrained models
num_features = 200
def vectorize(sentences, num_features):
  mat = np.zeros((len(sentences), num_features))
  for i, sentence in enumerate(sentences):
    vectors = np.array([embedding[word] for word in sentence.split(" ") if word in embedding])
    if len(vectors) != 0:
      mat[i] = np.sum(vectors, axis=0)
  return mat

# Each sentence is the normalized sum of the pretrained global vectors of all words
X_train = normalize(vectorize(train_df['review'], num_features))
X_test = normalize(vectorize(test_df['review'], num_features))

# Test with logistic regression
lr = LogisticRegression(max_iter=3000, C=0.05)
x_train_df, x_test_df, y_train_df, y_test_df = train_test_split(X_train, train_df.sentiment, test_size=0.2, random_state=111)

train_data = x_train_df, y_train_df
test_data = x_test_df, y_test_df

lr_y_pred_glove, lr_runtime_glove = test_model(lr, train_data, test_data)

lr_accu_glove = calculate_accuracy(y_test, lr_y_pred_glove)
test_results.append({'accuracy': lr_accu, 'runtime': lr_runtime_glove})

"""### Conclusion:

The attempt to use pre-trained GloVe word embedding seems to not have the good result . One possible reason is that the model we used is too general, and we belive we could achieve a better result if we can instead train the glove word embedding using our own review vocabulary.
"""