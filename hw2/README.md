Team Name: TAIWAN NO. 1 
Team Member: sshiang, Fred, Bernie
(You may want to look at their repository for more details/implementation)

A. Result: (Dev set)
Precision: 0.542926

B. Preprocsssing
1. lower case
2. remove punctuation
3. stemming/lemmatization

C. Translation Evaluation Algorithms
0. Framentation (complete Meteor funcationalies)
1. Exact match
2. POS tag + Exact match
3. n-gram match (n=2~4)
4. stem match
5. similarity match by word embeddings (Glove)
6. Doc2Vec (treat each sentence as a doc)

E. Fusion Method and Other Tricks
0. Average late fusion of the individual score ouput
1. MLP fusion on train-dev set
2. Grid search for (alpha, beta, gamma)

F. Tools
1. NLTK: stemmer, stopwords, POS tags
2. Glove for word embeddings
