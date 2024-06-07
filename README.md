# STREAM

This repo represents the workflow used in the following paper:
"Comparison of environmental DNA metabarcoding and electrofishing in freshwater systems of northwestern Italy" (Ballini & Staffoni, submitted to Hydrobiologia)
based on the datasets available at the NCBI Short Read Archive (accession no. pending) and produced at the Molecular Ecology and Zoology group of the University of Florence. 

The workflow was developed for the analysis of environmental DNA metabarcoding NGS data from Illumina platform. It performs step-by-step analysis of metabarcoding data using a custome reference database, created with CRABS software. It relies on Barque pipeline for data analysis, LULU filtering for error reduction and microDecon for decontamination. The goal of this repository is to simplify the coordinated use of these tools and make the analyses more reproducible.

## Table of contents
1. Introduction
2. Reference database creation with CRABS
3. eDNA metabarcoding analysis
5. Error reduction
6. Decontamination

## Introduction
We used a multi-marker approach with Vert01 (Riaz et al., 2011) and Tele02 (Taberlet et al., 2018) 12S markers. The following workflow highlights the steps used during the analysis of the Vert01 dataset. We slightly changed parameters when working with Tele02, according to the marker's characteristics. 

The following figure summarize the workflow:
![Image of the workflow]

Follow the instructions on the official documentation to install 
- CRABS (https://github.com/gjeunen/reference_database_creator)
- Barque (https://github.com/enormandeau/barque)
- LULU (https://github.com/tobiasgf/lulu)
- microDecon (https://github.com/donaldtmcknight/microDecon)
and their dependencies.

## Reference database creation with CRABS
For more details on CRABS, see the original documentation here https://github.com/gjeunen/reference_database_creator.

1. Database - vertebrate mitochondrial 12S rRNA sequences from NCBI and BOLD - and taxonomy download. 

```
#NCBI database - splitted download
./crabs db_download --source ncbi --database nucleotide --query '12S[All Fields] OR "small subunit ribosomal RNA"[All Fields] AND "Actinopterygii"[Organism]' --output ncbi_actinopterygii_12svert.fasta --keep_original no --email @user_email --batchsize 5000
./crabs db_download --source ncbi --database nucleotide --query '12S[All Fields] OR "small subunit ribosomal RNA"[All Fields] AND "Amphibia"[Organism]' --output ncbi_amphibia_12svert.fasta --keep_original no --email @user_email --batchsize 5000
./crabs db_download --source ncbi --database nucleotide --query '12S[All Fields] OR "small subunit ribosomal RNA"[All Fields] AND "Cyclostomata"[Organism]' --output ncbi_cyclostomata_12svert.fasta --keep_original no --email @user_email --batchsize 5000
./crabs db_download --source ncbi --database nucleotide --query '12S[All Fields] OR "small subunit ribosomal RNA"[All Fields] AND "Lepidosauria"[Organism]' --output ncbi_lepidosauria_12svert.fasta --keep_original no --email @user_email --batchsize 5000
./crabs db_download --source ncbi --database nucleotide --query '12S[All Fields] OR "small subunit ribosomal RNA"[All Fields] AND "Archelosauria"[Organism]' --output ncbi_archelosauria_12svert.fasta --keep_original no --email @user_email --batchsize 5000
./crabs db_download --source ncbi --database nucleotide --query '12S[All Fields] OR "small subunit ribosomal RNA"[All Fields] AND "Mammalia"[Organism]' --output ncbi_mammalia_12svert.fasta --keep_original no --email @user_email --batchsize 5000

#BOLD database  - BOLD sequences containing gaps are by default discarded
./crabs db_download --source bold --database 'Actinopterygii|Amphibia|Aves|Cephalaspidomorphi|Mammalia|Reptilia' --output bold_12svert.fasta --keep_original no --boldgap DISCARD --marker '12S'

#Taxonomy file
./crabs db_download --source taxonomy
```

2. Merge into one single database

```
#Merge the databases
./crabs db_merge --output merged_db.fasta --uniq yes --input ncbi_actinopterygii_12svert.fasta ncbi_amphibia_12svert.fasta ncbi_cyclostomata_12svert.fasta ncbi_lepidosauria_12svert.fasta ncbi_archelosauria_12svert.fasta ncbi_mammalia_12svert.fasta bold_12svert.fasta
```

3. In silico pcr

```
#In silico pcr
./crabs insilico_pcr --input merged_db.fasta --output 01-vert01_insilico-pcr.fasta --fwd TTAGATACCCCACTATGC --rev TAGAACAGGCTCCTCTAG --error 2
```

Reference databases created with CRABS must be converted into a Barque-friendly format (header: >Family_Genus_Species). We can do it at this point, using the idt2barque.py script. 

## eDNA metabarcoding analysis with Barque
Before starting to use Barque, please read the official documentation here https://github.com/enormandeau/barque?tab=readme-ov-file#description.

#### Data requirement
- Input Fastq files.
  The dataset used for this study contained forward and reverse reads from two 12S mitochondrial gene fragments of vertebrates and teleost species. Raw sequence reads were demultiplexed with bcl2fastq version 2.20 (Illumina) and FastQC was used to check read quality.
- Reference database. Reference databases created with CRABS must be converted into a Barque-friendly format (header: >Family_Genus_Species).

To work with OTUs, two runs for each marker dataset must be performed. The first one is used to refine the database and generate denoised OTUs, along with their taxonomic assignment. In the second one, the OTUs and their taxonomic assignment are used as a database themselves to find read counts per sample.

### Reference database conversion
Transform the reference database to the Barque format

```
  import sys
  import re

  def clean_records(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            # Split the line into columns
            columns = line.strip().split('\t')

             # Step 1: Remove records with 'cf.' or 'aff.' in column 9
            if 'cf.' in columns[8] or 'aff.' in columns[8]:
                continue

            # Step 2: Remove any character after 'sp.' in column 9
            if 'sp.' in columns[8]:
              columns[8] = columns[8].split('sp.')[0] + 'sp.'

            # Step 3: If column 9 contains '_x_', substitute '_x_' with '-x-'
            if '_x_' in columns[8]:
                columns[8] = columns[8].replace('_x_', '-x-')

            # Write the line on the new file
            outfile.write('\t'.join(columns) + '\n')

  if __name__ == "__main__":
    # Check that two arguments have been provided from the command line
    if len(sys.argv) != 3:
        print("Error! The right usage is: python3 dbrefinement.py input_file output_file")
        sys.exit(1)
```

### Runs settings
Download two Barque repositories, one for each run. We will call them "01_ASVs-OTUs_creation" and "02_OTUs_annotation". Then copy the reference database and the raw data into the 01_ASVs-OTUs_creation/03_database and 01_ASVs-OTUs_creation/04_data folders, respectively. All file names must end with .fastq.gz. 

### Barque analysis
Launch the first run using
```
./barque 02_info/barque_config.sh
```
To enhance accuracy in the taxonomic assignment and minimize erroneous sequence assignation, use the files stored in 01_ASVs-OTUs_creation/12_results to create a list of 'unwanted species', which can be non-target or non-present species in the study area. Specifically, you can use the files "marker_species_table" and "marker_multiple_hit_infos", and the sub-folder "01_multihits" to understand which 'unwanted species' resulted from the analysis. Copy their header into a txt file.

Use your unwanted species list to refine the reference database, removing their sequences.

Then re-run the pipeline using the refined database. 



## Error reduction with LULU filtering
For more details on LULU, see the original documentation here https://github.com/tobiasgf/lulu.

## Decontamination with microDecon
For more details on microDecon, see the original documentation here https://github.com/donaldtmcknight/microDecon.


