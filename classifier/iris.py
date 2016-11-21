import pydotplus
from sklearn.datasets import load_iris
from sklearn import tree
iris = load_iris()
clf = tree.DecisionTreeClassifier()
clf = clf.fit(iris.data, iris.target)

with open("iris.dot", 'w') as f:
    f = tree.export_graphviz(clf, out_file=f)

#dot_data = tree.export_graphviz(clf, out_file=None)
#graph = pydotplus.graph_from_dot_data(dot_data)
#graph.write_pdf("iris.pdf")


print clf.predict_proba(iris.data[:1, :])
