#!/usr/bin/env python
import optparse
import sys

def main():
    # parse commandline
    optparser = optparse.OptionParser()
    optparser.add_option("-f", "--forward", type="string", dest="f_forward", help="forward alignment f->e")
    optparser.add_option("-b", "--backward", type="string", dest="f_backward", help="backward alignment e->f")
    optparser.add_option("-n", "--number", type="int", default = sys.maxint, dest="num", help="number of line to process")
    optparser.add_option("-m", "--mode", type="string", dest="mode", help="mode")
    (opts, _) = optparser.parse_args()
    
    sys.stderr.write("Symmetrize forward and backward alignments...\n")
    # open files
    fw = open(opts.f_forward).read().split('\n')
    bw = open(opts.f_backward).read().split('\n')
    assert(len(bw)==len(fw))

    # symmetrize alignmenr
    for i in range(min(len(fw),opts.num)):
        fw_align = set(fw[i].strip().split())
        bw_align = set()
        #aligned_e = set()
        #aligned_f = set()
        
        # find intersection & union
        for al in bw[i].strip().split():
            f, e = al.split('-')
            bw_align.add('{}-{}'.format(e, f))
        intersection = fw_align & bw_align
        union = fw_align | bw_align

        max_e = 0
        max_f = 0
        for al in intersection:
            e, f = al.split('-')
            e = int(e)
            f = int(f)
            if e > max_e: max_e = e
            if f > max_f: max_f = f
            #aligned_e.add(e)
            #aligned_f.add(f)
        
        #new_alignment = grow_diag(intersection, union, aligned_e, aligned_f, max_e+1, max_f+1)
        new_alignment = grow_diag(intersection, union, max_e+1, max_f+1)

        #symmetrized = alignment
        if opts.mode == "intersect":
            symmetrized = list(intersection)
        if opts.mode == "union":
            symmetrized = list(union)
        if opts.mode == "grow_diag":
            symmetrized = new_alignment
        symmetrized = sorted(list(symmetrized), key=lambda al: int(al.split('-')[0]))
        print ' '.join(symmetrized)

#def grow_diag(intersection, union, aligned_e, aligned_f, len_e, len_f):
def grow_diag(intersection, union, len_e, len_f):
    while True:
        align = set()
        for i in range(len_e): # search through all possible grids
            for j in range(len_f):
                current = '{}-{}'.format(i,j)
                if (current in union)and (current not in intersection): # and ((i not in aligned_e) or (j not in aligned_f)): # removed based on multi-multi ground truth
                    # condifent diagnoal (*2 consective intesections)
                    if ('{}-{}'.format(i+1,j+1) in intersection) and ('{}-{}'.format(i+2,j+2) in intersection): 
                        align.add(current)
                        #aligned_e.add(i)
                        #aligned_f.add(j)

                    if ('{}-{}'.format(i-1,j-1) in intersection) and ('{}-{}'.format(i-2,j-2) in intersection):
                        align.add(current)
                        #aligned_e.add(i)
                        #aligned_f.add(j)

                    if ('{}-{}'.format(i+1,j-1) in intersection) and ('{}-{}'.format(i+2,j-2) in intersection):
                        align.add(current)
                        #aligned_e.add(i)
                        #aligned_f.add(j)
            
                    if ('{}-{}'.format(i-1,j+1) in intersection) and ('{}-{}'.format(i-2,j+2) in intersection):
                        align.add(current)
                        #aligned_e.add(i)
                        #aligned_f.add(j)

                    # sandwich
                    if ('{}-{}'.format(i+1,j+1) in intersection) and ('{}-{}'.format(i-1,j-1) in intersection):
                        align.add(current)
                        #aligned_e.add(i)
                        #aligned_f.add(j)

                    if ('{}-{}'.format(i+1,j-1) in intersection) and ('{}-{}'.format(i-1,j+1) in intersection):
                        align.add(current)
                        #aligned_e.add(i)
                        #aligned_f.add(j)
                    if ('{}-{}'.format(i,j+1) in intersection) and ('{}-{}'.format(i,j-1) in intersection):
                        align.add(current)
                        #aligned_e.add(i)
                        #aligned_f.add(j)

                    if ('{}-{}'.format(i-1,j+0) in intersection) and ('{}-{}'.format(i-2,j+0) in intersection):
                        align.add(current)
                        #aligned_e.add(i)
                        #aligned_f.add(j)
        intersection = intersection | align
        if len(align)==0: 
            break
    return intersection

if __name__=='__main__':
  main()
