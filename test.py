#%matplotlib inline

import pandas as pd
import numpy as np
from pandas import DataFrame
import datetime
import pandas.io.data
import seaborn as sns
from sklearn.feature_extraction.text import CountVectorizer

df = pd.read_csv('business.csv', index_col='business_id', low_memory=False)
#print df.head(20)

df2 = df[['name', 'stars', 'review_count', 'full_address', 'city', 'state', 'latitude', 'longitude','categories']]

print (df2.head(100))

df2.to_csv('test.csv')
