import argparse # optparse is deprecated
from itertools import islice # slicing for iterators

import numpy as np 
import codecs,sys,string

from scipy.spatial import distance

import os.path
import pickle

from nltk.corpus import stopwords

margin = 0.0001
threshold = 0.0001
exclude = set(string.punctuation)

word2vec_dim = 300

def load_word2vec():
    fin= codecs.open("/home/ubuntu/tools/GloVe-1.2/pretrained/glove.6B.300d.txt", encoding='utf-8')    
    word2vec = {}
    for line in fin:
        items = line.replace('\r','').replace('\n','').split(' ')
        word = items[0]
        vect = np.array([float(i) for i in items[1:]])
        word2vec[word] = vect
    return word2vec


def remove_punctuation(context):
    return ''.join(ch if ch not in exclude else " " for ch in context)


# DRY
def word_matches(h, ref):
    return sum(1 for w in h if w in ref)
    # or sum(w in ref for w in f) # cast bool -> int
    # or sum(map(ref.__contains__, h)) # ugly!
 
def main():
    parser = argparse.ArgumentParser(description='Evaluate translation hypotheses.')
    # PEP8: use ' and not " for strings
    parser.add_argument('-i', '--input', default='data/train-test.hyp1-hyp2-ref',
            help='input file (default data/train-test.hyp1-hyp2-ref)')
    parser.add_argument('-n', '--num_sentences', default=None, type=int,
            help='Number of hypothesis pairs to evaluate')
    # note that if x == [1, 2, 3], then x[:None] == x[:] == x (copy); no need for sys.maxint
    opts = parser.parse_args()
 
    # we create a generator and avoid loading all sentences into a list
    def sentences():
        with codecs.open(opts.input, encoding='utf-8') as f:
            for pair in f:
                yield [sentence for sentence in pair.split(' ||| ')]
 
    #load word vectors
    if not os.path.isfile("./word2vec.pkl"):
        word2vec = load_word2vec()
        with open('./word2vec.pkl', 'wb') as handle:
            pickle.dump(word2vec, handle)
    else:
        with open('./word2vec.pkl', 'rb') as handle:
            word2vec = pickle.load(handle)

    # note: the -n option does not work in the original code
    tmp = ""
    f_feature = open("feature4", "w");
    for h1, h2, ref in islice(sentences(), opts.num_sentences):
        h1 = remove_punctuation(''.join(h1.lower())).split(' ')
        h2 = remove_punctuation(''.join(h2.lower())).split(' ')
        ref = remove_punctuation(''.join(ref.replace("\n", "").lower())).split(' ')
        
        #h1 = [word for word in h1 if word not in stopwords.words('english')]
        #h2 = [word for word in h2 if word not in stopwords.words('english')]
        #ref = [word for word in ref if word not in stopwords.words('english')]
        
        #h1vec = np.array([word2vec[w] if w in word2vec else np.zeros((word2vec_dim, )) for w in h1])
        h1vec = np.array([word2vec[w] for w in h1 + ['.'] if w in word2vec ])
        h2vec = np.array([word2vec[w] for w in h2 + ['.'] if w in word2vec ]) 
        refvec = np.array([word2vec[w] for w in ref + ['.'] if w in word2vec ]) 
        #print h1vec.shape
        #print h2vec.shape
        #print refvec.shape
        #d_h1_ref = distance.cdist(refvec, h1vec, 'euclidean') 
        #d_h2_ref = distance.cdist(refvec, h2vec, 'euclidean') 
        d_h1_ref = distance.cdist(refvec, h1vec, 'cosine') 
        d_h2_ref = distance.cdist(refvec, h2vec, 'cosine') 
        d_h1_h2 = distance.cdist(h2vec, h1vec, 'cosine')        

        h1_score = np.sum(np.min(d_h1_ref,1))/(refvec.shape[0])
        h2_score = np.sum(np.min(d_h2_ref,1))/(refvec.shape[0])

        hscore = (np.sum(np.min(d_h1_h2,1))/(h2vec.shape[0]) + np.sum(np.min(d_h1_h2,0))/(h1vec.shape[0])) * 0.5
        
        print >>f_feature, h1_score - h2_score, hscore, float(refvec.shape[0])/h1vec.shape[0] - float(refvec.shape[0])/h2vec.shape[0] 
        #print h1_score
        #print h2_score
        #print hscore
        #print "-"*50

        if h1_score < h2_score and abs(h1_score - h2_score) > margin and hscore > threshold:
            print -1
        elif h1_score > h2_score and abs(h1_score - h2_score) > margin and hscore > threshold:
            print 1
        else:
            print 0
    f_feature.close()
# convention to allow import of this file as a module
if __name__ == '__main__':
    main()
