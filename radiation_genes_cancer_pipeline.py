#!/usr/bin/env python3
"""
incremental_radiation_gene_pipeline_batched.py

Processes curated genes in batches of 50 and appends to SQL files incrementally.
"""

import os
import json
import time
from Bio import Entrez
from tqdm import tqdm

# CONFIG
Entrez.email = os.environ.get("ENTREZ_EMAIL", "your_email@example.com")
MAX_PMIDS_PER_GENE = 999
SLEEP_TIME = 0.2
CACHE_FILE = "pubmed_radiation_titles_20yrs.json"
BATCH_SIZE = 50  # Process 50 genes per batch

# Load curated genes
with open("listofgenes.txt") as f:
    content = f.read().strip()
CURATED_GENES = [gene.strip().strip('"') for gene in content.split(",")]

# Cancer keywords
CANCER_KEYWORDS = {
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

RADIATION_TERMS = "(radiation OR radioresistance OR radiosensitivity)"

# FUNCTIONS 

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def query_pubmed_pmids(gene_symbol, max_pmids=MAX_PMIDS_PER_GENE):
    term = f"{gene_symbol}[Title/Abstract] AND {RADIATION_TERMS}"
    try:
        handle = Entrez.esearch(db="pubmed", term=term, retmax=max_pmids)
        record = Entrez.read(handle)
        handle.close()
        return record.get("IdList", [])
    except Exception as e:
        print(f"Error fetching PMIDs for {gene_symbol}: {e}")
        return []

def fetch_pubmed_title(pmid):
    try:
        handle = Entrez.esummary(db="pubmed", id=pmid, retmode="xml")
        rec = Entrez.read(handle)
        handle.close()
        return rec[0].get("Title", "").replace("'", "''")
    except Exception as e:
        print(f"Error fetching title for PMID {pmid}: {e}")
        return ""

def detect_cancer_types(title):
    title_lower = title.lower()
    found = set()
    for key, name in CANCER_KEYWORDS.items():
        if key in title_lower:
            found.add(name)
    return list(found)

# MAIN

def main():
    print("Loading PubMed cache...")
    cache = load_cache()  # {gene_symbol: [pmids]}

    # Open SQL files in append mode
    with open("genes_bulk_insert.sql", "a") as f_gene, \
         open("studies_bulk_insert.sql", "a") as f_study, \
         open("gene_radiation_link_insert.sql", "a") as f_link, \
         open("cancer_type_insert.sql", "a") as f_cancer, \
         open("gene_cancer_link_insert.sql", "a") as f_gene_cancer:

        study_id_counter = 1
        cancer_name_to_id = {}
        cancer_counter = 1

        # Process genes in batches
        for batch_start in range(0, len(CURATED_GENES), BATCH_SIZE):
            batch_genes = CURATED_GENES[batch_start:batch_start+BATCH_SIZE]
            print(f"Processing genes {batch_start+1}-{batch_start+len(batch_genes)}...")

            for gene_symbol in batch_genes:
                gene_symbol = gene_symbol.upper()

                # Insert gene
                f_gene.write(f"INSERT INTO GENE (gene_symbol, gene_name, entrez_id) "
                             f"VALUES ('{gene_symbol}', NULL, NULL);\n")

                # PubMed query (only new PMIDs)
                new_pmids = query_pubmed_pmids(gene_symbol)
                cached_pmids = cache.get(gene_symbol, [])
                pmids_to_process = [pmid for pmid in new_pmids if pmid not in cached_pmids]

                if not pmids_to_process:
                    continue

                for pmid in pmids_to_process:
                    title = fetch_pubmed_title(pmid)

                    # STUDY insert
                    f_study.write(f"INSERT INTO STUDY (study_id, title, pmid, year, journal, impact_factor) "
                                  f"VALUES ({study_id_counter}, '{title}', '{pmid}', NULL, NULL, NULL);\n")

                    # Gene~Study link
                    f_link.write(f"INSERT INTO GENE_RADIATION_LINK (gene_id, study_id, evidence_type, effect_direction, confidence_score) "
                                 f"SELECT gene_id, {study_id_counter}, 'Literature', 'Unknown', 0.8 "
                                 f"FROM GENE WHERE gene_symbol='{gene_symbol}';\n")

                    # Detect cancer types
                    cancer_types = detect_cancer_types(title)
                    for ct in cancer_types:
                        if ct not in cancer_name_to_id:
                            f_cancer.write(f"INSERT INTO CANCER_TYPE (cancer_id, cancer_name) "
                                           f"VALUES ({cancer_counter}, '{ct}');\n")
                            cancer_name_to_id[ct] = cancer_counter
                            cancer_counter += 1
                        f_gene_cancer.write(f"INSERT INTO GENE_CANCER_LINK (gene_id, cancer_id) "
                                            f"SELECT gene_id, {cancer_name_to_id[ct]} "
                                            f"FROM GENE WHERE gene_symbol='{gene_symbol}';\n")

                    study_id_counter += 1
                    time.sleep(SLEEP_TIME)

                # Update cache for this gene
                cache[gene_symbol] = cached_pmids + pmids_to_process

            # Save cache after each batch
            save_cache(cache)
            print(f"Batch {batch_start+1}-{batch_start+len(batch_genes)} completed. Cache saved.")

    print("All batches processed. SQL files updated successfully!")

if __name__ == "__main__":
    main()

