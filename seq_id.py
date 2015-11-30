#!/usr/bin/env python3

'''calculate sequence identity and similar statics for an alignment in FASTA format'''

import sys

import numpy

def calc_distance(sequences, skip_gaps) :
    '''Calculate the pairwise sequence identities in an alignment'''
    # calculate distances
    matrix = list()
    results = list()
    for i in range(len(sequences)) :
        for j in range(i+1, len(sequences)) :
            pos_id = compare_pair_res(sequences[i], sequences[j], skip_gaps)
            if len(pos_id) != 0 :
                seqid = sum(pos_id)/len(pos_id)
                results.append(round(seqid, 4))
    return results

def test_calc_distance() :
    assert calc_distance(('AAAAA', 'AAAAA', 'AAAAA'), True) == [1.0, 1.0, 1.0]
    assert calc_distance(('AAAAA', 'AAAAA', '-----', '-----'), True) == [1.0]
    assert calc_distance(('AAAAA', 'AAAAA', '-----', 'CCCCC'), True) == [1.0, 0.0, 0.0]
    assert calc_distance(('AAAAA', '-----', 'CCCCC'), False) == [0.0, 0.0, 0.0]
    assert calc_distance(('AAAAA', 'AA-CC', 'CCCCC'), False) == [0.4, 0.0, 0.4]
            
# compare the residues
def compare_pair_res(sequence1, sequence2, skip_gaps) :
    # len should be same
    results = list()
    for i in range(len(sequence1)) :
        if skip_gaps : 
            if sequence1[i] == '-' or sequence2[i] == '-' :
                continue
        if sequence1[i] == sequence2[i] :
            results.append(1)
        else :
            results.append(0)
    return results

def test_compare_pair_res() :
    assert compare_pair_res('ACDEFGHIK', 'ACDEFGHIK', True) == [1, 1, 1, 1, 1, 1, 1, 1, 1]
    assert compare_pair_res('ACDEFGHIK', 'ACDE-----', True) == [1, 1, 1, 1]
    assert compare_pair_res('ACDEFGHIK', 'ACDE-----', False) == [1, 1, 1, 1, 0, 0, 0, 0, 0]
    assert compare_pair_res('ACDEFGHIK', 'ACDEEEEEE', False) == [1, 1, 1, 1, 0, 0, 0, 0, 0]
    
def print_results(results) :
    print('Median: ', numpy.median(results))
    print('Average: ', numpy.average(results))
    print('Max: ', max(results))
    print('Min: ', min(results))
        
def read_sequences(filename) :
    headers = list()
    sequences = list()
    with open(filename) as infile :
        for line in infile :
            if line[0] == '>' :
                headers.append(line[1:-1])
                sequences.append('')
            elif len(sequences) > 0 :
                # sequence continued
                sequences[-1] += line.strip()

    return headers, sequences

def test_read_sequences() :
    import tempfile
    import os

    text = '''
>protein1
ACDEFGHIKLMNPQRST
>protein2
ACDEFGHIK
LMN-QRST'''

    file_name = tempfile.mkstemp()[1]
    with open(file_name, 'w') as f:
        f.write(text)

    assert read_sequences(file_name) == (['protein1', 'protein2'],
                                         ['ACDEFGHIKLMNPQRST', 'ACDEFGHIKLMN-QRST'])
    os.unlink(file_name)

if __name__ == '__main__' :
    if len(sys.argv) not in (2, 3) :
        print('Usage {0} <alignment file> <skip gaps y/N>'.format(sys.argv[0]))
        sys.exit()

    if len(sys.argv) == 3 and sys.argv[2].lower() == 'y' :
        GAPS_SKIP = True
    else :
        GAPS_SKIP = False
        
    heads, seqs = read_sequences(sys.argv[1])
    results = calc_distance(seqs, GAPS_SKIP)
    
    print_results(results)

    



