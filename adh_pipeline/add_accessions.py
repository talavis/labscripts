#!/usr/bin/env python3

import sys
import re
import sqlite3
import string

# check if sequence already in db

def add_single_data(data, table, dbcursor) :
    '''Insert a record into a table.
    Will check if data is int or str, meaning the type of the data must fit the datatype in the db.
    data: the data to add (int or str)
    table: the table name
    dbcursor: cursor from the Sqlite object'''

    if type(data) is int :
        dbcursor.execute('''INSERT INTO {tab} VALUES (NULL, {dat})'''.format(tab = table, dat = data))
    elif type(data) is str : 
        dbcursor.execute('''INSERT INTO {tab} VALUES (NULL, "{dat}")'''.format(tab = table, dat = data))
    else :
        sys.stderr.write('Error: unsupported data type: {0}\n'.format(type(data)))
        return False
    return True

def add_spec_class(lat, cla, dbcursor) :
    '''Add a new species-class combination
    lat: species in latin (str)
    cla: class number (int)
    dbcursor: cursor from the Sqlite object'''

    try :
        assert type(cla) is int
    except AssertionError :
        sys.stderr.write('Error: class is not an integer\n')
        return False

    # confirm that species and class are available, otherwise add them
    dbcursor.execute('''SELECT identifier FROM species WHERE latin="{latin}"'''.format(latin = lat))
    try :
        sid = dbcursor.fetchall()[0][0]
    except IndexError :
        sys.stderr.write('ERROR: record {} missing in species, attempting to add\n'.format(lat))
        add_species(lat, dbcursor)
        dbcursor.execute('''SELECT identifier FROM species WHERE latin="{latin}"'''.format(latin = lat))
        sid = dbcursor.fetchall()[0][0]

    dbcursor.execute('''SELECT identifier FROM classes WHERE class={ci}'''.format(ci = cla))
    try :
        cid = dbcursor.fetchall()[0][0]
    except IndexError :
        sys.stderr.write('ERROR: record {} missing in classes, attempting to add\n'.format(lat))
        add_single_data(int(cla), 'classes', c)
        dbcursor.execute('''SELECT identifier FROM classes WHERE class={ci}'''.format(ci = cla))
        cid = dbcursor.fetchall()[0][0]

    c.execute('''SELECT identifier FROM spec_class WHERE speciesID=(SELECT identifier FROM species WHERE latin="{latin}") 
    AND classID=(SELECT identifier FROM classes WHERE class={classnum})'''.format(latin = lat, classnum = int(cla)))
    try :
        scid = c.fetchall()[0][0]
    except IndexError :
        dbcursor.execute('''INSERT INTO spec_class VALUES (NULL, {speciesID}, {classID})'''.format(speciesID = sid, classID = cid))

def add_species(lat, dbcursor) :
    '''Add a new species with only latin name.
    lat: the name of the species in latin (str)
    dbcursor: cursor from the Sqlite object'''
    dbcursor.execute('''INSERT INTO species VALUES (NULL, "{latin}", NULL, NULL)'''.format(latin = lat))
    return True
    
def check_single_record(icolumn, ocolumn, table, irecord, dbcursor) :
    '''Check if a record exists in a database. Assumes AND unless specified
    Will check if irecord is int or str, meaning the type of the data must fit the datatype in the db.

    icolumn: the column to check, i.e. a in "WHERE a=".
    ocolumn: the wanted column, i.e. b in "SELECT b FROM".
    table: the table to check, i.e. c in "FROM c"
    irecord: the record to check for, i.e. d in "WHERE a=d"
    dbcursor: the cursor from the Sqlite object'''
    if type(irecord) is int :
        dbcursor.execute('''SELECT {ocol} FROM {tab} WHERE {icol}={irec}'''.format(icol = icolumn, tab = table, ocol = ocolumn, irec = irecord))
    elif type(irecord) is str :
        dbcursor.execute('''SELECT {ocol} FROM {tab} WHERE {icol}="{irec}"'''.format(icol = icolumn, tab = table, ocol = ocolumn, irec = irecord))
    try :
        identifier = dbcursor.fetchall()[0][0]
    except IndexError :
        return -1
    return identifier

if len(sys.argv) != 4 :
    sys.stderr.write('Usage: {0} <accession file> <database> <table>\n'.format(sys.argv[0]))
    sys.exit()

if __name__ == '__main__' :
    input_file = sys.argv[1]
    db_file = sys.argv[2]
    table_name = sys.argv[3]

    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    # cols: latin, class, subclass, dbname, acc, name, seq
    for line in open(input_file) :
        try :
            cols = re.split('\t', line.strip())
            lat = cols[0].capitalize()
            cla = cols[1]
            sub = cols[2]
            dbn = cols[3]
            acn = cols[4]
            nam = cols[5]
            seq = cols[6]
        except IndexError :
            sys.stderr.write('Error: problem with columns: {}\n'.format(cols))
            continue
        
        if len(sub) == 0 :
            sub = cla

        # check if the accession is present in db
        if check_single_record('accession', 'identifier', 'accessions', acn, c) != -1 :
            sys.stderr.write('NOTE: record {} already in accessions\n'.format(acn))
            continue

        # check if the species is present in db, otherwise add it
        if check_single_record('latin', 'identifier', 'species', lat, c) == -1 :
            add_species(lat, c)

        # check if the class is present in db, otherwise add it
        if check_single_record('class', 'identifier', 'classes', int(cla), c) == -1 :
            add_single_data(int(cla), 'classes', c)

        # check if the spec_class record is present in db, otherwise add it
        spec_class_added = False # if a new spec_class entry is added, set the new acc as preferred, at the end of this script
        c.execute('''SELECT identifier FROM spec_class WHERE speciesID=(SELECT identifier FROM species WHERE latin="{latin}") 
        AND classID=(SELECT identifier FROM classes WHERE class={classnum})'''.format(latin = lat, classnum = int(cla)))
        try :
            scid = c.fetchall()[0][0]
        except IndexError :
            add_spec_class(lat, int(cla), c)
            spec_class_added = True
            c.execute('''SELECT identifier FROM spec_class WHERE speciesID=(SELECT identifier FROM species WHERE latin="{latin}") 
            AND classID=(SELECT identifier FROM classes WHERE class={classnum})'''.format(latin = lat, classnum = int(cla)))
            scid = c.fetchall()[0][0]

        # check if the sequence is present in db, otherwise add it
        seqid = check_single_record('sequence', 'identifier', 'sequences', seq, c)
        if seqid == -1 :
            add_single_data(seq, 'sequences', c)
            seqid = check_single_record('sequence', 'identifier', 'sequences', seq, c)

        c.execute('''INSERT INTO {table} VALUES (NULL, {spec_classID}, "{acc}", "{db}", "{name}", {sequenceID}, {subclass})'''.format(table = table_name, spec_classID = scid,
                                                                                                                                    db = dbn, acc = acn, name = nam, sequenceID = seqid, subclass = sub))
        # if spec_class was new, set the new acc as preffered
        if spec_class_added :
            c.execute('''SELECT identifier FROM accessions WHERE spec_classID = {}'''.format(scid))
            aid = c.fetchall()[0][0]

            c.execute('''INSERT INTO preferred VALUES ({a}, {sc})'''.format(sc = scid, a = aid))
                
    conn.commit()
    conn.close()
