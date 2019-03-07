######################################################################################
# This script is to initialize the MySQL database for the desired list of phenotypes #
######################################################################################
import os
import pandas as pd
import numpy as np
import re
import urllib.request
import subprocess
import sqlalchemy as sa
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, String
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
#        "3062"
#        ,"3063"
        "3064"
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

# Also download the variants file:
if not os.path.isfile("variants.tsv.bgz"):
        print("Downloading variants.tsv.bgz")
        download("https://www.dropbox.com/s/puxks683vb0omeg/variants.tsv.bgz?dl=1", "variants.tsv.bgz")
else:
        print("variants.tsv.bgz exists")

# Also download the phenotypes file:
if not os.path.isfile("phenotypes.both_sexes.tsv.bgz"):
        print("Downloading phenotypes.both_sexes.tsv.bgz")
        download("https://www.dropbox.com/s/d4mlq9ly93yhjyt/phenotypes.both_sexes.tsv.bgz?dl=1", "phenotypes.both_sexes.tsv.bgz")
else:
        print("phenotypes.both_sexes.tsv.bgz exists")




# Initialize MySQL database in chunks (taking small chunks for now as proof of concept for the app):
engine = sa.create_engine('mysql://root:root@127.0.0.1/uk_biobank')
inspector = inspect(engine)
tables = inspector.get_table_names()
print(tables)
# columns = inspector.get_columns(tables[1])
# for column in columns:
#     print(column["name"], column["type"])

if "variants" not in tables:
        chunks = pd.read_csv("variants.tsv.bgz", compression="gzip", sep="\t", chunksize=5000)
        for chunk in chunks:
                chr = []
                for chrrow in list(chunk['chr']):
                        if chrrow == "X":
                                chr.append(23)
                        else:
                                try:
                                        chr.append(int(chrrow))
                                except:
                                        chr.append(chrrow)
                chunk['chr'] = chr
                chunk.set_index(['chr','pos','ref','alt', 'variant'], inplace=True)
                chunk.to_sql(name="variants", if_exists='append', index=True, index_label=['chr','pos','ref','alt', 'variant', 'rsid'], 
                        con=engine, dtype={'ref': String(512), 'alt': String(512), 'variant': String(512), 'rsid': String(50)})
                break
        engine.execute("ALTER TABLE `uk_biobank`.`variants` add primary key(chr, pos, ref(50), alt(50));")

if "phenotypes_both_sexes" not in tables:
        pheno_df = pd.read_csv("phenotypes.both_sexes.tsv.bgz", compression="gzip", sep="\t")
        pheno_df.set_index(['phenotype'], inplace=True)
        pheno_df.to_sql(name="phenotypes_both_sexes", index=True, index_label='phenotype', con=engine, dtype={'phenotype': String(100)})
        engine.execute("ALTER TABLE `uk_biobank`.`phenotypes_both_sexes` add primary key(phenotype(100));")

# Not necessary...
# if "manifest" not in tables:
#         ukbb_manifest_df.to_sql(name="manifest", con=engine)


for filename in filenames:
        if filename not in tables:
                chunks = pd.read_csv(filename, compression='gzip', sep='\t', chunksize=5000)
                for chunk in chunks:
                        # # Adding chromosome and basepair position columns from variant column:  <--- skipping this; will do a join with variants table on variant column
                        # chr = []
                        # for variant in list(chunk['variant']):
                        #         chrom = variant.split(":")[0]
                        #         if chrom == "X":
                        #                 chr.append(23)
                        #         else:
                        #                 try:
                        #                         chr.append(int(chrom))
                        #                 except:
                        #                         chr.append(chrom)
                        # chunk['chr'] = chr
                        # chunk['pos'] = [int(variant.split(":")[1]) for variant in list(chunk['variant'])]
                        # chunk['ref'] = [variant.split(":")[2] for variant in list(chunk['variant'])]
                        # chunk['alt'] = [variant.split(":")[3] for variant in list(chunk['variant'])]
                        # cols = chunk.columns.tolist()
                        # cols = cols[-4:] + cols[:-4] # re-arranging to put chr,pos,ref,alt columns in front
                        # chunk = chunk[cols]
                        # chunk.set_index(['chr', 'pos','ref','alt'], inplace=True)
                        tbl_name = filename.split(".")[0] + "_" + filename.split(".")[3]
                        chunk.set_index(['variant'], inplace=True)
                        chunk.to_sql(name=tbl_name, if_exists='append', index=True, index_label=['variant'], con=engine, dtype={'variant': String(512)}) # push this chunk to sql
                        break
                engine.execute(f"""ALTER TABLE `uk_biobank`.`{tbl_name}` add primary key(variant(512));""")


