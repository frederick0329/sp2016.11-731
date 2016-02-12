#!/usr/bin/env python
import optparse
import sys
from collections import defaultdict

optparser = optparse.OptionParser()
optparser.add_option("-b", "--bitext", dest="bitext", default="data/dev-test-train.de-en", help="Parallel corpus (default data/dev-test-train.de-en)")
optparser.add_option("-t", "--threshold", dest="threshold", default=0.5, type="float", help="Threshold for aligning with Dice's coefficient (default=0.5)")
optparser.add_option("-n", "--num_sentences", dest="num_sents", default=sys.maxint, type="int", help="Number of sentences to use for training and alignment")
(opts, _) = optparser.parse_args()
bitext = [[sentence.strip().split() for sentence in pair.split(' ||| ')] for pair in open(opts.bitext)][:opts.num_sents]

#IBM Model 1

ALIGN_NULL = True;
NUM_ITER = 5;

def addNullToken(bitext):
    for (n, (f, e)) in enumerate(bitext):
        e.append("null");

def initialize(p=0.25):
    return defaultdict(lambda: p)

def EM(bitext, num_iter):
    t = initialize()
    for it in xrange(num_iter):
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

def decode(f, e, params):
    alignment = []
    for i, e_i in enumerate(e[:len(e)-1]):
        t_prob = [params[(e_i, f_j)] for f_j in f]
        alignment.append(t_prob.index(max(t_prob)))
    return alignment 

def main():
    if ALIGN_NULL:
        addNullToken(bitext)    
    params = EM(bitext, NUM_ITER)
    for (f, e) in bitext:
        alignment = decode(f, e, params)
        for i, a in enumerate(alignment):
            sys.stdout.write("%i-%i " % (a, i))
        sys.stdout.write("\n")

if __name__ == "__main__":
    main()
