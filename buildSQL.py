import os
import pandas as pd
import re

ukbb_manifest_file = os.path.join(".", "UKBB GWAS Imputed v3 - File Manifest Release 20180731 - Manifest 201807.tsv")
ukbb_manifest_df = pd.read_csv(ukbb_manifest_file, sep='\t', encoding='utf-8')
re.search("3062_*", "3062_irnt")
phenotype_list = [
        "3062",
        "3063",
        "3064",
        "20150",
        "20153",
        "20154",
        "20002_1115",
        "22127",
        "22128",
        "22129",
        "22130",
        "22133",
        "22134",
        "22135",
        "22137",
        "22502",
        "22504"
        ]

download_urls = []
def get_url(phenocode):
        search_term = phenocode + "_*"
        allphenocodes_list = list(ukbb_manifest_df['Phenotype Code'])
        
for phenotype in phenotype_list:
        search_term = phenotype + "_*"
        for i in np.arange(ukbb_manifest_df.shape[0]):
                if re.search(search_term, ukbb_manifest_df.iloc[i,0]):
                        download_urls.append(ukbb_manifest_df.iloc[i, ['']])
