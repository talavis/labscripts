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

def rip_acc(header) :
    if acc[:2] in ('sp', 'tr') :
        return(rip_data_uniprot(header))
    else :
        try :
            return(rip_data_ncbi(header))
        except IndexError :
            return(header)

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
