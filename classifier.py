import pandas as pd
import numpy as np
import pylab as P
from sklearn.tree import DecisionTreeClassifier, export_graphviz

df = pd.read_csv('sliced_dataset.csv', header=0)

print df.describe()
df2 = df[df['review_count'] > 5000][['stars']]
print df.dtypes

#print df['stars'].hist(bins=16, range=(0,5), alpha = .5)
#P.show()

#print ("Restaurants name: ", df['name'].unique())

features = list(df.columns['stars', 'review_count'])

X = df['stars']
y = df[features]

dt = DecisionTreeClassifier(min_samples_split=20, random_state=99)
dt.fit(X, y)
