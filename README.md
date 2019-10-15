# README by Rohan Maddamsetti (rmaddams _AT_ ODU _DOT_ edu)
### Last edited on 10/12/2019.

IMPORTANT CAVEAT: the code here was written and tested on a Mac running Mac OS 10.13, and genomes were resequenced using breseq 0.33.2 on a cluster running Linux. You may have to lightly edit source files to get them working on your machine.

# How to run the analyses for the manuscript 'Genomic and phenotypic evolution of Escherichia coli in a citrate-only resource environment'.

I expect that users will be running these scripts within the 'src' directory of this project.
So, using the Terminal on Mac/Linux, run this command:
'cd DM0-evolution/src' before running these scripts.

## Generating the Last Common Ancestor as a reference for mutation calling.
First, we need to generate the Last Common Ancestor (LCA) for the strains studied in this project.
We use the LCA as the reference strain for mutation calling.

The LCA is generated by taking the intersection of mutations in CZB152 and CZB154. I took the curated
genome diff (*.gd) files for CZB152 and CZB154 that Jeff Barrick has made available on github at
https://github.com/barricklab/LTEE-Ecoli. These curated files are missing a SNP
that is found in every single one of the genomes analyzed in this project. Therefore, I added this mutation
(in clpA-serW-mut.gd) to the LCA. In addition to generating the LCA, I also generate a genome diff of the LTEE 50K
Cit+ clone REL11364 that has all mutations in CZB154 subtracted out. CZB154 is a direct ancestor of the 50K clone,
so this file contains all additional mutations on this line of descent. 

To do this work, run the shell script generate-LCA.sh like so:
'bash generate-LCA.sh'.  

## Calling mutations with breseq.
Second, we need to run Jeff Barrick's breseq pipeline (github.com/barricklab/breseq) to call mutations,
using the LCA of all strains as a reference genome.

To do this work, I wrote a shell script to run breseq on all Illumina data for the genomes on the local high-performance
computing cluster (HPC).

Run this script like so, on your computer cluster. You have to have breseq installed, and you will have to update the pathnames
for the data as appropriate. Note that we use slurm as the job scheduler.

'bash submit-slurm-job.sh'

Then, download the breseq results to your computer for further analysis.

## Running preparatory scripts before analysis.

The following python scripts are used to set up directory structures, run utility programs, munge data, and so forth before doing the data analysis.

NOTA BENE: these scripts involve system calls and path and directory manipulations. While I have made some attempt at portability, they may not work
     	   out of the box in untested environments (like Windows). You may have to modify source code to get things working.

Run the follow scripts as follows, from the 'src' directory:

'python deal-with-gdiffs.py'
'python prep-growth-data.py'
'python run-kallisto.py'

## Running analysis scripts.

Run the following python scripts as follows, from the 'src' directory.

'python grep-maeA-citT-polymorphism.py > ../results/maeA-citT-polymorphism.csv'

This will print a table of all variants in maeA, citT, and dctA throughout the experiment.
In particular, I use this to look for polymorphism due to copy number variation in these genes.

To compare genome environment across environments and calculate related statistics, run the following:

'python dice-analysis.py'

dice-analysis.py controls the arguments being passed to citrate_dice.py, which does all the actual analysis and statistics.
citrate_dice.py is a fork of Daniel Deatherage's TEE.py; see supplement to Deatherage et al. (2017) in PNAS for original source code.  

To do the FBA analysis, run the following jupyter notebook (using a python 3 kernel):  

'jupyter notebook FBA-analysis.ipynb'.  

The R analysis scripts should be run interactively in your favorite R environment. I use Emacs Speaks Statistics (ESS) to run R within Emacs, but you may prefer RStudio or something else.  

Nkrumah wrote CellDeath.v09.R to analyze his cell death experiment.
Rohan made modifications, mainly to use bias-corrected and accelerated bootstrap confidence intervals, weighted by the number of cells per sample in the analyzed micrographs.  

copy-number-analysis.R examines the sequencing coverage distributions output
by breseq, and tests positions over the chromosome for significantly elevated overage indicative of copy number variation/gene amplification. Statistical tests are carried out on positions that are further apart than the maximum sequencing read length, in order to carry out independent statistical tests and reduce the number of statistical tests (by reducing the correction for multiple testing I increase statistical power).  

make-figures.R depends on output from copy-number-analysis.R as well as
dice-analysis.py (and therefore citrate_dice.py).  

For this reason, run make-figures.R interactively after all other programs have
been run.
