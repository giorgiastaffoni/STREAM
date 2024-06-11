#!/usr/bin/env python3
"""
Length filtering step to be applied after in silico pcr

Usage: python3 length-filtering.py file_input --max_length threshold
"""

import sys
from Bio import SeqIO

def filter_sequences(input_file, length_threshold):
    marker_name = input_file.split('_')[0] #Obtain the marker's name from the input file

    # Create two files: one for the accepted - filtered - reads and one for the discarded ones
    output_reads = open(f"{marker_name}_filtered_reads.fasta", "w")
    output_discarded = open(f"{marker_name}_discarded_reads.fasta", "w")

    for record in SeqIO.parse(input_file, "fasta"):
        if len(record.seq) <= length_threshold:
            output_reads.write(f">{record.id}\n{record.seq}\n")
        else:
            output_discarded.write(f">{record.id}\n{record.seq}\n")

    output_reads.close()
    output_discarded.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 length-filtering.py file_input --max_length length_threshold")
        sys.exit(1)
    file_input = sys.argv[1]
    length_threshold = int(sys.argv[3])

    filter_sequences(file_input, length_threshold)
