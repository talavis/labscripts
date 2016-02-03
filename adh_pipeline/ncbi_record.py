#!/usr/bin/env python3

import sys

from Bio import Entrez

def fetch(acc, database='protein') :
    '''Downloads data from Entrez.
    Input: 
    acc: accession code of the record
    database: database name
    Return: the Entrez record
    '''
    try :
        handle = Entrez.efetch(db = database, id = acc, retmode = 'xml')
    except :
        sys.stderr.write('ERROR: problem accessing {}\n'.format(acc))
    return Entrez.read(handle)[0]

def sequence(record) :
    '''Input: ncbi record from Entrez.read()
    Return: species name (str)
    '''
    return record['GBSeq_sequence'].upper()

def setup(email) :
    Entrez.email = email

def species(record) :
    '''Input: ncbi record from Entrez.read()
    Return: species name (str)
    '''
    return record['GBSeq_organism']

def title(record) :
    '''Input: UniProt record from SwissProt.read()
    Return: protein title (str)
    '''
    return record['GBSeq_definition']

if __name__ == '__main__' :
    sys.exit()
