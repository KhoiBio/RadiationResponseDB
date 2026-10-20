import sqlite3
import json

# Create and connect to SQLite database
conn = sqlite3.connect("radiation.db")
cursor = conn.cursor()

# Create tables
with open("create_tables.sql", "r") as f:
    cursor.executescript(f.read())

# Insert data from your SQL files
sql_files = [
    "genes_bulk_insert.sql",
    "studies_bulk_insert.sql",
    "gene_radiation_link_insert.sql",
    "cancer_type_insert.sql",
    "gene_cancer_link_insert.sql"
]

for file in sql_files:
    with open(file, "r") as f:
        cursor.executescript(f.read())

conn.commit()

# Export to JSON
def fetch_all(table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]

data = {
    "genes": fetch_all("GENE"),
    "studies": fetch_all("STUDY"),
    "gene_radiation_links": fetch_all("GENE_RADIATION_LINK"),
    "cancer_types": fetch_all("CANCER_TYPE"),
    "gene_cancer_links": fetch_all("GENE_CANCER_LINK")
}

with open("radiation_data.json", "w") as f:
    json.dump(data, f, indent=2)

print("radiation_data.json created successfully.")
conn.close()
