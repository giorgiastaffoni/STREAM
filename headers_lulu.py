#!/usr/bin/env python3
'''
This script modifies the header of a fasta file to create a lulu-compatible format.

Usage: python3 headers_lulu.py input_file output_file
'''

import argparse
import re

def modify_lulu_header(file_input, file_output):
    with open(file_input, 'r') as input_file, open(file_output, 'w') as output_file:
        for line in input_file:
            if line.startswith('>'):
                # Extract the OTU info with the corresponding number 
                match = re.match(r'.*otu-(\d+)-.*', line)
                if match:
                    otu_number = match.group(1)
                    output_file.write(f'>otu{otu_number}\n')
            else:
                output_file.write(line)

def main():
    parser = argparse.ArgumentParser(description='Modify headers of a fasta file')
    parser.add_argument('file_input', help='Path to the input FASTA file')
    parser.add_argument('file_output', help='Path to the output FASTA file')
    
    args = parser.parse_args()
    
    modify_lulu_header(args.file_input, args.file_output)
    
if __name__ == "__main__":
    main()

