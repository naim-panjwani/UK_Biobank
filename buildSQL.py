import os
import pandas as pd
import numpy as np
import re
import urllib.request
import subprocess
import sqlalchemy as sa
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect
import pymysql
pymysql.install_as_MySQLdb()
# import dropbox
# import wget
# import spacy

def download(url, filename):
    u = urllib.request.urlopen(url)
    data = u.read()
    u.close()

    with open(filename, "wb") as f: 
        f.write(data)

ukbb_manifest_file = os.path.join(".", "UKBB GWAS Imputed v3 - File Manifest Release 20180731 - Manifest 201807.tsv")
ukbb_manifest_df = pd.read_csv(ukbb_manifest_file, sep='\t', encoding='utf-8')
ukbb_manifest_df = ukbb_manifest_df.dropna()
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
                        # wget_commands.append(ukbb_manifest_df[['wget command']].iloc[i,0])
                        pheno_descriptions.append(ukbb_manifest_df[['Phenotype Description']].iloc[i,0])
                        sex.append(ukbb_manifest_df[['Sex']].iloc[i,0])
                        filenames.append(ukbb_manifest_df[['File']].iloc[i,0])
download_urls = [url.replace('dl=0','dl=1') for url in download_urls]

# Make downloads folder and download required files:
if not os.path.exists(os.path.join(os.getcwd(),"downloads")):
        print("Creating downloads directory")
        os.makedirs(os.path.join(os.getcwd(),"downloads"))

os.chdir(os.path.join(os.getcwd(),"downloads"))
for i in np.arange(len(download_urls)):
        url = download_urls[i]
        filename = filenames[i]
        if not os.path.isfile(filename):
                print("Downloading file " + str(i+1) + " of " + str(len(download_urls)) + ": " + filename)
                download(url, filename)
        else:
                print(filename + " exists")


# Load into a MySQL database in chunks:
engine = sa.create_engine('mysql://root:root@localhost/uk_biobank')
# inspector = inspect(engine)
# tables = inspector.get_table_names()
# columns = inspector.get_columns(tables[0])
# for column in columns:
#     print(column["name"], column["type"])

# chunks = pd.read_csv(filename, compression='gzip', sep='\t', nrows=100000)
for filename in filenames:
        chunks = pd.read_csv(filename, compression='gzip', sep='\t', chunksize=100000)
        for chunk in chunks:
                chunk.to_sql(name=filename, if_exists='append', con=engine)
        conn = engine.connect()
        query = f'SELECT *, substring_index(SUBSTRING_INDEX(`variant`, ":", 1), ":", -1) as chr, substring_index(SUBSTRING_INDEX(`variant`, ":", 2), ":", -1) as pos FROM `uk_biobank`.`{filename}`;'
        # query = f"SELECT variant FROM {filename}"
        newdb = pd.read_sql(query, conn)
