#!/usr/bin/env python
import optparse
import sys
from collections import defaultdict
from random import random, choice
from math import exp

optparser = optparse.OptionParser()
optparser.add_option("-b", "--bitext", dest="bitext", default="data/dev-test-train.de-en", help="Parallel corpus (default data/dev-test-train.de-en)")
optparser.add_option("-t", "--threshold", dest="threshold", default=0.5, type="float", help="Threshold for aligning with Dice's coefficient (default=0.5)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to use for training and alignment")
(opts, _) = optparser.parse_args()

# Implementation of alignment using IBM Model 2 w/ Diagonal + Markov.
sys.stderr.write("Training with IBM Model 2 w/ Diagonal + Markov...\n")
bitext = [[[x.lower() for x in sentence.strip().split()] for sentence in pair.split(' ||| ')] for pair in open(opts.bitext)][:opts.num_sents]

### IBM Model 2 w/ Diagonal + Markov ###

NUM_ITERATIONS = 5
NUM_TRAINING_DATA = sys.maxint
NONE_INS = True # Whether to align w/ null token as well
P0 = 0.08
LAMBDA = 4.0

def uniform_parameters(p=0.25):
    return defaultdict(lambda: p)

def random_parameters():
    return defaultdict(random)

def align_parameters():
    class _DefDict(dict):
        def __missing__(self, key):
            result = self[key] = dfunc(*key[:-1])
            return result
    return _DefDict()

hdict = {}
ddict = {}

def hfunc(i, j, m, n):
    if (i, j, m, n) not in hdict: hdict[(i, j, m, n)] = - abs(float(i)/m - float(j)/n)
    return hdict[(i, j, m, n)]

def dfunc(i, j, m, n):
    if (i, j, m, n) not in ddict:
        Z = sum([exp(LAMBDA * hfunc(i, j_, m, n)) for j_ in range(n)])
        ddict[(i, j, m, n)] = (1 - P0) * exp(LAMBDA * hfunc(i, j, m, n)) / Z
    return ddict[(i, j, m, n)]

def best_alignment(e, f, params):
    words, align = params
    a = []
    m, n = len(e), len(f)
    a_prev = -1
    for i, e_i in enumerate(e):
        probs = [words[(e_i, f_j)] * align[(i, j, m, n, a_prev)] for j, f_j in enumerate(f)]
        a_prev = choice([j for j, p in enumerate(probs) if p == max(probs)])
        a.append(a_prev)
    return a

def em_iteration(params, bitext):
    words, align = params
    ef_counts = defaultdict(float) # Avoid integer division problems.
    f_counts = defaultdict(float)
    imn_counts = defaultdict(float)
    ijmn_counts = defaultdict(float)
    for (f, e) in bitext:
        m, n = len(e), len(f)
        a_prev = -1
        for i, e_i in enumerate(e):
            deltas = []
            s = sum([align[(i, _j, m, n, a_prev)] * words[(e_i,_f)] for _j, _f in enumerate(f)])
            for j, f_j in enumerate(f):
                delta = align[(i, j, m, n, a_prev)] * words[(e_i,f_j)] / s
                deltas.append(delta)
                ef_counts[(e_i, f_j)] += delta
                f_counts[f_j] += delta
                imn_counts[(i, m, n, a_prev)] += delta
                ijmn_counts[(i, j, m, n, a_prev)] += delta
            a_prev = deltas.index(max(deltas))
    
    for (e, f) in words: # set(params.keys()) | set(ef_counts.keys()):
        words[(e, f)] = ef_counts[(e, f)] / f_counts[f]
    for (i, j, m, n, a_prev) in align:
        align[(i, j, m, n, a_prev)] = ijmn_counts[(i, j, m, n, a_prev)] / imn_counts[(i, m, n, a_prev)] if imn_counts[(i, m, n, a_prev)] else 0.01
    return (words, align)

# Parameters: Expected p(e_i | f_{a_i}).
words, align = uniform_parameters(), align_parameters()
params = (words, align)
if NONE_INS:
    for (f, e) in bitext:
        f.insert(0, None)
for k in range(NUM_ITERATIONS):
    sys.stderr.write("Training model with iteration %i of EM algorithm.\n" % k)
    params = em_iteration(params, bitext[:NUM_TRAINING_DATA])
sys.stderr.write("Finished training model.\n")

for (f, e) in bitext:
    a = best_alignment(e, f, params)
    for (i, a_i) in enumerate(a):
        if a_i > 0 and NONE_INS:
            sys.stdout.write("%i-%i " % (a_i-1, i))
        else:
            sys.stdout.write("%i-%i " % (a_i, i))
    sys.stdout.write("\n")
sys.stderr.write("Finished writing output.\n")

