#!/usr/bin/env python3

import re
import sys 

import ncbi_record
import uniprot_record

def is_uniprot(accession) :
    if len(accession) not in (6,10) :
        return False
    pattern = re.compile('[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}')
    if pattern.match(accession) :
        return True
    else :
        return False

def test_is_uniprot() :
    assert is_uniprot('P41681') == True
    assert is_uniprot('A0A0F7YFA1') == True
    assert is_uniprot('ENSG00000172955') == False # Ensembl
    assert is_uniprot('NP_001095940.1') == False # NCBI

    
def prepare_data(accession, adh_class, adh_subclass='') :
    '''Prepares data for output in the format for the db.

    title: str, the FASTA title without '>', can handle NCBI and UniProt
    sequence: str, the residue sequence
    adh_class: str, the number of the ADH class
    adh_subclass: str, the title of the ADH subclass, default empty
    return: (species, adh_class, adh_subclass, database, accession, title, sequence)'''
    if is_uniprot(accession) :
        record = uniprot_record.fetch(accession)
        species = uniprot_record.species(record)[0] # only want latin name
        sequence = uniprot_record.sequence(record)
        title = uniprot_record.title(record)
        db = 'UniProt'
    elif accession[:3] != 'ENS' :
        record = ncbi_record.fetch(accession)
        species = ncbi_record.species(record)
        sequence = ncbi_record.sequence(record)
        title = ncbi_record.title(record)
        db = 'NCBI'
    else :
        sys.stderr.write('Error: unsupported accession: {}\n'.format(accesion))
        return tuple()
    return species, adh_class, adh_subclass, db, accession, title, sequence

def test_prepare_data() :
    # stopped working 160204; seems to be a problem in BioPython, not this code
    #    assert prepare_data('P28332', 5) ==
    assert prepare_data('NP_001095940.1', 5) == ('Homo sapiens', 5, '', 'NCBI', 'NP_001095940.1', 'alcohol dehydrogenase 6 isoform 1 [Homo sapiens]',
                                              'MSTTGQVIRCKAAILWKPGAPFSIEEVEVAPPKAKEVRIKVVATGLCGTEMKVLGSKHLDLLYPTILGHEGAGIVESIGEGVSTVKPGDKVITLFLPQCGECTSCLNSEGNFCIQFKQSKTQLMSDGTSRFTCKGKSIYHFGNTSTFCEYTVIKEISVAKIDAVAPLEKVCLISCGFSTGFGAAINTAKVTPGSTCAVFGLGGVGLSVVMGCKAAGAARIIGVDVNKEKFKKAQELGATECLNPQDLKKPIQEVLFDMTDAGIDFCFEAIGNLDVLAAALASCNESYGVCVVVGVLPASVQLKISGQLFFSGRSLKGSVFGGWKSRQHIPKLVADYMAEKLNLDPLITHTLNLDKINEAVELMKTGKCIRCILLL')

if __name__ == '__main__' :
    if len(sys.argv) < 3 or len(sys.argv) > 5 :
        sys.stderr.write('Usage: {0} <file with accessions and classes> <print non-significant instead of significant y/n> [ADH subclass]\n'.format(sys.argv[0]))
        sys.exit()

    ncbi_record.setup('email@example.com')

    filename = sys.argv[1]
    if sys.argv[2].lower() not in ('y', 'n') :
        sys.stderr.write('ERROR: print_nonsig should be y or n, not {}\n'.format(sys.argv[2])) 
        sys.exit()
    print_nonsig = True if sys.argv[2].lower() == 'y' else False

    for line in open(filename) :
        cols = line.split('\t')
        if float(cols[2]) > 1E-200 and print_nonsig :
            res = prepare_data(cols[0], cols[1])
            if len(res) > 0 :
                print('\t'.join(res))
        elif not print_nonsig :
            res = prepare_data(cols[0], cols[1])
            if len(res) > 0 :
                print('\t'.join(res))
