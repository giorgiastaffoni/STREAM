#!/usr/bin/env python3
"""
Transform a database from an idt-fasta-format created with CRABS to a barque-friendly format

Usage: python3 idt2barque.py input_fasta output_fasta
"""

import argparse
from Bio import SeqIO

# Def function for extracting "Family_Genus_Species" from the header of the input file
def format_header(header):
    parts = header.split(";")
    famiglia = parts[-3]
    genere_specie = parts[-1]
    return f"{famiglia}_{genere_specie}"

parser = argparse.ArgumentParser(description="Reformat FASTA headers.")
parser.add_argument("input_file", help="Nome del file FASTA di input")
parser.add_argument("output_file", help="Nome del file FASTA di output")

args = parser.parse_args()

with open(args.output_file, "w") as out_handle, open(args.input_file, "r") as in_handle:
    for record in SeqIO.parse(in_handle, "fasta"):
        new_header = format_header(record.description)
        record.description = ""  # Rimuovi la descrizione originale
        record.id = new_header
        SeqIO.write(record, out_handle, "fasta-2line")

print("idt-fasta file converted into a barque-friendly format :)")

