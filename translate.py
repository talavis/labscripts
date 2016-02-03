#!/usr/bin/env python3

# Copyright (c) 2015-2016, Linus Östberg

'''
Translate a FASTA file DNA->protein
'''

import sys
import os

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

def translate(sequence, frame = 0) :
    protseq = ''
    for i in range(frame, len(sequence), 3) :
        new_cod = sequence[i:i+3]
        if len(new_cod) == 3 :
            if 'N' in new_cod :
                protseq += 'X'
            else :
                protseq += CODONS[new_cod]

    return protseq

def test_translate() :
    assert translate('TTTGCGGAGCTA') == 'FAEL'

CODONS = {'TTT':'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
          'TCT':'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
          'TAT':'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
          'TGT':'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',

          'CTT':'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
          'CCT':'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
          'CAT':'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
          'CGT':'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',

          'ATT':'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
          'ACT':'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
          'AAT':'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
          'AGT':'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',

          'GTT':'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
          'GCT':'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
          'GAT':'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
          'GGT':'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}

if __name__ == '__main__' :
    if len(sys.argv) not in [2,3] :
        sys.stderr.write('Usage: {0} <filename> [readingframe (0-2)]\n'.format(sys.argv[0]))
        sys.exit()
    if len(sys.argv) == 3 :
        read_frame = int(sys.argv[2]) % 3
    else :
        read_frame = 0
    
    headers, seqs = read_sequences(sys.argv[1])

    for s in range(len(seqs)) :
        print('>' + headers[s])
        print(translate(seqs[s]))
