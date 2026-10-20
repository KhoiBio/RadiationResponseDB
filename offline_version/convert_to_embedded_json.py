import sqlite3
import json

# Connect to SQLite database
conn = sqlite3.connect("radiation.db")
cursor = conn.cursor()

# Helper function to fetch all rows from a table as list of dicts
def fetch_all(table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]

# Fetch data from all relevant tables
data = {
    "genes": fetch_all("GENE"),
    "studies": fetch_all("STUDY"),
    "gene_radiation_links": fetch_all("GENE_RADIATION_LINK"),
    "cancer_types": fetch_all("CANCER_TYPE"),
    "gene_cancer_links": fetch_all("GENE_CANCER_LINK")
}

conn.close()

# Generate HTML with embedded JSON
html_template = f"""<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <title>Radiation Gene / Cancer Explorer</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    input, button {{ margin: 5px; padding: 5px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
    th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
    th {{ background-color: #f2f2f2; }}
  </style>
</head>
<body>
  <h1>Radiation Gene / Cancer Explorer</h1>

  <h3>Search by Gene Symbol</h3>
  <input type="text" id="geneInput" placeholder="e.g. TP53">
  <button onclick="searchGene()">Search</button>
  <div id="geneResults"></div>

  <h3>Search by Cancer Type</h3>
  <input type="text" id="cancerInput" placeholder="e.g. Breast Cancer">
  <button onclick="searchCancer()">Search</button>
  <div id="cancerResults"></div>

  <h3>All Gene-Cancer Links</h3>
  <button onclick="showLinks()">Show All</button>
  <div id="linkResults"></div>

  <h3>Download Current Table</h3>
  <button onclick="downloadCSV()">Download CSV</button>

  <script>
    const data = {json.dumps(data)};
    let currentTable = [];

    function searchGene() {{
      const gene = document.getElementById("geneInput").value.toUpperCase();
      const results = data.gene_radiation_links.map(link => {{
        const geneObj = data.genes.find(g => g.gene_id === link.gene_id);
        const studyObj = data.studies.find(s => s.study_id === link.study_id);
        return {{
          gene_symbol: geneObj?.gene_symbol,
          pmid: studyObj?.pmid,
          title: studyObj?.title
        }};
      }}).filter(r => r.gene_symbol && r.gene_symbol.includes(gene));
      currentTable = results;
      renderTable(results, "geneResults");
    }}

    function searchCancer() {{
      const cancer = document.getElementById("cancerInput").value.toLowerCase();
      const results = data.gene_cancer_links.map(link => {{
        const geneObj = data.genes.find(g => g.gene_id === link.gene_id);
        const cancerObj = data.cancer_types.find(c => c.cancer_id === link.cancer_id);
        return {{
          gene_symbol: geneObj?.gene_symbol,
          cancer_name: cancerObj?.cancer_name
        }};
      }}).filter(r => r.cancer_name && r.cancer_name.toLowerCase().includes(cancer));
      currentTable = results;
      renderTable(results, "cancerResults");
    }}

    function showLinks() {{
      const results = data.gene_cancer_links.map(link => {{
        const geneObj = data.genes.find(g => g.gene_id === link.gene_id);
        const cancerObj = data.cancer_types.find(c => c.cancer_id === link.cancer_id);
        return {{
          gene_symbol: geneObj?.gene_symbol,
          cancer_name: cancerObj?.cancer_name
        }};
      }});
      currentTable = results;
      renderTable(results, "linkResults");
    }}

    function renderTable(rows, containerId) {{
      const container = document.getElementById(containerId);
      if (rows.length === 0) {{
        container.innerHTML = "<p>No results found.</p>";
        return;
      }}
      const headers = Object.keys(rows[0]);
      let html = "<table><tr>" + headers.map(h => `<th>${{h}}</th>`).join("") + "</tr>";
      html += rows.map(row => "<tr>" + headers.map(h => `<td>${{row[h]}}</td>`).join("") + "</tr>").join("");
      html += "</table>";
      container.innerHTML = html;
    }}

    function downloadCSV() {{
      if (currentTable.length === 0) return alert("No data to download.");
      const headers = Object.keys(currentTable[0]);
      const csv = [headers.join(",")].concat(
        currentTable.map(row => headers.map(h => `"${{row[h]}}"`).join(","))
      ).join("\\n");
      const blob = new Blob([csv], {{ type: "text/csv" }});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "table.csv";
      a.click();
      URL.revokeObjectURL(url);
    }}
  </script>
</body>
</html>
"""

# Save to file
with open("index.html", "w") as f:
    f.write(html_template)

print("Self-contained dashboard saved as 'index.html'")
