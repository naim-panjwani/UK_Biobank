############################################################################
# 
############################################################################

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


app = Flask(__name__)


#################################################
# Database Setup
#################################################

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:root@127.0.0.1/uk_biobank"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False # to disable tracking by flask of SQLAlchemy session modifications
db = SQLAlchemy(app)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(db.engine, reflect=True)

# Base.metadata.tables
Base.classes.keys()
Variants = Base.classes.variants
Phenotypes = Base.classes.phenotypes_both_sexes

#metadata = sqlalchemy.MetaData(bind=db.engine)

inspector = inspect(db.engine)
pheno_tables = inspector.get_table_names()
try:
    pheno_tables.remove('variants')
    pheno_tables.remove('phenotypes_both_sexes')
except:
    pass

conn = db.engine.connect()
session = Session(db.engine) # can't use as tables don't get reflected

@app.route("/")
def index():
    """Return the homepage."""
    return render_template("index.html")

@app.route("/phenotypes")
def getAvailablePhenotypes():
    return jsonify(pheno_tables)

@app.route("/<variant>")
def getVariantMetaData(variant):
    """Return one SNP's metadata"""

    # Use Pandas to perform the sql query
    stmt = session.query(Variants).filter(Variants.variant == variant).statement
    df = pd.read_sql_query(stmt, conn)

    # Format the data to send as json
    return jsonify(df.to_dict(orient='list'))

@app.route("/<phenotype>")
def getPhenotypeDetails(phenotype):
    phenocode = phenotype.split("_")[0] + "_" + phenotype.split("_")[1]
    #sex = "_".join(phenotype.split("_")[2:])
    stmt = session.query(Phenotypes).filter(Phenotypes.phenotype == phenocode).statement
    df = pd.read_sql_query(stmt, conn)
    return jsonify(df.to_dict(orient="list"))

@app.route("/<phenotype>/<chr>/<startbp>/<endbp>")
def phenoAssocResults(phenotype, chr, startbp, endbp):
    """Return the association results for phenotype at chr:startbp-endbp."""

    # Use Pandas to perform the sql query
    if (int(endbp) - int(startbp) > 2000000 or int(startbp) > int(endbp)):
        return "Please query a genomic region less than 2Mbp"
    else:
        # Small problem here in that the phenotype table names start with an integer, 
        # and so the class is inaccessible
        # (eg. get invalid token error for 3064_irnt_both_sexes when doing 
        # Base.classes.3064_irnt_both_sexes or rather exec(f"Base.classes.{phenotype}"))
        stmt = (f"""select `variants`.`chr`
                        , `variants`.`pos`
                        , `variants`.`ref`
                        , `variants`.`alt`
                        , `variants`.`rsid`
                        , `variants`.`consequence`
                        , `variants`.`consequence_category`
                        , `variants`.`info`
                        , `variants`.`call_rate`
                        , `variants`.`AC`
                        , `variants`.`minor_AF`
                        , `variants`.`minor_allele`
                        , `variants`.`n_hom_ref`
                        , `variants`.`n_het`
                        , `variants`.`n_hom_var`
                        ,`{phenotype}`.`low_confidence_variant`
                        ,`{phenotype}`.`ytx`
                        ,`{phenotype}`.`beta`
                        ,`{phenotype}`.`se`
                        ,`{phenotype}`.`tstat`
                        ,`{phenotype}`.`pval`
                        from `uk_biobank`.`variants`
                        inner join `uk_biobank`.`{phenotype}`
                        on `variants`.`variant` = `{phenotype}`.`variant`
                        where `variants`.`chr` = {chr} and `variants`.`pos` >= {startbp} and `variants`.`pos` <= {endbp};""")
        
        df = pd.read_sql_query(stmt, conn)

        # Format the data to send as json
        return jsonify(df.to_dict(orient='list'))

@app.route("/<chr>/<startbp>/<endbp>")
def variantDetails(chr, startbp, endbp):
    """Return the data in variants table for region chr:startbp-endbp."""

    # Use Pandas to perform the sql query
    # Note: can't do it via a session.query as the tables are not reflecting on Base
    if (int(endbp) - int(startbp) > 2000000 or int(startbp) > int(endbp)):
        return "Please query a genomic region less than 2Mbp"
    else:
        stmt = session.query(Variants).\
            filter(Variants.chr == chr).\
                filter(Variants.pos >= startbp).\
                    filter(Variants.pos <= endbp).statement
        df = pd.read_sql_query(stmt, conn)

        # Format the data to send as json
        return jsonify(df.to_dict(orient='list'))

if __name__ == "__main__":
    app.run()

