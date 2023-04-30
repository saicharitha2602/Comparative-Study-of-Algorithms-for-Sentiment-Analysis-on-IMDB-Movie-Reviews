# -*- coding: utf-8 -*-
"""Comparative Study for Sentiment Analysis.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lc-80f47AZiWLrKUudA630Ea4n97hwcq
"""

import pandas as pd
import numpy as np
np.set_printoptions(precision=2, linewidth=80)

from google.colab import files
uploaded = files.upload()

import io
imdb_data= pd.read_csv(io.BytesIO(uploaded['IMDB Dataset.csv']))

imdb_data.head()

imdb_data.describe()

imdb_data['sentiment'].value_counts()

import nltk
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelBinarizer
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from wordcloud import WordCloud,STOPWORDS
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize,sent_tokenize
from bs4 import BeautifulSoup
import spacy
import re,string,unicodedata
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.stem import LancasterStemmer,WordNetLemmatizer

#Tokenization of text
tokenizer=ToktokTokenizer()
#Setting English stopwords
nltk.download('stopwords')
stopword_list=nltk.corpus.stopwords.words('english')
imdb_data.head()

#Removing the html strips
def strip_html(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text()
#Removing the square brackets
def remove_between_square_brackets(text):
    return re.sub('\[[^]]*\]', '', text)
#Removing the noisy text
def denoise_text(text):
    text = strip_html(text)
    text = remove_between_square_brackets(text)
    return text
#Apply function on review column
imdb_data['review']=imdb_data['review'].apply(denoise_text)
imdb_data.head()

#Define function for removing special characters
def remove_special_characters(text, remove_digits=True):
    pattern=r'[^a-zA-z0-9\s]'
    text=re.sub(pattern,'',text)
    return text
#Apply function on review column
imdb_data['review']=imdb_data['review'].apply(remove_special_characters)
imdb_data.head()

#Stemming the text
def simple_stemmer(text):
     ps=nltk.porter.PorterStemmer()
     text= ' '.join([ps.stem(word) for word in text.split()])
    return text
#Apply function on review column
imdb_data['review']=imdb_data['review'].apply(simple_stemmer)
imdb_data.head()

#set stopwords to english
stop=set(stopwords.words('english'))
print(stop)

#removing the stopwords
def remove_stopwords(text, is_lower_case=False):
    tokens = tokenizer.tokenize(text)
    tokens = [token.strip() for token in tokens]
    if is_lower_case:
        filtered_tokens = [token for token in tokens if token not in stopword_list]
    else:
        filtered_tokens = [token for token in tokens if token.lower() not in stopword_list]
    filtered_text = ' '.join(filtered_tokens)    
    return filtered_text
#Apply function on review column
imdb_data['review']=imdb_data['review'].apply(remove_stopwords)

# Encoding Sentiment column
from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
imdb_data["sentiment"] = le.fit_transform(imdb_data["sentiment"])
imdb_data.head()

reviews = np.array(imdb_data['review'])
sentiments = np.array(imdb_data['sentiment'])

# build train and test datasets
train_reviews = reviews[:35000]
train_sentiments = sentiments[:35000]
test_reviews = reviews[35000:]
test_sentiments = sentiments[35000:]

norm_train_reviews=imdb_data.review[:35000]

#norm_train_reviews[0]

norm_test_reviews=imdb_data.review[35000:]
#norm_test_reviews[45005]

#word cloud for positive review words
plt.figure(figsize=(10,10))
positive_text=norm_train_reviews[1]
WC=WordCloud(width=1000,height=500,max_words=500,min_font_size=5)
positive_words=WC.generate(positive_text)
plt.imshow(positive_words,interpolation='bilinear')
plt.show

#Word cloud for negative review words
plt.figure(figsize=(10,10))
negative_text=norm_train_reviews[8]
WC=WordCloud(width=1000,height=500,max_words=500,min_font_size=5)
negative_words=WC.generate(negative_text)
plt.imshow(negative_words,interpolation='bilinear')
plt.show

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# build BOW features on train reviews
cv = CountVectorizer(binary=False, min_df=0.0, max_df=1.0, ngram_range=(1,2))
cv_train_reviews = cv.fit_transform(norm_train_reviews)

# build TFIDF features on train reviews
tfidf = TfidfVectorizer(use_idf=True, min_df=0.0, max_df=1.0, ngram_range=(1,2),sublinear_tf=True)
tfidf_train_reviews = tfidf.fit_transform(norm_train_reviews)

cv_test_reviews = cv.transform(norm_test_reviews)
tfidf_test_reviews = tfidf.transform(norm_test_reviews)

print('BOW model:> Train features shape:', cv_train_reviews.shape, ' Test features shape:', cv_test_reviews.shape)
print('TFIDF model:> Train features shape:', tfidf_train_reviews.shape, ' Test features shape:', tfidf_test_reviews.shape)

"""**1a. Applying Logistic Regression on BOW model**"""

from sklearn.linear_model import SGDClassifier, LogisticRegression

lr = LogisticRegression()

# Logistic Regression model on BOW features
lr.fit(cv_train_reviews,train_sentiments)
# predict using model
lr_bow_predictions = lr.predict(cv_test_reviews)

from sklearn import metrics
from sklearn.metrics import accuracy_score
lr_bow_score=metrics.accuracy_score(test_sentiments, lr_bow_predictions)
print("Accuracy score:",np.round(lr_bow_score,2)*100,"%")

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics
lr_bow_cm = metrics.confusion_matrix(test_sentiments, lr_bow_predictions)
plt.figure(figsize=(5,5))
print(lr_bow_cm)

sns.heatmap(lr_bow_cm/np.sum(lr_bow_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
#plt.xaxis.set_ticklabels(['Negative', 'Positive'])
#plt.xaxis.set_ticklabels(['Positive', 'Negative'])

print("Confusion matrix:")
all_sample_title = 'Accuracy Score: {0}%'.format(np.round(lr_bow_score,2)*100)
plt.title(all_sample_title, size = 12)

from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, lr_bow_predictions))

"""**Building a Prediction System**"""

#Custom Test: Test a review on the best performing model (Logistic Regression)
trainingVector = CountVectorizer(stop_words='english', ngram_range = (1,1), max_df = .80, min_df = 5)
X=imdb_data.review
trainingVector.fit(X)
X_dtm = trainingVector.transform(X)
y=imdb_data.sentiment
LR_complete = LogisticRegression()
LR_complete.fit(X_dtm, y)
#Input Review
print('\nTesting  a custom review')
test = ['good ,but not great']
test_dtm = trainingVector.transform(test)
predLabel = LR_complete.predict(test_dtm)
if(predLabel[0]==1):
  print("Positive Review")
else:
  print("Negative Review")

"""**1b. Logistic Regression using TFIDF features **"""

lr.fit(tfidf_train_reviews,train_sentiments)
# predict using model
lr_tfidf_predictions = lr.predict(tfidf_test_reviews)

lr_tfidf_score = metrics.accuracy_score(test_sentiments,lr_tfidf_predictions)
print("Accuracy score:",np.round(lr_tfidf_score,2)*100,"%")

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics
lr_tfidf_cm = metrics.confusion_matrix(test_sentiments, lr_tfidf_predictions)
print(lr_tfidf_cm)
plt.figure(figsize=(5,5))
sns.heatmap(lr_tfidf_cm/np.sum(lr_tfidf_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
print("Confusion matrix:")
all_sample_title = 'Accuracy Score: {0}%'.format(np.round(lr_tfidf_score,2)*100)
plt.title(all_sample_title, size = 12)

from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, lr_tfidf_predictions))

"""2a . SVM model using BOW features"""

#SVM model on BOW features
svm = SGDClassifier(loss='hinge', max_iter=1000)
svm.fit(cv_train_reviews,train_sentiments)
# predict using model
svm_bow_predictions = svm.predict(cv_test_reviews)

svm_bow_score = metrics.accuracy_score(test_sentiments,svm_bow_predictions)
print("Accuracy score:",np.round(svm_bow_score,2)*100,"%")

svm_bow_cm = metrics.confusion_matrix(test_sentiments, svm_bow_predictions)
plt.figure(figsize=(5,5))
sns.heatmap(svm_bow_cm/np.sum(svm_bow_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
print("Confusion matrix:")
print(svm_bow_cm)
all_sample_title = 'Accuracy Score: {0}%'.format(np.round(svm_bow_score,2)*100)
plt.title(all_sample_title, size = 12)

from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, svm_bow_predictions))

"""2b . SVM model using TF-IDF features"""

# SVM model on TF-IDF features
svm.fit(tfidf_train_reviews,train_sentiments)
# predict using model
svm_tfidf_predictions = svm.predict(tfidf_test_reviews)

svm_tfidf_score = metrics.accuracy_score(test_sentiments,svm_tfidf_predictions)
print("Accuracy score:",np.round(svm_tfidf_score,2)*100,"%")

svm_tfidf_cm = metrics.confusion_matrix(test_sentiments, svm_tfidf_predictions)
plt.figure(figsize=(5,5))
sns.heatmap(svm_tfidf_cm/np.sum(svm_tfidf_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
print("Confusion matrix:")
print(svm_tfidf_cm)
all_sample_title = 'Accuracy Score: {0}%'.format(np.round(svm_tfidf_score,2)*100)
plt.title(all_sample_title, size = 12)

from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, svm_tfidf_predictions))

"""3b .Naive Bayes using BOW"""

from sklearn.naive_bayes import MultinomialNB

#training the model
mnb=MultinomialNB()
#fitting the svm for bag of words
mnb.fit(cv_train_reviews,train_sentiments)
mnb_bow_predictions=mnb.predict(cv_test_reviews)
print(mnb_bow_predictions)

#Accuracy score for bag of words
mnb_bow_score = metrics.accuracy_score(test_sentiments,mnb_bow_predictions)
print("Accuracy score:",np.round(mnb_bow_score,2)*100,"%")

mnb_bow_cm = metrics.confusion_matrix(test_sentiments, mnb_bow_predictions)
plt.figure(figsize=(5,5))
sns.heatmap(mnb_bow_cm/np.sum(mnb_bow_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
print("Confusion matrix:")
print(mnb_bow_cm)
all_sample_title = 'Accuracy Score: {0}%'.format(np.round(mnb_bow_score,2)*100)
plt.title(all_sample_title, size = 12)

#Classification report for bag of words 
from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, mnb_bow_predictions))

"""3b . Naive Bayes using TF-IDF"""

#fitting the svm for tfidf features
mnb.fit(tfidf_train_reviews,train_sentiments)
#Predicting the model for tfidf features
mnb_tfidf_predictions=mnb.predict(tfidf_test_reviews)
print(mnb_tfidf_predictions)

#Accuracy score for tfidf features
mnb_tfidf_score=metrics.accuracy_score(test_sentiments,mnb_tfidf_predictions)
print("Accuracy score:",np.round(mnb_tfidf_score,2)*100,"%")

mnb_tfidf_cm = metrics.confusion_matrix(test_sentiments, mnb_tfidf_predictions)
plt.figure(figsize=(5,5))
sns.heatmap(mnb_tfidf_cm/np.sum(mnb_tfidf_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
print("Confusion matrix:")
print(mnb_tfidf_cm)
all_sample_title = 'Accuracy Score: {0}%'.format(np.round(mnb_tfidf_score,2)*100)
plt.title(all_sample_title, size = 12)

from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, mnb_tfidf_predictions))

"""**4a . Decision Tress using BOW**"""

from sklearn.tree import DecisionTreeClassifier
dct = DecisionTreeClassifier()

#Fitting the model
dct.fit(cv_train_reviews,train_sentiments)

#predicting the model
dct_bow_predictions = dct.predict(cv_test_reviews)

dct_bow_score = metrics.accuracy_score(test_sentiments,dct_bow_predictions)
print("Accuracy score:",np.round(dct_bow_score,2)*100,"%")

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics
dct_bow_cm = metrics.confusion_matrix(test_sentiments, dct_bow_predictions)
plt.figure(figsize=(5,5))
#sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True)
sns.heatmap(dct_bow_cm/np.sum(dct_bow_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
print("Confusion matrix:")
print(dct_bow_cm)
all_sample_title = 'Accuracy Score: {0}%'.format(np.round(dct_bow_score,2)*100)
plt.title(all_sample_title, size = 12)

from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, dct_bow_predictions))

"""**4b . Decision Trees using TF-IDF** """

#Fitting the model
dct.fit(tfidf_train_reviews,train_sentiments)

#predicting the model
dct_tfidf_predictions = dct.predict(tfidf_test_reviews)

dct_tfidf_score = metrics.accuracy_score(test_sentiments,dct_tfidf_predictions)
print("Accuracy score:",np.round(dct_tfidf_score,2)*100,"%")

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics
dct_tfidf_cm = metrics.confusion_matrix(test_sentiments, dct_tfidf_predictions)
plt.figure(figsize=(5,5))
#sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True)
sns.heatmap(dct_tfidf_cm/np.sum(dct_tfidf_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
print("Confusion matrix:")
print(dct_tfidf_cm)
all_sample_title = 'Accuracy Score: {0}%'.format(np.round(dct_tfidf_score,2)*100)
plt.title(all_sample_title, size = 12)

from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, dct_bow_predictions))

"""**5a . KNN model using bow** """

from sklearn.neighbors import KNeighborsClassifier
KNN = KNeighborsClassifier(n_neighbors = 3)

KNN.fit(cv_train_reviews,train_sentiments)

knn_bow_predictions = KNN.predict(cv_test_reviews)

print(knn_bow_predictions)

knn_bow_score = metrics.accuracy_score(test_sentiments,knn_bow_predictions)
print('Accuracy:  {:2.2%} '.format(metrics.accuracy_score(test_sentiments, knn_bow_predictions)))

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics
knn_bow_cm = metrics.confusion_matrix(test_sentiments, knn_bow_predictions)
plt.figure(figsize=(5,5))
#sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True)
sns.heatmap(knn_bow_cm/np.sum(knn_bow_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
print("Confusion matrix:")
print(knn_bow_cm)
plt.title(all_sample_title, size = 12)

from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, knn_bow_predictions))

"""**5b. KNN using TF-IDF**"""

KNN.fit(tfidf_train_reviews,train_sentiments)

knn_tfidf_predictions = KNN.predict(tfidf_test_reviews)

print(knn_tfidf_predictions)

from sklearn.metrics import accuracy_score
knn_tfidf_score = metrics.accuracy_score(test_sentiments,knn_tfidf_predictions)
print('Accuracy:  {:2.2%} '.format(metrics.accuracy_score(test_sentiments, knn_tfidf_predictions)))

import matplotlib.pyplot as plt
import seaborn as sns
from sklearn import metrics
knn_tfidf_cm = metrics.confusion_matrix(test_sentiments, knn_tfidf_predictions)
plt.figure(figsize=(5,5))
#sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True)
sns.heatmap(knn_tfidf_cm/np.sum(knn_tfidf_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
print("Confusion matrix:")
print(knn_tfidf_cm)
knn_tfidf_score=metrics.accuracy_score(test_sentiments, knn_tfidf_predictions)
all_sample_title = 'Accuracy Score: {0}%'.format(np.round(knn_tfidf_score,2)*100)
plt.title(all_sample_title, size = 12)

from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, knn_tfidf_predictions))

from xgboost import XGBClassifier

xgboost_bow = XGBClassifier(random_state=22,learning_rate=0.9)

xgboost_bow.fit(cv_train_reviews,train_sentiments)

xgboost_bow_predictions = xgboost_bow.predict(cv_test_reviews)

model_bow_score = metrics.accuracy_score(test_sentiments,xgboost_bow_predictions)
print('Accuracy:  {:2.2%} '.format(metrics.accuracy_score(test_sentiments, xgboost_bow_predictions)))

xgboost_bow_cm = metrics.confusion_matrix(test_sentiments, xgboost_bow_predictions)
plt.figure(figsize=(5,5))
#sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True)
sns.heatmap(xgboost_bow_cm/np.sum(xgboost_bow_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
print("Confusion matrix:")
print(xgboost_bow_cm)
plt.title(all_sample_title, size = 12)

from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, xgboost_bow_predictions))

xgboost_tfidf= XGBClassifier(random_state=22,learning_rate=0.9)

xgboost_tfidf.fit(tfidf_train_reviews,train_sentiments)

xgboost_tfidf_predictions = xgboost_tfidf.predict(tfidf_test_reviews)

from sklearn.metrics import accuracy_score
xgboost_tfidf_score = metrics.accuracy_score(test_sentiments,xgboost_tfidf_predictions)
print('Accuracy:  {:2.2%} '.format(metrics.accuracy_score(test_sentiments, xgboost_tfidf_predictions)))

xgboost_tfidf_cm = metrics.confusion_matrix(test_sentiments, xgboost_tfidf_predictions)
plt.figure(figsize=(5,5))
#sns.heatmap(cm, annot=True, fmt=".3f", linewidths=.5, square = True)
sns.heatmap(xgboost_tfidf_cm/np.sum(xgboost_tfidf_cm), annot=True, fmt='.2%', cmap='Blues')
plt.ylabel('Actual label')
plt.xlabel('Predicted label')
print("Confusion matrix:")
print(xgboost_tfidf_cm)
plt.title(all_sample_title, size = 12)

from sklearn.metrics import classification_report
print("Classification report\n")
print(classification_report(test_sentiments, xgboost_tfidf_predictions))

