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

### 1. Database - vertebrate mitochondrial 12S rRNA sequences from NCBI and BOLD - and taxonomy download. 

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

### 2. Merging into one single database

```
./crabs db_merge --output merged_db.fasta --uniq yes --input ncbi_actinopterygii_12svert.fasta ncbi_amphibia_12svert.fasta ncbi_cyclostomata_12svert.fasta ncbi_lepidosauria_12svert.fasta ncbi_archelosauria_12svert.fasta ncbi_mammalia_12svert.fasta bold_12svert.fasta
```

### 3. In silico pcr

```
./crabs insilico_pcr --input merged_db.fasta --output 01-vert01_insilico-pcr.fasta --fwd TTAGATACCCCACTATGC --rev TAGAACAGGCTCCTCTAG --error 2
```

<details>
<summary> OverFlow Error: FASTA/FASTQ does not fit into buffer </summary>

If the database download is not filtered by length and thus contains whole genome sequences, this error appears during in silico pcr. It is overcome by adding the buffer size parameter (see https://github.com/marcelm/cutadapt/issues/462) on lines 266 and 294 of the crabs original script. We applied ```--buffer-size=4000000000```.

</details>

A small % of large and out-of-target amplicons can be generated during the in silico pcr. Although probably containing our fragment of interest, these sequences have to be filtered out because they can introduce errors during the pga. We did it using the ```length-fultering.py``` script, as follows:
```
python3 length-filtering.py input --max_length 150
```
It will generate two files, one containing the discarded sequences and the second containing the accepted ones and used in the following steps. 

### 4. Pairwise global alignment

```
./crabs pga --input merged_db.fasta --output 02-vert01_pga.fasta --database 01-vert01_insilico-pcr.fasta --fwd TTAGATACCCCACTATGC --rev TAGAACAGGCTCCTCTAG --speed medium --percid 0.90 --coverage 0.90 --filter_method strict
```

### 5. Taxonomy assignment

```
./crabs assign_tax --input 02-vert01_pga.fasta --output 03-vert01_taxonomy.tsv --acc2tax nucl_gb.accession2taxid --taxid nodes.dmp --name names.dmp --missing 03-vert01_missing_taxa.tsv
```

### 6. Database curation
We removed records marked with "cf." or "aff." or "sp." - which are doubtful about the real taxonomy of the sequences - and curated hybrids records using the script ```dbrefinement_strict.py```.

### 7. Dereplication
```
./crabs dereplicate --input 04-vert01_taxonomy-curated.tsv --output 05-vert01_dereplicated.tsv --method uniq_species
```

### 8. Cleanup
```
./crabs seq_cleanup --input 05-vert01_dereplicated.tsv --output 06-vert01_cleaned.tsv --minlen 30 --maxlen 150 --maxns 2 --enviro yes --species yes --nans 2
```

### 9. Fasta conversion
```
./crabs tax_format --input 06-vert01_cleaned.tsv --output 07-vert01_idt.fasta --format idt
```

### 10. Conversion into a barque-friendly fasta format
Reference databases created with CRABS must be converted into a Barque-friendly format (header: >Family_Genus_Species). We can do it at this point, using the ```idt2barque.py``` script. 

## eDNA metabarcoding analysis with Barque
Before starting to use Barque, please read the official documentation here https://github.com/enormandeau/barque?tab=readme-ov-file#description.

#### Data requirement
- Input Fastq files.
  The dataset used for this study contained forward and reverse reads from two 12S mitochondrial gene fragments of vertebrates and teleost species. Raw sequence reads were demultiplexed with bcl2fastq version 2.20 (Illumina) and FastQC was used to check read quality.
- Reference database converted into a Barque-friendly format

To work with OTUs, two runs for each marker dataset must be performed. The first one is used to refine the database and generate denoised OTUs, along with their taxonomic assignment. In the second one, the OTUs and their taxonomic assignment are used as a database themselves to find read counts per sample.

### Runs settings
We downloaded two Barque repositories, one for each run, and called them "01_ASVs-OTUs_creation" and "02_OTUs_annotation". We then copied the reference database and the raw data into the 01_ASVs-OTUs_creation/03_database and 01_ASVs-OTUs_creation/04_data folders, respectively. 

### First run
We launched the first run with the following parameters:


To enhance accuracy in the taxonomic assignment and minimize erroneous sequence assignation, we then used the files stored in 01_ASVs-OTUs_creation/12_results to create a list of 'unwanted species' - non-target or non-present species in the study area. Specifically, we used the files "marker_species_table" and "marker_multiple_hit_infos", and the sub-folder "01_multihits" to understand which 'unwanted species' resulted from the analysis. Copy their header into a txt file named "unwanted_species.txt".

Use your unwanted species list to refine the reference database, removing their sequences.

Then re-run the pipeline using the refined database. 



## Error reduction with LULU filtering
For more details on LULU, see the original documentation here https://github.com/tobiasgf/lulu.

## Decontamination with microDecon
For more details on microDecon, see the original documentation here https://github.com/donaldtmcknight/microDecon.


