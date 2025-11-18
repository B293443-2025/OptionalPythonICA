#!/usr/bin/python3

import os, shutil, subprocess, re, sys

print("Welcome to the taxon Protein sequence conservation analyser")

#searching for querys using entrez on ncbi and assessing whether conditions are met

#prot_family = 'glucose-6-phosphatase'
#taxon_grp = 'birds'

min_date = None
max_date = None

while True:
    prot_family = input("Choose a protein family: ").strip(" ")
    taxon_grp = input("Choose a taxon group: ").strip(" ")
    
    query = f'{taxon_grp}[ORGN] AND {prot_family}[PROT]'
    cmd = f"esearch -db protein -query '{query}' | efetch -format acc"

    accs = subprocess.check_output(cmd, shell = True, text = True)
    accs_list = accs.split("\n")

    if accs == "":
        print("no results for your query, try again")
        continue
    elif len(accs_list) > 1000:
        print("too many sequences, max is 1000. Choose a different set of queries or add a filter for the date")
        ans = str(input("would you like to add a date filter? (Y/N): "))
        if ans == "Y":
            while True:
                try:
                    min_date = int(input("enter a minimum year (eg. 1999)"))
                    max_date = int(input("enter a maximum year (eg. 1999)"))
                except ValueError:
                    print("type an integer")
                    continue
                if min_date < max_date:
                    break
                else:
                    print("invalid dates, minimum cannot be greater than maximum")
            cmd = f"esearch -db protein -query '{query}' | efilter -mindate {min_date} -maxdate {max_date} | efetch -format acc"
            accs = subprocess.check_output(cmd, shell = True, text = True)
            accs_list = accs.split("\n")
            if accs == "" or len(accs_list) > 1000:
                print("still not acceptable, starting again")
                continue
        else:
            print("Either you have answered N or you have submitted an invalid answer, starting again")
            continue
    break

print(f"your queries {prot_family} and {taxon_grp} are valid, now obtaining sequences in fasta format")
#use entrex to obtain and store all sequences into a file
query = f'{taxon_grp}[ORGN] AND {prot_family}[PROT]'
cmd = f"esearch -db protein -query '{query}' | efetch -format fasta > prot_seqs.fasta"
if min_date:
    cmd = f"esearch -db protein -query '{query}' | efilter -mindate {min_date} -maxdate {max_date} | efetch -format fasta > prot_seqs.fasta"

subprocess.check_output(cmd, shell = True)
#obtain all species
species = set()
with open("prot_seqs.fasta") as prot_seqs:
    for line in prot_seqs:
        if line.startswith(">"):
            spec = re.findall(r'\[.*\]', line)
            for s in spec:
                species.add(s)

#check number of species and warn if its too low
if len(species) < 3:
    answer = input("less than 3 species found, continue? (Y/N): ")
    if answer == "Y":
        print("understood")
    elif answer == "N":
        print("exiting programme, please start again")
        sys.exit(0) #exit program if user wants to start again
    else:
        print("invalid answer, assuming the process will want to be continued")

cmd = f'clustalo -i prot_seqs.fasta -o aligned_seqs_out.fasta --outfmt=fa --force'
subprocess.check_output(cmd, shell = True)

cmd = f'cons -sequence aligned_seqs_out.fasta -outseq consensus_seqs.fasta'
subprocess.check_output(cmd, shell = True)
cmd = f'patmatmotifs -sequence consensus_seqs.fasta -outfile output.patmatmotifs'
subprocess.check_output(cmd, shell = True)

cmd = f'hmoment -seqall consensus_seqs.fasta -graph x11 -outfile hphobicout.hmoment'
subprocess.check_output(cmd, shell = True)

cmd = f'plotcon -sequence aligned_seqs_out.fasta -winsize 4 -graph x11 -goutfile seq_consplt.png'
subprocess.check_output(cmd, shell = True)


