#!/usr/bin/env python
import optparse
import sys
from collections import defaultdict

import itertools

optparser = optparse.OptionParser()
optparser.add_option("-b", "--bitext", dest="bitext", default="data/dev-test-train.de-en", help="Parallel corpus (default data/dev-test-train.de-en)")
optparser.add_option("-t", "--threshold", dest="threshold", default=0.5, type="float", help="Threshold for aligning with Dice's coefficient (default=0.5)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to use for training and alignment")
(opts, _) = optparser.parse_args()
bitext = [[sentence.strip().split() for sentence in pair.split(' ||| ')] for pair in open(opts.bitext)][:opts.num_sents]

#IBM Model 1

ALIGN_NULL = False;
NUM_ITER = 5;
BOUNDRY_STATE = "###"

def reverse_enumerate(iterable):
    """
    Enumerate over an iterable in reverse order while retaining proper indexes
    """
    return itertools.izip(reversed(xrange(len(iterable))), reversed(iterable))

def addNullToken(bitext):
    for (n, (f, e)) in enumerate(bitext):
        e.append("null");

def initialize(p):
    return defaultdict(lambda: p)

def forward(f, e, trans, align):
    alpha = initialize(1.0)
    for j, e_j in enumerate(e): 
        for i, f_i in enumerate(f):
            #initial condition
            if (j==0):
                alpha[(j, i)] = trans[(e_j, f_i)]
            else:
                alpha[(j, i)] =  sum(alpha[(j-1, k)]*trans[(e_j, f_i)]*align[i-k] for k, f_k in enumerate(f))
    #print sum(alpha[(len(f)-1, k)] for k, e_k in enumerate(e))
    return alpha

def backward(f, e, trans, align):
    beta = initialize(1.0)
    for j, e_j in reverse_enumerate(e):
        for i, f_i in enumerate(f):
            if j==len(e)-1:
                beta[(j, i)] = trans[(e_j, f_i)]
            else:
                beta[(j, i)] = sum(beta[(j+1, k)]*trans[(e_j, f_i)]*align[k-i] for k, f_k in enumerate(f))
    #print sum(beta[(0, k)] for k, e_k in enumerate(e))
    return beta
            
        

#transition probability from Model 1 
def Model1_EM(bitext, num_iter): 
     t = initialize(0.25) 
     for it in xrange(num_iter): 
         sys.stderr.write("EM iter=%d\n" % it)
         #E-step 
         count_e_f = defaultdict(float) 
         total_f = defaultdict(int) 
         for (n, (f, e)) in enumerate(bitext): 
             s_total = defaultdict(float) 
             for e_i in e: 
                 for f_j in f: 
                     s_total[e_i] += t[(e_i,f_j)] 
             for e_i in e: 
                 for f_j in f: 
                     count_e_f[(e_i,f_j)] += t[(e_i,f_j)]/s_total[e_i] 
                     total_f[f_j] += t[(e_i,f_j)]/s_total[e_i] 
         #M-step 
         for (e_i,f_j) in t: 
             t[(e_i, f_j)] = count_e_f[(e_i, f_j)]/total_f[f_j] 
     return t 

def BaumWelch(bitext, NUM_ITER, trans):
    align = initialize(0.01)
    for it in xrange(NUM_ITER):
        sys.stderr.write("BaumWelch iter=%d\n" % it)
        corpus_xi = initialize(0.0)
        for (n, (f, e)) in enumerate(bitext):
            xi = {}
            alpha = forward(f, e, trans, align)    
            beta = backward(f, e, trans, align)
            for t in xrange(len(e)-1):
                sum_xi = 0.0
                for i, f_i in enumerate(f):
                    for j, f_j in enumerate(f):
                        xi[(i, j)] = alpha[(t, i)]*align[j-i]*trans[(e[t+1], f_j)]*beta[(t+1, j)]
                        sum_xi += xi[(i, j)]
                for i, f_i in enumerate(f):
                    for j, f_j in enumerate(f):
                        corpus_xi[(i, j)] += xi[(i, j)]/sum_xi

        #update
        gamma = initialize(0.0)
        for key in corpus_xi.keys():
            gamma[key[0]] += corpus_xi[key]     
        for key in corpus_xi.keys():
            jump = key[1] - key[0]
            align[jump] += corpus_xi[key]/gamma[key[0]]
        sum_align = sum(align.values())
        for key in align.keys():
            align[key] = align[key]/sum_align
    return align


def viterbi(f, e, trans, align):
    viterbi = initialize(0.0)
    backtrack = initialize(-1)
    alignment = []
    for j, e_j in enumerate(e): 
        for i, f_i in enumerate(f):
            #initial condition
            if (j==0):
                viterbi[(j, i)] = trans[(e_j, f_i)]
                backtrack[(j, i)] = i
            else:
                tmp =  [viterbi[(j-1, k)]*trans[(e_j, f_i)]*align[i-k] for k, f_k in enumerate(f)]
                viterbi[(j, i)] = max(tmp)
                backtrack[(j, i)] = tmp.index(max(tmp))
    #print backtrack
    #find max viterbi
    max_prob = 0
    for i in xrange(len(f)):
        if (viterbi[(len(e)-1,i)] >= max_prob): 
            max_prob = viterbi[(len(e)-1,i)]
            max_prob_id = i
    alignment.append(max_prob_id)
    for j in xrange(len(e)-1, 0, -1):
        alignment.append(backtrack[j, (alignment[-1])])
    alignment.reverse()
    return alignment

def main():
    if ALIGN_NULL:
        addNullToken(bitext)    
    trans = Model1_EM(bitext, 5)    
    align = BaumWelch(bitext, 3, trans)
    for (f, e) in bitext:
        alignment = viterbi(f, e, trans, align)
        for i, a in enumerate(alignment):
            sys.stdout.write("%i-%i " % (a, i))
        sys.stdout.write("\n")

if __name__ == "__main__":
    main()
