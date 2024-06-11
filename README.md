 # STREAM

This repo represents the workflow used in the following paper: <br />
"Comparison of environmental DNA metabarcoding and electrofishing in freshwater systems of northwestern Italy" (Ballini & Staffoni, submitted to Hydrobiologia)<br />
based on the datasets available at the NCBI Short Read Archive (accession no. pending) and produced at the Molecular Ecology and Zoology group of the University of Florence. 

The workflow was developed for the analysis of environmental DNA metabarcoding NGS data from Illumina platform. It performs step-by-step analysis of metabarcoding data using a custome reference database, created with CRABS software. It relies on Barque pipeline for data analysis, LULU filtering for error reduction and microDecon for decontamination. The goal of this repository is to simplify the coordinated use of these tools and make the analyses more reproducible.

## Table of contents
I. Introduction <br />
II. Reference database creation with CRABS <br />
III. eDNA metabarcoding analysis <br />
IV. Error reduction <br />
V. Decontamination <br />
VI. Final curation <br />

## I. Introduction
We used a multi-marker approach with Vert01 (Riaz et al., 2011) and Tele02 (Taberlet et al., 2018) 12S markers. The following workflow highlights the steps used during the analysis of the Vert01 dataset. We slightly changed parameters when working with Tele02, according to the marker's characteristics. 

The following figure summarize the workflow:<br />
![Image of the workflow]

