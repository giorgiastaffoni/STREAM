#!/usr/bin/env python3
'''
Remove the sequences of the species listed in the unwanted_species.txt file. 

Usage: python3 remove_unwanted-species.py input_file.fasta unwanted_species.txt
'''

import sys

if len(sys.argv) != 3:
    print("Usage: python script.py input_file.fasta species_to_remove.txt")
    sys.exit(1)

# Read names from the unwanted_species.txt file
input_fasta_file = sys.argv[1]
species_to_remove_file = sys.argv[2]

with open(species_to_remove_file, 'r') as file:
    species_to_remove = [line.strip() for line in file]

with open(input_fasta_file, 'r') as file:
    lines = file.readlines()

# Create a new database with the filtered species
output_fasta_file = input_fasta_file.split('.')[0] + "_filtered.fasta"

with open(output_fasta_file, 'w') as file:
    should_remove = False
    for line in lines:
        if line.startswith('>'):
            header = line[1:].strip()
            if header in species_to_remove:
                should_remove = True
            else:
                should_remove = False
                file.write(line)
        else:
            if not should_remove:
                file.write(line)

print(f"Unwanted species were removed from the fasta file. The new version is saved as {output_fasta_file}.")
