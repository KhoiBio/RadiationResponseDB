CREATE TABLE GENE (
    gene_id INTEGER PRIMARY KEY AUTOINCREMENT,
    gene_symbol TEXT,
    gene_name TEXT,
    entrez_id TEXT
);

CREATE TABLE STUDY (
    study_id INTEGER PRIMARY KEY,
    title TEXT,
    pmid TEXT,
    year TEXT,
    journal TEXT,
    impact_factor REAL
);

CREATE TABLE GENE_RADIATION_LINK (
    gene_id INTEGER,
    study_id INTEGER,
    evidence_type TEXT,
    effect_direction TEXT,
    confidence_score REAL,
    FOREIGN KEY (gene_id) REFERENCES GENE(gene_id),
    FOREIGN KEY (study_id) REFERENCES STUDY(study_id)
);

CREATE TABLE CANCER_TYPE (
    cancer_id INTEGER PRIMARY KEY,
    cancer_name TEXT
);

CREATE TABLE GENE_CANCER_LINK (
    gene_id INTEGER,
    cancer_id INTEGER,
    FOREIGN KEY (gene_id) REFERENCES GENE(gene_id),
    FOREIGN KEY (cancer_id) REFERENCES CANCER_TYPE(cancer_id)
);