Follow the instructions on the official documentation to install 
- CRABS (https://github.com/gjeunen/reference_database_creator)
- Barque (https://github.com/enormandeau/barque)
- LULU (https://github.com/tobiasgf/lulu)
- microDecon (https://github.com/donaldtmcknight/microDecon)
and their dependencies.

## Reference database creation with CRABS
For more details on CRABS, see the original documentation here https://github.com/gjeunen/reference_database_creator.

#### 1. Database - vertebrate mitochondrial 12S rRNA sequences from NCBI and BOLD - and taxonomy download. 

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

#### 2. Merging into one single database

```
./crabs db_merge --output merged_db.fasta --uniq yes --input ncbi_actinopterygii_12svert.fasta ncbi_amphibia_12svert.fasta ncbi_cyclostomata_12svert.fasta ncbi_lepidosauria_12svert.fasta ncbi_archelosauria_12svert.fasta ncbi_mammalia_12svert.fasta bold_12svert.fasta
```

#### 3. In silico pcr

```
./crabs insilico_pcr --input merged_db.fasta --output 01-vert01_insilico-pcr.fasta --fwd TTAGATACCCCACTATGC --rev TAGAACAGGCTCCTCTAG --error 2
```

<details>
<summary> OverFlow Error: FASTA/FASTQ does not fit into buffer </summary>

If the database download is not filtered by length and thus contains whole genome sequences, this error appears during in silico pcr. It is overcome by adding the buffer size parameter (see https://github.com/marcelm/cutadapt/issues/462) on lines 266 and 294 of the crabs original script. We applied ```--buffer-size=4000000000```.

</details>

A small % of large and out-of-target amplicons can be generated during the in silico pcr. Although probably containing our fragment of interest, these sequences have to be filtered out because they can introduce errors during the pga. We did it using the ```length-fultering.py``` script, as follows:
```
python3 length-filtering.py input_file --max_length 150
```
It will generate two files, one containing the discarded sequences and the second containing the accepted ones and used in the following steps. 

#### 4. Pairwise global alignment

```
./crabs pga --input merged_db.fasta --output 02-vert01_pga.fasta --database 01-vert01_insilico-pcr.fasta --fwd TTAGATACCCCACTATGC --rev TAGAACAGGCTCCTCTAG --speed medium --percid 0.90 --coverage 0.90 --filter_method strict
```

#### 5. Taxonomy assignment

```
./crabs assign_tax --input 02-vert01_pga.fasta --output 03-vert01_taxonomy.tsv --acc2tax nucl_gb.accession2taxid --taxid nodes.dmp --name names.dmp --missing 03-vert01_missing_taxa.tsv
```

#### 6. Database curation
We removed records marked with "cf." or "aff." or "sp." - which are doubtful about the real taxonomy of the sequences - and curated hybrids records using the script ```dbrefinement_strict.py```.
```
python3 dbrefinement_strict.py input_file output_file
```

#### 7. Dereplication
```
./crabs dereplicate --input 04-vert01_taxonomy-curated.tsv --output 05-vert01_dereplicated.tsv --method uniq_species
```

#### 8. Cleanup
```
./crabs seq_cleanup --input 05-vert01_dereplicated.tsv --output 06-vert01_cleaned.tsv --minlen 30 --maxlen 150 --maxns 2 --enviro yes --species yes --nans 2
```

#### 9. Fasta conversion
```
./crabs tax_format --input 06-vert01_cleaned.tsv --output 07-vert01_idt.fasta --format idt
```

#### 10. Conversion into a barque-friendly fasta format
Reference databases created with CRABS must be converted into a Barque-friendly format (header: >Family_Genus_Species). We used the ```idt2barque.py``` script. 
```
python3 idt2barque.py input_file output_file
```

## II. Barque analysis
Before starting to use Barque, please read the official documentation here https://github.com/enormandeau/barque?tab=readme-ov-file#description.

#### Data requirement
- Input Fastq files.
  The dataset used for this study contained forward and reverse reads from two 12S mitochondrial gene fragments of vertebrates and teleost species. Raw sequence reads were demultiplexed with bcl2fastq version 2.20 (Illumina) and FastQC was used to check read quality.
- Reference database converted into a Barque-friendly format

To work with OTUs, two runs must be performed. The first one is used to refine the database and generate denoised OTUs, along with their taxonomic assignment. In the second one, the OTUs and their taxonomic assignment are used as a database themselves to find read counts per sample.

### Runs settings
We downloaded two Barque repositories, one for each run, and called them "01_OTUs_creation" and "02_OTUs_annotation". We then copied the reference database and the raw data into the 01_OTUs_creation/03_database and 01_OTUs_creation/04_data folders, respectively. Then, we set the parameters in 01_OTUs_creation/02_info/barque_config.sh and 01_OTUs_creation/02_info/primers.csv as follows:
- 01_OTUs_creation/02_info/barque_config.sh
```
#!/bin/bash

# Modify the following parameter values according to your experiment
# Do not modify the parameter names or remove parameters
# Do not add spaces around the equal (=) sign
# It is a good idea to try to run Barque with different parameters 

# Global parameters
NCPUS=40                    # Number of CPUs to use. A lot of the steps are parallelized (int, 1+)
PRIMER_FILE="02_info/primers.csv" # File with PCR primers information

# Skip data preparation and rerun only from vsearchp
SKIP_DATA_PREP=0            # 1 to skip data preparation steps, 0 to run full pipeline (recommended)

# Filtering with Trimmomatic
CROP_LENGTH=152             # Cut reads to this length after filtering. Just under amplicon length

# Merging reads with flash
MIN_OVERLAP=30              # Minimum number of overlapping nucleotides to merge reads (int, 1+)
MAX_OVERLAP=280             # Maximum number of overlapping nucleotides to merge reads (int, 1+)

# Extracting barcodes
MAX_PRIMER_DIFF=4           # Maximum number of differences allowed between primer and sequence (int, 0+)

# Running or skipping chimera detection
SKIP_CHIMERA_DETECTION=0    # 0 to search for chimeras (RECOMMENDED), 1 to skip chimera detection
                            #   or use already created chimera cleaned files

# vsearch
MAX_ACCEPTS=20              # Accept at most this number of sequences before stoping search (int, 1+)
MAX_REJECTS=20              # Reject at most this number of sequences before stoping search (int, 1+)
QUERY_COV=0.9               # At least that proportion of the sequence must match the database (float, 0-1)
MIN_HIT_LENGTH=36          # Minimum vsearch hit length to keep in results (int, 1+)

# Filters
MIN_HITS_SAMPLE=10           # Minimum number of hits in at least one sample  to keep in results (int, 1+)
MIN_HITS_EXPERIMENT=10       # Minimum number of hits in whole experiment to keep in results (int, 1+)

# Non-annotated reads
NUM_NON_ANNOTATED_SEQ=200   # Number of unique most-frequent non-annotated reads to keep (int, 1+)

# OTUs
SKIP_OTUS=0                 # 1 to skip OTU creation, 0 to use it
MIN_SIZE_FOR_OTU=10          # Only unique reads with at least this coverage will be used for OTUs
```

- 01_OTUs_creation/02_info/primers.csv

| PrimerName  |     ForwardSeq     |    ReverseSeq      | MinAmpliconSize | MaxAmpliconSize  | DatabaseName | SimilSpecies  | SimilGenus | SimilPhylum  |
| ----------- | ------------------ | ------------------ | --------------- | ---------------- | ------------ | ------------- | ---------- | ------------ |							
|   vert01    | TTAGATACCCCACTATGC	| TAGAACAGGCTCCTCTAG |	       56	      |       132	       | vert01_mar24	|      0.98	    |    0.95	   |      0.9     |


### First run
We launched the first run and obtained the results for the ASVs - stored in 12_results - and the OTU database - stored in 13_otu_database. To enhance accuracy in the taxonomic assignment and minimize erroneous sequence assignation, we then used the files stored in 12_results to create a list of 'unwanted species' - non-target or non-present species in the study area. We used this list - under the form of .txt file - to refine our reference database, removing the sequences of the unwanted species with the script ```remove_species.py```.
```
python3 remove_species.py input_file unwanted_species.txt
```
We finally re-run the pipeline using the refined database. 

### Second run
For the second run the 01_OTUs_creation/13_otu_database/vert01.otus.database.fasta.gz file from the first one was copied into the 02_OTUs_annotation/03_database folder and used as database. The “barque_config” and “primers” files were kept with the same parameters as in the first run, except for skip_otu = 1. 

### Most frequent non annotated sequences
Sequences that are frequent in the samples but were not annotated by the pipeline can be checked on NCBI using blast. We only blasted sequences found more than 10 times. No target species were identified. 

## III. Error reduction with LULU filtering
For more details on LULU, see the original documentation here https://github.com/tobiasgf/lulu.

We used as
- OTU_table -> the file 02_OTUs_annotation/12_results/vert01_species_table.csv, which was formatted as requested by LULU 
- OTU_sequences -> the file 01_OTUs_creation/13_otu_database/vert01.otus.database.fasta.gz with modified headers - see ```headers_lulu.py``` script.

We then created the match_list with vsearch
```
vsearch --usearch_global OTU_sequences.fasta --db OTU_sequences.fasta --self --id .84 --iddef 1 --userout match_list.txt -userfields query+target+id --maxaccepts 0 --query_cov .9 --maxhits 10
```

As LULU was developed for ITS marker and the 12S barcode region presents lower variability, we raised the min_seq_similarity parameter to 87. The other default parameters were kept unchanged. 
```
curated_result_mm87 <- lulu(otutab, matchlist, minimum_ratio_type = "min", minimum_ratio = 1, minimum_match = 87, minimum_relative_cooccurence = 0.95)
```

In the resulting curated table, OTUs assigned to the same taxon were finally merged and their reads were summed, using the aggregate function in R. OTUs with multi-hits were manually assigned to OTUs with the same taxonomic assignment selected by LULU.

## IV. Decontamination with microDecon
For more details on microDecon, see the original documentation here https://github.com/donaldtmcknight/microDecon.

We converted our manually curated table from LULU into the format requested by microDecon. Default options were applied. 
```
decontaminated_default <- decon(data = microDecon_table, numb.blanks = 7, numb.ind = c(6,6,6,6,6,6,1), taxa = T)
```

## V. Final curation 
The replicates from the same site were then summed to obtain a single site-specific taxonomic list. Non-target species (humans and livestock) and possible contaminations were discarded. Sequences with unknown species assignments were annotated to the genus and the species was recorded as “sp.”. A threshold of >10 reads was set to declare a species as present in the watercourse.
