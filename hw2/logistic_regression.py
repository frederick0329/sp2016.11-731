import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier

NUM_TRAIN = 5000
def loadData():
    f_label = open("./data/train.gold", "r")
    f_feature = open("feature5", "r")
    labels = f_label.readlines()
    features = f_feature.readlines()
    y = []
    X = []
    
    for l in labels:
        y.append(int(l.split("\n")[0]))
    for f in features:
        X.append([float(i) for i in f.split()[0:5]])
    
    return np.array(X), np.array(y) 
        
    




def main():
    f_pred = open("out", "w")
    X, y = loadData()
    
    #X = (X - X.min(0)) / X.ptp(0)
    
    #X[:,2] = X[:,2]/100
    #clf = svm.SVC(C=1, kernel="linear", class_weight="balanced")
    #clf = LogisticRegression(class_weight='balanced') 
    #clf = RandomForestClassifier(3) 
    clf = AdaBoostClassifier() 
    clf.fit(X[:NUM_TRAIN], y[:NUM_TRAIN])   
    pred = clf.predict(X)
    for i in pred:
        print >> f_pred, i     

    f_pred.close()
    
if __name__ == '__main__':
    main()

