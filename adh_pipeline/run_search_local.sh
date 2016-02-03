#!/bin/bash

if [[ $# -ne 3 ]] ; then
    echo Usage: $0 sequencefile blastdbname sqldbname
    exit 1
fi

SEQS=$1
DB=$2
SQLDB=$3


BASEPATH=`pwd`
HMM=${BASEPATH}/adh.hmm
QUERY=adh
SHORT_DB="${DB##*/}"
SHORT_SQLDB="${SQLDB##*/}"
FULL_SQLDB=${BASEPATH}/${SHORT_SQLDB}

RUNDIR=run-${SHORT_DB}-`date +%d%m%y-%H:%M`
#RUNDIR=run-${SHORT_DB}
#RES_BASE=${RUNDIR}/res_${QUERY}_${SHORT_DB}
RES_BASE=res_${QUERY}

# create run directory
mkdir ${RUNDIR}

cd ${RUNDIR}

if [ -f res_all_nonsig_input ] ; then
    rm res_all_nonsig_input
fi

# run search
if [ "$?" != "0" ] ; then
    break
fi
nice -n 19 blastp -query ${SEQS} -db ${DB} -num_threads 8 -outfmt 5 > ${RES_BASE}${a}_${i}.xml
${BASEPATH}/blast_analyse.py ${RES_BASE}${a}_${i}.xml 67 70 > ${RES_BASE}${a}_${i}_accs # limits at 68% seqid, 70% coverage, assumes all hits will be adhs
let i++

RES_ALL=${RES_BASE}${a}_all
cat ${RES_BASE}${a}_{?,??}_accs | sort | uniq > ${RES_ALL}_accs
if [ -f ${RES_ALL}.fasta ] ; then
	rm ${RES_ALL}.fasta
fi
while read line ; do
    blastdbcmd -dbtype prot -db ${DB} -entry ${line} >> ${RES_ALL}.fasta
done < ${RES_ALL}_accs

${BASEPATH}/split_fasta_titles.py ${RES_ALL}.fasta > ${RES_ALL}_split.fasta

hmmscan --cpu 4 --max --tblout ${RES_ALL}_hmmtable ${HMM} ${RES_ALL}_split.fasta > /dev/null
${BASEPATH}/parse_hmm.py ${RES_ALL}_hmmtable > ${RES_ALL}_restable
sort -k1 ${RES_ALL}_restable | awk -F"[. ]" '!a[$1]++' > ${RES_ALL}_restable_uniq
${BASEPATH}/accs_to_input.py ${RES_ALL}_restable_uniq n > ${RES_ALL}_sig_input
${BASEPATH}/accs_to_input.py ${RES_ALL}_restable_uniq y > ${RES_ALL}_nonsig_input

${BASEPATH}/add_accessions.py ${RES_ALL}_sig_input $FULL_SQLDB accessions

cat ${RES_ALL}_nonsig_input >> res_all_nonsig_input

