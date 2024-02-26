# eDNA_workflow
This repo correspond to the bioinformatics steps of the following article:
"Comparison of environmental DNA metabarcoding and electrofishing to assess freshwater fish biodiversity in northwestern Italy" (Ballini & Staffoni, submitted to Hydrobiologia)
based on the datasets available at () and produced at the () group of the University of Florence. 

The workflow was developed for the analysis of environmental DNA metabarcoding NGS data from Illumina platform. It performs step-by-step analysis of metabarcoding data using a custome reference database, created with CRABS software. It relies on Barque pipeline for data analysis, LULU filtering for error reduction and microDecon for decontamination. The goal of this repository is to simplify the coordinated use of these four tools and make the analyses more reproducible.

## Table of contents
1. Introduction
2. Reference database creation with CRABS
3. eDNA metabarcoding analysis
4. Error reduction
5. Decontamination

## Reference database creation with CRABS
For more details on CRABS, see the original 
