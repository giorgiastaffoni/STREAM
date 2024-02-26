# eDNA_workflow
This repo corresponds to the bioinformatics steps of the following article:
"Comparison of environmental DNA metabarcoding and electrofishing to assess freshwater fish biodiversity in northwestern Italy" (Ballini & Staffoni, submitted to Hydrobiologia)
based on the datasets available at (), produced at the () group of the University of Florence. 

The workflow was developed for the analysis of environmental DNA metabarcoding NGS data from Illumina platform. It performs step-by-step analysis of metabarcoding data using a custom reference database, created with CRABS software. It relies on Barque pipeline for data analysis, LULU filtering for post-clustering curation and microDecon for decontamination. The goal of this repository is to simplify the coordinated use of these tools and make the analyses more reproducible.

## Table of contents
1. Introduction
2. Reference database creation with CRABS
3. eDNA metabarcoding analysis
5. Error reduction
6. Decontamination

## Introduction
We applied a multi-marker approach with Vert01 and Tele02 12S markers. 

The following figure summarizes the workflow:
![Image of the workflow]

The following workflow highlights the steps used during the analysis of the Vert01 dataset. We slightly changed parameters when working with Tele02, according to the marker's characteristics. 

## Reference database creation with CRABS

For more details on CRABS, see the original documentation here https://github.com/gjeunen/reference_database_creator.

```
#NCBI database download 
crabs db_download --source ncbi --database nucleotide --query '12S[All Fields] OR "small subunit ribosomal RNA"[All Fields] AND ("Vertebrata"[Organism] OR vertebrates[All Fields])' --output 12S_vertebrata_ncbi.fasta --keep_original no --email @youremail --batchsize 5000

#BOLD database download (BOLD sequences containing gaps are by default discarded)
crabs db_download --source bold --database 'Actinopterygii|Amphibia|Aves|Elasmobranchii|Reptilia|Sarcopterygii' --output 12S_vertebrates_bold.fasta --keep_original no --boldgap DISCARD --marker '12S'

#Taxonomy file download
crabs db_download --source taxonomy

#Merge the databases
crabs db_merge --output merged_db.fasta --uniq yes --input 12S_vertebrata_ncbi.fasta 12S_vertebrates_bold.fasta

#In silico pcr, default settings  
crabs insilico_pcr --input merged_db.fasta --output output_pcr.fasta --fwd TTAGATACCCCACTATGC --rev TAGAACAGGCTCCTCTAG --error 4.5

#Pga (Pairwise Global Alignment)
crabs pga --input merged_db.fasta --output output_pga.fasta --database output_pcr.fasta --fwd TTAGATACCCCACTATGC --rev TAGAACAGGCTCCTCTAG --speed slow --percid 0.90 --coverage 0.90 --filter_method relaxed

#Assign_tax
crabs assign_tax --input output_pga.fasta --output database_with_taxonomy.tsv --acc2tax nucl_gb.accession2taxid --taxid nodes.dmp --name names.dmp --missing missing_taxa.tsv
```
Reference databases created with CRABS must be converted into a Barque-friendly format (header: >Family_Genus_Species). We can do it at this point, using the idt2barque.py script. Then we can go on with dereplication.

```
#Dereplicate
crabs dereplicate --input database_with_refined_taxonomy.tsv --output dereplicated_vert01.tsv --method uniq_species

#Seq_cleanup - we did not use maxlen and maxns restrictions
crabs seq_cleanup --input dereplicated_vert01.tsv --output cleaned_vert01.tsv --minlen 30 --maxlen 1000000000 --maxns 1000000000 --enviro no --species no --nans 2

#Conversion into idt fasta
crabs tax_format --input cleaned_vert01.tsv --output final_vert01.fasta --format idt
```
Reference databases created with CRABS must be converted into a Barque-friendly format (header: >Family_Genus_Species). We can do it using the idt2barque.py script. 
```
python3 idt2barque.py
```

## eDNA metabarcoding analysis with Barque
Before starting to use Barque, please read the official documentation here https://github.com/enormandeau/barque?tab=readme-ov-file#description.
To work with OTUs, two runs for each marker dataset must be performed. The first one is used to refine the database and generate denoised OTUs, along with their taxonomic assignment. In the second one, the OTUs and their taxonomic assignment are used as a database themselves to find read counts per sample.

#### Data requirement
- Input Fastq files.
  The dataset used for this study contained forward and reverse reads from two 12S mitochondrial gene fragments of vertebrates and teleost species. Raw sequence reads were demultiplexed with bcl2fastq version 2.20 (Illumina) and FastQC was used to check read quality.
- Reference databaset.
 
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

### First run
Download the Barque repositories. We will call it "01_ASVs-OTUs_creation". Enter the 02_info folder and modify the "barque_config.sh" and "primers.csv" files according to the marker characteristics and the assignment aims. We used the following parameters for the config file:
```
barque cofig file with parameters
```

Then copy the reference database and the raw data into the 03_database and 04_data folders, respectively. All file names must end with .fastq.gz. 

Now you can launch the first run using
```
./barque 02_info/barque_config.sh
```

To enhance accuracy in the taxonomic assignment and minimize erroneous sequence assignation, use the files stored in 01_ASVs-OTUs_creation/12_results to create a list of 'unwanted species', which can be non-target or non-present species in the study area. Specifically, you can use the files "marker_species_table" and "marker_multiple_hit_infos", and the sub-folder "01_multihits" to understand which 'unwanted species' resulted from the analysis. Copy their header into a txt file. Use this list along with the script ---- to refine - removing their sequences - your reference database in the 03_database folder. Then re-run the pipeline with the same parameters but the depleted database. 

## Second run
Download a second Barque repositories. We will call it "02_OTUs_annotation". Keep the "barque_config.sh" and "primers.csv" files as in the first run (except for skip_otu: 1). In the “03_database” folder, copy the “markers.otus.database.fasta” file from the 13_otu_database folder of the first run, and add the original data to the “04_data” folder. Launch the pipeline
```
./barque 02_info/barque_config.sh
```
The final results will be stored in the 12_results folder. Unassigned OTUs at the species level collected into the “most_frequent_non_annotated_sequences” file can be subjected to a separate BLAST search against the complete NCBI nucleotide (nt) database. In our case, no OTUs had matches with species of interest. 

## Error reduction with LULU filtering
For more details on LULU, see the original documentation here https://github.com/tobiasgf/lulu.

## Decontamination with microDecon
For more details on microDecon, see the original documentation here https://github.com/donaldtmcknight/microDecon.


