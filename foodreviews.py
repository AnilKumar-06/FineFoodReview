# -*- coding: utf-8 -*-
"""FoodReviews.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14sxTQF3A9zDzkALEh10heHplUkHKELCX
"""

from google.colab import drive
drive.mount('/content/drive/')

import pandas as pd
import re
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nltk
import string
import sqlite3
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import confusion_matrix
from sklearn import metrics
from sklearn.metrics import roc_curve, auc 
from nltk.stem.porter import PorterStemmer

con = sqlite3.connect("/content/drive/My Drive/ML_Projects/database.sqlite")

filtered_data = pd.read_sql_query("""SELECT *FROM  Reviews WHERE Score != 3""", con)
filtered_data.head()

def partition(x):
  if x<3:
    return 'negative'
  else:
    return 'positive'

#changing reviews with score less than 3 to be negative and vice versa
actual_score = filtered_data['Score']
positive_negative = actual_score.map(partition)
filtered_data['Score'] = positive_negative

filtered_data.shape

filtered_data.head(100)

#data Cleaning Dediplication(remove duplicate reviews)
display = pd.read_sql_query("""SELECT *FROM Reviews WHERE Score != 3 AND UserId = "AR5J8U146CURR" ORDER BY ProductId""",con)

#sorting by product id
sorted_data = filtered_data.sort_values('ProductId', axis = 0, ascending = True)

#deduplication of entries
final = sorted_data.drop_duplicates(subset={'UserId','ProfileName','Time','Text'},keep = 'first', inplace = False)

#check Remaining data in %
(final['Id'].size*1.0)/(filtered_data['Id'].size*1.0)*100

display = pd.read_sql_query("""SELECT *FROM Reviews WHERE Score != 3 AND Id = "44737" or Id = "64422" """,con)
display

final  = final[final.HelpfulnessNumerator <= final.HelpfulnessDenominator]
print(final.shape)

#count of each rating(review)
final['Score'].value_counts()

i=0;
for sent in final['Text'].values:
  if(len(re.findall('<.*?>', sent))):
    print(i)
    print(sent)
    break;
  i += 1;

!pip install -q wordcloud
import wordcloud

import nltk
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

#import re
import nltk
#nltk.download()
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer

#set of stopwords and initializing the snowball stemmer
stop = set(stopwords.words('english'))
sno = nltk.stem.SnowballStemmer('english')

def cleanHtml(sentence):
  cleaner = re.compile('<.*?>')
  cleantext = re.sub(cleaner, ' ', sentence)
  return cleantext


def cleanPunc(sentence):
  cleaned = re.sub(r'[?|!|\'|"|#]', r'',sentence)
  cleaned = re.sub(r'[.|,|)|(|\|/]', r' ',cleaned)
  return cleaned

print(stop)
print("\n*******************************************")
print("Base word of tasty = ",sno.stem('tasty'))

i=0
str1 = ' '
final_string = []
all_positive_word = []
all_negative_word = []
s = ''
for sent in final['Text'].values:
  filtered_sentence = []
  sent = cleanHtml(sent)
  for w in sent.split():
    for cleaned_words in cleanPunc(w).split():
      if ((cleaned_words.isalpha()) & (len(cleaned_words)>2)):
        if (cleaned_words.lower() not in stop):
          s = (sno.stem(cleaned_words.lower())).encode('utf8')
          filtered_sentence.append(s)
          if(final['Score'].values)[i] == 'positive':
            all_positive_word.append(s)
          if (final['Score'].values)[i] == 'negative':
            all_negative_word.append(s)
          else:
            continue
        else:
          continue
  str1 = b" ".join(filtered_sentence)
  final_string.append(str1)
  i += 1

final['cleanedText'] = final_string

final.head(3)

conn = sqlite3.connect('final.sqlite')
c = conn.cursor()
conn.text_factory = str
final.to_sql('Reviews', conn, schema=None, if_exists='replace')

freq_dist_pos = nltk.FreqDist(all_positive_word)
freq_dist_neg = nltk.FreqDist(all_negative_word)
print("Most Common Positive word : ",freq_dist_pos.most_common(20))
print("Most Common Negative word : ",freq_dist_neg.most_common(20))

#bi-grma and n-gram
from sklearn.feature_extraction.text import CountVectorizer
count_vect = CountVectorizer(ngram_range = (1,2))
final_bigram_counts = count_vect.fit_transform(final['Text'].values)

final_bigram_counts.get_shape()

#TF-IDF

tf_idf_vect = TfidfVectorizer(ngram_range=(1,2))
final_tf_idf = tf_idf_vect.fit_transform(final['Text'].values)

final_tf_idf.get_shape()

features = tf_idf_vect.get_feature_names()
len(features)

features[100000:100010]

print(final_tf_idf[3, :].toarray()[0])

def top_tfidf_feats(row, features, top_n = 25):
  top_ids = np.argsort(row)[::-1][:top_n]
  top_feats = [(features[i], row[i]) for i in top_ids]
  df = pd.DataFrame(top_feats)
  df.columns = ['feature', 'tfidf']
  return df

top_tfidf = top_tfidf_feats(final_tf_idf[1,:].toarray()[0], features, 25)

top_tfidf

from gensim.models import word2vec
from gensim.models import KeyedVectors
import pickle

model = KeyedVectors.load_word2vec_format('/content/drive/My Drive/ML_Projects/GoogleNews-vectors-negative300.bin', binary=True)

model.wv['computer']

model.wv.similarity('woman', 'man')

model.wv.most_similar('woman')

model.wv.most_similar('tasty')

model.wv.similarity('tasty', 'tast')



#train our own w2v model using your own text corpus
import gensim
i=0
list_of_sent = []
for sent in final['Text'].values:
  filtered_sentence = []
  sent = cleanHtml(sent)
  for w in sent.split():
    for cleaned_word in cleanPunc(w).split():
      if (cleaned_word.isalpha()):
        filtered_sentance.append(cleaned_word.lower())

      else:
        continue
  list_of_sent.append(filtered_sentance)

print(final['Text'].values[0])

print("************************************************")
print(list_of_sent[0])

from gensim.models import word2vec
from gensim.models import KeyedVectors
import pickle

w2v_model = gensim.models.word2vec(list_of_sent, min_count=5, size=50, workers=4)
words = list(w2v_model.wv.vocab)
print(len(words))
w2v_model.wv.most_similar('tasty')
w2v_model.wv.most_similar('like')
count_vec_feat = count_vect.get_feature_names()
count_vect_feat.index('like')
print(count_vect_feat[64055])

