#!/usr/bin/env python3

import sys
import urllib.request

from Bio import SwissProt

def fetch(acc) :
    '''Downloads data from UniProt.
    Input: 
    acc: accession code of the record
    database: database name
    Return: the Entrez record
    '''
    base_url = 'http://www.uniprot.org/uniprot/'
    handle = urllib.request.urlopen(base_url + acc + '.txt')
    record = SwissProt.read(handle)
    return record

def sequence(record) :
    '''Input: UniProt record from SwissProt.read()
    Return: species name (str)
    '''
    return record.sequence

def species(record) :
    '''Input: UniProt record from SwissProt.read()
    Return: latin and english species names (str, str)
    '''
    os = record.organism
    os = os.replace('.', ' ')
    try :
        latin = os[:os.index('(')].strip()
        #        english = os[os.index('(')+1:-os[::-1].index(')')-1].strip()
        english = os[os.index('(')+1:os.index(')', os.index('('))].strip()
    except ValueError :
        latin = os.strip()
        english = ''
    return latin, english

def title(record) :
    '''Input: UniProt record from SwissProt.read()
    Return: protein name (str)
    '''
    return record.description


if __name__ == '__main__' :
    sys.exit()
