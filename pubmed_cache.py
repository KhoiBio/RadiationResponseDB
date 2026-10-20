from Bio import Entrez
import json
import csv
import time
import os
from datetime import datetime

# Always tell NCBI who you are
Entrez.email = "your_email@example.com"

CACHE_FILE = "pubmed_radiation_titles_20yrs.json"
CSV_FILE = "pubmed_radiation_titles_20yrs.csv"

# Load cache if it exists
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        pubmed_cache = json.load(f)
else:
    pubmed_cache = {}

def fetch_pubmed_titles(query, batch_size=200):
    """Fetch all PubMed IDs and titles for a query (past 10 years)."""
    if query in pubmed_cache:
        print(f"Resuming cached query: {query}")
        results = pubmed_cache[query]
        fetched_until = len(results)
    else:
        print(f"Starting new query: {query}")
        handle = Entrez.esearch(db="pubmed", term=query, retmax=0)
        record = Entrez.read(handle)
        handle.close()
        total = int(record["Count"])
        print(f"Total records found: {total}")
        results = []
        fetched_until = 0
        pubmed_cache[query] = results

    # get all IDs
    all_ids = []
    while True:
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retstart=fetched_until,
            retmax=batch_size
        )
        record = Entrez.read(handle)
        handle.close()
        ids = record["IdList"]
        if not ids:
            break
        all_ids.extend(ids)
        fetched_until += len(ids)
        print(f"Collected {fetched_until} IDs...")
        time.sleep(0.3)
        if fetched_until >= int(record["Count"]):
            break

    # fetch titles for all IDs
    results = []
    for i in range(0, len(all_ids), batch_size):
        id_batch = all_ids[i : i + batch_size]
        handle = Entrez.efetch(
            db="pubmed", id=",".join(id_batch),
            rettype="medline", retmode="text"
        )
        data = handle.read()
        handle.close()

        # Parse PMID + Title
        for entry in data.split("\n\n"):
            lines = entry.split("\n")
            pmid = None
            title = None
            for line in lines:
                if line.startswith("PMID- "):
                    pmid = line.replace("PMID- ", "").strip()
                elif line.startswith("TI  - "):
                    title = line.replace("TI  - ", "").strip()
            if pmid and title:
                results.append({"PMID": pmid, "Title": title})

        print(f"Fetched titles for {i + batch_size} / {len(all_ids)} papers...")
        pubmed_cache[query] = results
        with open(CACHE_FILE, "w") as f:
            json.dump(pubmed_cache, f, indent=2)
        time.sleep(0.5)

    print(f"Finished: {len(results)} records fetched and cached.")
    return results

def save_to_csv(results, csv_path):
    """Save results to CSV file."""
    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["PMID", "Title"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)
    print(f" Saved results to {csv_path}")


# Run the script
if __name__ == "__main__":
    # Compute date range (past 20 years)
    current_year = datetime.now().year
    start_year = current_year - 20

    # Add date filter to query
    query = f"(radioresistance AND cancer AND ({start_year}[PDAT] : {current_year}[PDAT])"
    print(f"Running query: {query}")

    results = fetch_pubmed_titles(query)
    save_to_csv(results, CSV_FILE)

    print(f"\nSaved {len(results)} PubMed IDs + titles (past 20 years) to:")
    print(f"  - {CACHE_FILE}")
    print(f"  - {CSV_FILE}")

