#!/usr/bin/env python3

import sys

from Bio import SeqIO

if __name__ == '__main__' :

    if len(sys.argv) != 2 :
        sys.stderr.write('Usage: {} <fasta file>\n'.format(sys.argv[0]))
        sys.exit()

    records = list(SeqIO.parse(sys.argv[1], 'fasta'))

    descs = list()

    recs = list()
    for r in records :
        if r.description not in descs :
            recs.append(r)
            descs.append(r.description)

    for i in range(len(recs)) :
        titles = descs[i]. split(' >')
        for j in range(len(titles)) :
            print('>' + titles[j])
            print(recs[i].seq)
