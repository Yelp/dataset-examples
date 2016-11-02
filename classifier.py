import pandas as pd
import numpy as np
import pylab as P
from sklearn.tree import DecisionTreeClassifier, export_graphviz

def encode_target(df, target_column):
    df_mod = df.copy()
    targets = df_mod[target_column].unique()
    map_to_int = {name: n for n, name in enumerate(targets)}
    df_mod['Target'] = df_mod[target_column].replace(map_to_int)

    return (df_mod, targets)

def visualize_tree(tree, feature_names):
    with open("dt.dot", 'w') as f:
        export_graphviz(tree, out_file=f,
                        feature_names=feature_names)

    command = ["dot", "-Tpng", "dt.dot", "-o", "dt.png"]
    try:
        subprocess.check_call(command)
    except:
        exit("Could not run dot, ie graphviz, to "
             "produce visualization")

def stars(x):
    if(x[0] == 1):
        return 1
    elif(x[0] == 1.5):
        return 2
    elif(x[0] == 2):
        return 3
    elif(x[0] == 2.5):
        return 4
    elif(x[0] == 3):
        return 5
    elif(x[0] == 3.5):
        return 6
    elif(x[0] == 4):
        return 7
    elif(x[0] == 4.5):
        return 8
    elif(x[0] == 5):
        return 9
    else:
        return 0


#df = pd.read_csv('sliced_dataset.csv', header=0)
df3 = pd.read_csv('test2.csv', header=0)
#df2 = df[['stars']]
#print df2.head(10)

#print df2.apply(stars, axis=0).head(10)
#df2.insert(1, 'star_weight', df2.apply(stars, axis=1)) #calls stars function row by row and inserts in the new columns star_weight at column position 5

#df2.to_csv('test2.csv')

print df3.describe()
print df3.head()
print "done"


#df2 = df[df['review_count'] > 5000][['stars']]
#print df.dtypes

#print df['stars'].hist(bins=16, range=(0,5), alpha = .5)
#P.show()

#print ("Restaurants name: ", df['name'].unique())

#df, targets = encode_target(df, 'name')
#print("* df.head()", df[['id', 'name']].head())


features = df3.columns[1:2]

X = df3['stars']
y = features

dt = DecisionTreeClassifier(min_samples_split=20, random_state=99, criterion='entropy')
#dt.fit(map(lambda x: [x],X),y)
dt.fit(X,y)
visualize_tree(dt, y)
