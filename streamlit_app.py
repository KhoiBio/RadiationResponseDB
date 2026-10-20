import streamlit as st
import pandas as pd
import oracledb
import os

# ---------------- ORACLE DB CONFIG ----------------

DB_USER = os.getenv("ORACLE_DB_USER")
DB_PASSWORD = os.getenv("ORACLE_DB_PASSWORD")
DB_DSN = "radiationresponsedb_high"  # Use alias from tnsnames.ora (adb_high, adb_low, adb_medium)

# Ensure TNS_ADMIN is set to wallet directory
TNS_ADMIN = os.getenv("TNS_ADMIN")
if not TNS_ADMIN:
    st.error("TNS_ADMIN environment variable is not set. Please set it to your wallet directory.")
    st.stop()

# ---------------- FUNCTIONS ----------------
@st.cache_data(ttl=3600)
def run_query(query):
    try:
        # Thin mode connection using wallet
        conn = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN)
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return pd.DataFrame()

# ---------------- STREAMLIT APP ----------------
st.title("Radiation Gene / Cancer Explorer")

# Sidebar filters
st.sidebar.header("Filters")
gene_input = st.sidebar.text_input("Search Gene Symbol")
cancer_input = st.sidebar.text_input("Search Cancer Type")
show_rank = st.sidebar.checkbox("Show Gene Ranking")

# ---------------- GENE SEARCH ----------------
if gene_input:
    st.subheader(f"Studies for Gene: {gene_input.upper()}")
    sql = f"""
        SELECT g.gene_symbol, s.pmid, s.title
        FROM GENE g
        JOIN GENE_RADIATION_LINK gl ON g.gene_id = gl.gene_id
        JOIN STUDY s ON gl.study_id = s.study_id
        WHERE UPPER(g.gene_symbol) LIKE UPPER('%{gene_input}%')
        ORDER BY s.pmid
    """
    df_gene = run_query(sql)
    st.dataframe(df_gene)

# ---------------- CANCER SEARCH ----------------
if cancer_input:
    st.subheader(f"Genes & Studies for Cancer: {cancer_input}")
    sql = f"""
        SELECT c.cancer_name, g.gene_symbol, s.pmid, s.title
        FROM CANCER_TYPE c
        JOIN GENE_CANCER_LINK gcl ON c.cancer_id = gcl.cancer_id
        JOIN GENE g ON g.gene_id = gcl.gene_id
        JOIN GENE_RADIATION_LINK gl ON g.gene_id = gl.gene_id
        JOIN STUDY s ON gl.study_id = s.study_id
        WHERE UPPER(c.cancer_name) LIKE UPPER('%{cancer_input}%')
        ORDER BY g.gene_symbol
    """
    df_cancer = run_query(sql)
    st.dataframe(df_cancer)

# ---------------- GENE–CANCER LINKS ----------------
st.subheader("All Gene–Cancer Links")
sql_links = """
    SELECT g.gene_symbol, c.cancer_name
    FROM GENE g
    JOIN GENE_CANCER_LINK gcl ON g.gene_id = gcl.gene_id
    JOIN CANCER_TYPE c ON gcl.cancer_id = c.cancer_id
"""
df_links = run_query(sql_links)
st.dataframe(df_links)

# ---------------- GENE RANKING ----------------
if show_rank:
    st.subheader("Gene Ranking by Number of Studies")
    sql_rank = """
        SELECT g.gene_symbol, COUNT(gl.study_id) AS study_count,
               RANK() OVER (ORDER BY COUNT(gl.study_id) DESC) AS rank_overall
        FROM GENE g
        LEFT JOIN GENE_RADIATION_LINK gl ON g.gene_id = gl.gene_id
        GROUP BY g.gene_symbol
        ORDER BY rank_overall
    """
    df_rank = run_query(sql_rank)
    st.dataframe(df_rank)

# ---------------- DOWNLOAD DATA ----------------
st.subheader("Download Tables")
if st.button("Download Gene–Study Table"):
    csv = df_gene.to_csv(index=False) if gene_input else df_links.to_csv(index=False)
    st.download_button("Download CSV", csv, "table.csv", "text/csv")

