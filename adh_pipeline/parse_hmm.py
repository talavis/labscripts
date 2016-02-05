#!/usr/bin/env python3

import sys

if len(sys.argv) != 2 :
    sys.stderr.write('Usage: {0} <hmm table>\n'.format(sys.argv[0]))
    sys.exit()

table = sys.argv[1]

def rip_data_ncbi(title) :
    '''Rip data from a FASTA file from a NCBI database.
    Returned data will be:
    (accession, species, 'NCBI')'''
    parts = title.split('|')
    if parts[2] == 'pir' :
        accession = parts[4]
    elif parts[2] == 'prf' :
        accession = parts[4]
    elif parts[2] == 'pdb' :
        accession = parts[3]+'_'+parts[4][0]
    else :
        accession = parts[3]
    return(accession)

def test_rip_data_ncbi() :
    assert rip_data_ncbi('>gi|86651|pir||A33909') == 'A33909'
    assert rip_data_ncbi('>gi|887492973|pdb|5CDS|A') == '5CDS_A'
    assert rip_data_ncbi('>gi|229330|prf||701201A') == '701201A'
    assert rip_data_ncbi('>gi|929358743|ref|XP_014088683.1|') == 'XP_014088683.1'

def rip_data_uniprot(title) :
    '''Rip data from a FASTA file from a Uniprot database.
    Returned data will be:
    (accession, species, 'Uniprot')'''
    try :
        accession = title.split('|')[1]
    except IndexError :
        sys.stderr.write('ERROR: trouble with title in rip_data_uniprot: {}'.format(title))
        return ''
    return accession

def test_rip_data_uniprot() :
    assert rip_data_uniprot('>tr|W5Q2F4|W5Q2F4_SHEEP') == 'W5Q2F4'

def rip_acc(header) :
    if acc[:2] in ('sp', 'tr') :
        return(rip_data_uniprot(header))
    else :
        try :
            return(rip_data_ncbi(header))
        except IndexError :
            return(header)
        
if __name__ == '__main__' :
    models = list()
    e_values = list()
    acc = ''
    for line in open(table) :
        if line[0] == '#' :
            continue
        cols = line.split()
        if acc != cols[2] :
            if acc != '' :
                outacc = rip_acc(acc)
                if len(outacc.strip()) > 0 :
                    print('\t'.join((outacc , models[e_values.index(min(e_values))], str(min(e_values)))))
                else :
                    sys.stderr.write('ERROR: problem with acc ({})\n'.format(acc))
                models = list()
                e_values = list()
            acc = cols[2] 
    
        models.append(cols[0])
        e_values.append(float(cols[4]))
    
    if acc != '' :
        print('\t'.join((rip_acc(acc), models[e_values.index(min(e_values))], str(min(e_values)))))
