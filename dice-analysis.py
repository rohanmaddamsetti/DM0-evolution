'''

dice-analysis.py by Rohan Maddamsetti

1) Generate the input directory structure needed for Dan Deatherage's
TEE.py to run on the Cit+ evolution experiment data.

2) Run TEE.py on the data two ways: DM0 versus DM25, and CZB151 versus CZB152 and CZB154.

It is necessary to have run deal-with-diffs.py before running this program.

Command line used in the TEE analysis:
python TEE.py -n 1000000 -p 150 -dt -s annotated_gd/ -g ../REL606.gbk -e annotated_gd/REL1207.gd -ct 37c

parser = argparse.ArgumentParser(description="Read in gd files, assign mutations to genes, perform statistics where applicable.")
parser.add_argument("-n", "--number", type=int, default=10, help="number of randomizations to perform for statistical models. Set to 0 to skip some tests")
parser.add_argument("-g", "--genbank_ref", help="input genbank file of reference genome, must have blattner numbers as note")
parser.add_argument("-s", "--samples", help="folder containing 'output' folder with gd files to be randomized to detect enrichment")
parser.add_argument("-dt", "--directory_treatments", help="treatment types specified by file architecture", action="store_true")
parser.add_argument("-ct", "--control_treatment", help="specify single treatment to compare all others to for valid and total mutations")
parser.add_argument("--command_line_treatments", help="command line specification of treatments. THIS IS NOT FUNCTIONAL, must specify by directory")
parser.add_argument("-p", "--promoter", type=int, default=0, help="length of promoter to consider as 'valid' mutation default =0")
parser.add_argument("-e", "--excluded_mutations", help="gd file with list of mutations to exclude. Helpful for avoiding using gdtools subtract")
parser.add_argument("--pvalue", type=float, default=0.05, help="p value significance cut off")
parser.add_argument("-pw", "--pairwise", help="perform pairwise dice comparisons among all treatments", action="store_true")
args = parser.parse_args()
'''

from pathlib import Path
from os import makedirs
from os.path import join, expanduser, dirname
from subprocess import run
import pandas as pd

class CallTEE:
    def __init__(self,gd_dir,genbank_ref,mutmatrixfile,control_treatment=''):
        ##self.number = 1000000
        self.number = 10 ## for debugging
        self.promoter_length = 150
        self.genbank_ref = genbank_ref
        self.control_treatment = control_treatment
        self.samples = gd_dir
        self.mutmatrixfile = mutmatrixfile
        self.args = ['python', './external/Deatherage-analysis/DiceSimilarity/citrate_dice.py', '-pw', '-n', str(self.number),
                     '-p', str(self.promoter_length), '-dt', '-s', self.samples, '-g', self.genbank_ref, '-ct', self.control_treatment, '--matrixfile', self.mutmatrixfile]

    def call(self):
        return run(self.args)

    def __str__(self):
        return ' '.join(self.args)

def organize_diffs(analysisdir):
    ''' automatically organize files for the dice analysis.'''

    CZB151_paths = list(Path(join(analysisdir,'CZB151')).rglob("*.gd"))
    CZB152_paths = list(Path(join(analysisdir,'CZB152')).rglob("*.gd"))
    CZB154_paths = list(Path(join(analysisdir,'CZB154')).rglob("*.gd"))

    DM0_paths = [x for x in CZB151_paths+CZB152_paths+CZB154_paths if "DM0" in x.parts]
    DM25_paths = [x for x in CZB151_paths+CZB152_paths+CZB154_paths if "DM25" in x.parts]

    def cp_files(comparisontype,treatment,paths):
        for x in paths:
            y = join(analysisdir, comparisontype, treatment, x.name)
            my_args = ['cp',str(x),y]
            my_cmd = ' '.join(my_args)
            makedirs(dirname(y), exist_ok=True)
            run(my_cmd ,executable='/bin/bash',shell=True)

    cp_files("genotype-comparison","CZB151",CZB151_paths)
    cp_files("genotype-comparison","CZB152",CZB152_paths)
    cp_files("genotype-comparison","CZB154",CZB154_paths)
    cp_files("environment-comparison","DM0",DM0_paths)
    cp_files("environment-comparison","DM25",DM25_paths)    
    
def main():
    homedir = expanduser("~")
    projdir = join(homedir,"BoxSync/DM0-evolution")
    analysis_dir = join(projdir,"results/genome-analysis")

    organize_diffs(analysis_dir)
    
    do_environment = True
    if do_environment:
        gddir = join(analysis_dir,"environment-comparison")
        ctl_treat = 'DM25'
    else: ## No significant difference in targets of selection across parental genotypes.
        gddir = join(analysis_dir,"genotype-comparison")
        ctl_treat = 'CZB151'

    DiceRun = CallTEE(gddir,'../genomes/curated-diffs/LCA.gbk', '../results/DM0-DM25-comparison-mut-matrix.csv', ctl_treat)
    print(DiceRun)
    DiceRun.call()

    ## For comparison, run TEE.py on the LTEE to make a matrix for Fig. 1C.
    ## I do some unnecessary formatting to get TEE.py running at the moment.
    ## I should probably refactor citrate_dice.py so that the mutation matrix code runs separately from the statistics.

    ltee_gddir = join(projdir,"genomes/annotated-LTEE-50K-diffs")
    LTEE_DiceRun = CallTEE(ltee_gddir,'../genomes/REL606.7.gbk','../results/LTEE-mut_matrix.csv','Ara+')
    print(LTEE_DiceRun)
    LTEE_DiceRun.call()

main()
