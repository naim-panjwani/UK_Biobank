import os
import pandas as pd
import numpy as np
import re
import urllib.request
import subprocess
import dropbox
import wget
# import spacy

ukbb_manifest_file = os.path.join(".", "UKBB GWAS Imputed v3 - File Manifest Release 20180731 - Manifest 201807.tsv")
ukbb_manifest_df = pd.read_csv(ukbb_manifest_file, sep='\t', encoding='utf-8')
ukbb_manifest_df = ukbb_manifest_df.dropna()
re.search("3062_*", "3062_irnt")
phenotype_list = [
        "3062"
        ,"3063"
        ,"3064"
#        ,"20150"
#        ,"20153"
#        ,"20154"
#        ,"20002_1115"
#        ,"22127"
#        ,"22128"
#        ,"22129"
#        ,"22130"
#        ,"22133"
#        ,"22134"
#        ,"22135"
#        ,"22137"
#        ,"22502"
#        ,"22504"
        ]

# Get the download URLs:
download_urls = []
wget_commands = []
phenocodes = []
pheno_descriptions = []
sex = []
filenames = []
for phenotype in phenotype_list:
        search_term = "^" + phenotype + "_*"
        for i in np.arange(ukbb_manifest_df.shape[0]):
                if re.search(search_term, ukbb_manifest_df.iloc[i,0]) and ukbb_manifest_df.iloc[i,:]['Sex'] == "both_sexes":
                        phenocodes.append(ukbb_manifest_df[['Phenotype Code']].iloc[i,0])
                        download_urls.append(ukbb_manifest_df[['Dropbox File']].iloc[i,0])
                        wget_commands.append(ukbb_manifest_df[['wget command']].iloc[i,0])
                        pheno_descriptions.append(ukbb_manifest_df[['Phenotype Description']].iloc[i,0])
                        sex.append(ukbb_manifest_df[['Sex']].iloc[i,0])
                        filenames.append(ukbb_manifest_df[['File']].iloc[i,0])

if not os.path.exists(os.path.join(os.getcwd(),"downloads")):
        print("Creating downloads directory")
        os.makedirs(os.path.join(os.getcwd(),"downloads"))

os.chdir(os.path.join(os.getcwd(),"downloads"))
for i in np.arange(len(download_urls)):
        url = download_urls[i]
        filename = filenames[i]
        print(url)
        print("Downloading file " + str(i+1) + " of " + str(len(download_urls)+1) + ": " + filename)
        wget.download(url)

dropbox.files_download(url)
os.