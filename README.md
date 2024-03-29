# STREAM (Supporting Tool for Research with Environmental dna Approach of Metabarcoding)

STREAM represents the workflow used in the following paper:
"Comparison of environmental DNA metabarcoding and electrofishing to assess freshwater fish biodiversity in northwestern Italy" (Ballini & Staffoni, submitted to Hydrobiologia)
based on the datasets available at () and produced at the () group of the University of Florence. 

The workflow was developed for the analysis of environmental DNA metabarcoding NGS data from Illumina platform. It performs step-by-step analysis of metabarcoding data using a custome reference database, created with CRABS software. It relies on Barque pipeline for data analysis, LULU filtering for error reduction and microDecon for decontamination. The goal of this repository is to simplify the coordinated use of these four tools and make the analyses more reproducible.

## Table of contents
1. Introduction
2. Reference database creation with CRABS
3. eDNA metabarcoding analysis
5. Error reduction
6. Decontamination

## Introduction
We used a multi-marker approach with Vert01 and Tele02 12S markers. 

The following figure summarize the workflow:
![Image of the workflow]

Follow the instructions on the official documentation to install CRABS, Barque, LULU and microDecon.


## Reference database creation with CRABS
For more details on CRABS, see the original documentation here https://github.com/gjeunen/reference_database_creator.

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


