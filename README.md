# RadiationResponseDB
An app that track a curated list of genes that are interest to me. it show all publication associated with the genes and the terms radiation, radioresistance, and radiosensitivity.
The app can be found here: http://146.235.210.139:8501/

# Online version
### extract any publication related to radioresistance from 2005-2025:

pubmed_cache.py extract all paper published from 2005-2025 and related to radioresistance and cancer
1. total paper is 7130 paper.
The extracted pubmed search cache can be found as json file :pubmed_radiation_titles_20yrs.json. pubmed_radiation_titles_20yrs.csv shows all pubmedid and title.

### extract any publication from above related to curated gene list:

radiation_genes_cancer_pipeline.py for curated genes with these following related terms

CURATED_GENES = [ our DEGs with p-value < 0.05, log2FC > 3 or < -3]

The publication is also related to these cancers:

CANCER_KEYWORD = {
    "breast": "Breast Cancer",
    "lung": "Lung Cancer",
    "colorectal": "Colorectal Cancer",
    "prostate": "Prostate Cancer",
    "glioblastoma": "Glioblastoma",
    "leukemia": "Leukemia",
    "ovarian": "Ovarian Cancer",
    "pancreatic": "Pancreatic Cancer",
    "melanoma": "Melanoma",
    "sarcoma": "Sarcoma",
    "cervical": "Cervical Cancer",
    "head and neck": "Head and Neck Cancer"
}
RADIATION_TERMS = "(radioresistance)"

### SQL database
Oracle Autonomous AI Daabase was chosen due to its generous "always free" offer

5 SQL tables are created with SQL commands in create_table_onsql.txt
All sql files created with radiation_genes_cancer_pipeline.py are then loaded into the database in this order:
1. genes_bulk_insert.sql
2. studies_bulk_insert.sql
3. gene_radiation_link_insert.sql
4. cancer_type_insert.sql
5. gene_cancer_link_insert.sql

### Python app deployment
Streamlit was chosen as a deployment method due to its ease of use.
streamlit_app.py is the app python script
Oracle Compute free instance is used to deploy the app following instruction in how_to_run file

# Offline version with JavaScript and HTML

### to create database with SQLite
All scripts can be found in offline_embedded_json_html directory

1. Used all the SQL files generated for online version
2. Create a create table SQL file to make table for the offline SQLite
3. convertsql_tojson.py use SQLite and JSON (JavaScript Object Notation) in Python to make build offline database
4. convert_to_embedded_json.py make the HTML offline dashboard with embedded data from the created json database file in step 3
5. radiogeneexplorer.html is the offline dashboard of the online dashboard deployed with streamlit above.


