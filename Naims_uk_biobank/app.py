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

# Base.metadata.tables # the tables are listed here
# Base.classes.keys() # but this returns an empty list and shows tables are not reflected...
#                     # perhaps I had to define the primary key per table and foreign keys

inspector = inspect(db.engine)
pheno_tables = inspector.get_table_names()
try:
    pheno_tables.remove('variants')
    pheno_tables.remove('manifest')
except:
    pass

conn = db.engine.connect()
#session = Session(db.engine) # can't use as tables don't get reflected

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
    # Note: can't do it via a session.query as the tables are not reflecting on Base
    stmt = (f"""SELECT *
    FROM `uk_biobank`.`variants`
    WHERE variant = "{variant}";""")
    df = pd.read_sql_query(stmt, conn)

    # Format the data to send as json
    return jsonify(df.to_dict(orient='list'))

@app.route("/manifest/<phenotype>")
def getManifestDetails(phenotype):
    phenocode = phenotype.split("_")[0] + "_" + phenotype.split("_")[1]
    sex = "_".join(phenotype.split("_")[2:])
    stmt = (f"""SELECT *
    FROM `uk_biobank`.`manifest`
    WHERE `manifest`.`Phenotype Code` = "{phenocode}" AND `manifest`.`Sex` = "{sex}";""")
    df = pd.read_sql_query(stmt, conn)
    return jsonify(df.to_dict(orient="list"))

@app.route("/<phenotype>/<chr>/<startbp>/<endbp>")
def phenoAssocResults(phenotype, chr, startbp, endbp):
    """Return the association results for phenotype at chr:startbp-endbp."""

    # Use Pandas to perform the sql query
    # Note: can't do it via a session.query as the tables are not reflecting on Base
    if (int(endbp) - int(startbp) > 2000000):
        return "Please query a genomic region less than 2Mbp"
    else:
        stmt = (f"""SELECT *
        FROM `uk_biobank`.`{phenotype}`
        WHERE chr = {chr} AND pos >= {startbp} AND pos <= {endbp};""")
        df = pd.read_sql_query(stmt, conn)

        # Format the data to send as json
        return jsonify(df.to_dict(orient='list'))

@app.route("/<chr>/<startbp>/<endbp>")
def variantDetails(chr, startbp, endbp):
    """Return the data in variants table for region chr:startbp-endbp."""

    # Use Pandas to perform the sql query
    # Note: can't do it via a session.query as the tables are not reflecting on Base
    if (int(endbp) - int(startbp) > 2000000):
        return "Please query a genomic region less than 2Mbp"
    else:
        stmt = (f"""SELECT *
        FROM `uk_biobank`.`variants`
        WHERE chr = {chr} AND pos >= {startbp} AND pos <= {endbp};""")
        df = pd.read_sql_query(stmt, conn)

        # Format the data to send as json
        return jsonify(df.to_dict(orient='list'))

if __name__ == "__main__":
    app.run()

