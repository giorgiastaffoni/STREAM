#!/usr/bin/env python3
"""
This script is used to refine the crabs database after the assign_tax step. It removes doubtful records, which generally include the characters 'cf.' 'aff.' 'sp.' or 'nr.', and format the hybrids removing '_' and using '-'. 

Usage: python3 dbrefinement.py input_file output_file
"""

import sys
import re

def clean_records(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            columns = line.strip().split('\t')

            if 'cf.' in columns[8] or 'aff.' in columns[8] or 'sp.' in columns[8] or 'nr.' in columns[8]:
                continue

            if '_x_' in columns[8]:
                parts = columns[8].split('_x_')  # Dividi la stringa basandoti su '_x_'
            # If there are at least 2 parts after '_x_', then proceed with the substitution
                if len(parts) > 1:
                    # Keep the first '_' and substitute the others
                    parts[1] = parts[1].replace('_', '-')
                    # Now merge the parts again creating an updated column 8
                    columns[8] = '_x_'.join(parts)
                    columns[8] = columns[8].replace('_x_', '-x-')

            outfile.write('\t'.join(columns) + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 dbrefinement.py input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    clean_records(input_file, output_file)
