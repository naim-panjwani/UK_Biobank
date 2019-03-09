
import os

import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect


from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()
thepwd = list(pd.read_csv('pwd.txt').columns)[0]

app = Flask(__name__)
genomicWindowLimit = 2000000

#################################################
# Database Setup
#################################################

app.config["SQLALCHEMY_DATABASE_URI"] = ("mysql://naimpanjwani@ukbiobankmysql:%s@ukbiobankmysql.mysql.database.azure.com:3306/uk_biobank" % thepwd)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # to disable tracking by flask of SQLAlchemy session modifications
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(db.engine, reflect=True)

# Base.metadata.tables
Base.classes.keys()
Variants = Base.classes.variants
Phenotypes = Base.classes.phenotype_tables_added

#metadata = sqlalchemy.MetaData(bind=db.engine)

inspector = inspect(db.engine)
pheno_tables = inspector.get_table_names()
try:
    pheno_tables.remove('variants')
    pheno_tables.remove('phenotypes_both_sexes')
    pheno_tables.remove('phenotype_tables_added')
except:
    pass

conn = db.engine.connect()
session = Session(db.engine)

@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")

@app.route("/phenotypes")
def getAvailablePhenotypes():
    return jsonify(pheno_tables)

@app.route("/variant/<variant>")
def getVariantMetaData(variant):
    """Return one SNP's metadata"""

    # Use Pandas to perform the sql query
    stmt = session.query(Variants).filter(Variants.variant == variant).statement
    df = pd.read_sql_query(stmt, conn)

    # Format the data to send as json
    return jsonify(df.to_dict(orient='list'))

@app.route("/phenotype/<phenotype>")
def getPhenotypeDetails(phenotype):
    #sex = "_".join(phenotype.split("_")[2:])
    stmt = session.query(Phenotypes.Phenotype_description).filter(Phenotypes.Table_name == phenotype).statement
    df = pd.read_sql_query(stmt, conn)
    return jsonify(df.to_dict(orient="list"))

@app.route("/assoc/<phenotype>/<chr>/<startbp>/<endbp>")
def phenoAssocResults(phenotype, chr, startbp, endbp):
    """Return the association results for phenotype at chr:startbp-endbp."""

    # Use Pandas to perform the sql query
    if ((int(endbp) - int(startbp) > genomicWindowLimit) or (int(startbp) > int(endbp))):
        return render_template("invalid_input.html")
    else:
        # Small problem here in that the phenotype table names start with an integer, 
        # and so the class is inaccessible
        # (eg. get invalid token error for 3064_irnt_both_sexes when doing 
        # Base.classes.3064_irnt_both_sexes or rather exec(f"Base.classes.{phenotype}"))
        stmt = (f"""select `variants`.`chr`
        , `variants`.`pos`
        #, `variants`.`ref`
        #, `variants`.`alt`
        , `variants`.`rsid`
        , `variants`.`consequence`
        , `variants`.`consequence_category`
        #, `variants`.`info`
        #, `variants`.`call_rate`
        #, `variants`.`AC`
        , `variants`.`minor_AF`
        #, `variants`.`minor_allele`
        #, `variants`.`n_hom_ref`
        #, `variants`.`n_het`
        #, `variants`.`n_hom_var`
        #,`{phenotype}`.`low_confidence_variant`
        #,`{phenotype}`.`ytx`
        ,`{phenotype}`.`beta`
        #,`{phenotype}`.`se`
        #,`{phenotype}`.`tstat`
        ,`{phenotype}`.`pval`
        from `uk_biobank`.`variants`
        inner join `uk_biobank`.`{phenotype}`
        on `variants`.`variant` = `{phenotype}`.`variant`
        where `variants`.`chr` = {chr} and `variants`.`pos` >= {startbp} and `variants`.`pos` <= {endbp} and `{phenotype}`.`low_confidence_variant` <> 1;""")
        
        df = pd.read_sql_query(stmt, conn)
        df.dropna(subset=['pval', 'chr', 'pos'], inplace=True)

        # Format the data to send as json
        return jsonify(df.to_dict(orient='list'))

@app.route("/variantAt/<chr>/<startbp>/<endbp>")
def variantDetails(chr, startbp, endbp):
    """Return the data in variants table for region chr:startbp-endbp."""

    # Use Pandas to perform the sql query
    if ((int(endbp) - int(startbp) > genomicWindowLimit) or (int(startbp) > int(endbp))):
        return render_template("invalid_input.html")
    else:
        stmt = session.query(Variants).\
            filter(Variants.chr == chr).\
                filter(Variants.pos >= startbp).\
                    filter(Variants.pos <= endbp).statement
        df = pd.read_sql_query(stmt, conn)
        df.dropna(inplace=True)

        # Format the data to send as json
        return jsonify(df.to_dict(orient='list'))

if __name__ == "__main__":
    app.run()

