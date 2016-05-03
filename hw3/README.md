Team Name: TAIWAN NO. 1 Team Member: sshiang, Fred, Bernie
(You may want to look at their repository for more details/implementation)

My implementation follows this paper, 
http://www.cs.columbia.edu/~mcollins/pb.pdf

Here is what my teamates did, 
1. insert phrase into arbitrary place.
2. scan sentence both forward and backard, and select the one with highest score.
3. Distance score for insertion point. Tuning by a parameter alpha with range [0,0.2]
4. beam search with future prediction: If scanning the sentence from the beginning and seeing the position i in the sentence, we use score of (i,end) sub-sentence from backward scanning.
5. Parallel processing of all sentences to speed up. We tried some large beam search space ranging from [1000~10000]


We ensemble our results by using the grading script to look for the best decoding score for each sentence. 
The ensemble includes multiple results from different models/parameters.




There are three Python programs here (`-h` for usage):

 - `./decode` a simple non-reordering (monotone) phrase-based decoder
 - `./grade` computes the model score of your output

The commands are designed to work in a pipeline. For instance, this is a valid invocation:

    ./decode | ./grade


The `data/` directory contains the input set to be decoded and the models

 - `data/input` is the input text

 - `data/lm` is the ARPA-format 3-gram language model

 - `data/tm` is the phrase translation model

