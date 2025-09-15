-- Create schema

DROP SCHEMA retrotector_dream CASCADE;
CREATE SCHEMA retrotector_dream;

-- Set Schema

SET search_path TO retrotector_dream;

-- ENUM Types
CREATE TYPE motif_type AS ENUM ('Slippery', 'PseudoKnot', 'SpliceAcceptor', 'SpliceDonor');
CREATE TYPE ltr_type AS ENUM ('solo', '5', '3');
CREATE TYPE chain_type AS ENUM ('P', 'S');

-- Table: seq
--CREATE TABLE seq (
--    id SERIAL PRIMARY KEY,
--    file_name TEXT NOT NULL,
--    contig TEXT NOT NULL,
--    chunk TEXT NOT NULL
--);

-- Table: run_metadata
CREATE TABLE run_metadata (
    id SERIAL PRIMARY KEY,
    -- seq_id INTEGER REFERENCES seq(id) ON DELETE SET NULL,
    executer TEXT NOT NULL,
    dna_file TEXT NOT NULL,
    selected TEXT NOT NULL,
    database TEXT NOT NULL,
    execution_duration INTEGER NOT NULL,
    selection_threshold FLOAT NOT NULL,
    input_file TEXT NOT NULL,
    improve_hits_max INTEGER NOT NULL,
    conservation_factor INTEGER NOT NULL,
    subgene_hits_max INTEGER NOT NULL,
    script_path TEXT NOT NULL,
    max_subgene_skip INTEGER NOT NULL,
    strand TEXT NOT NULL,
    sdfactor BOOLEAN NOT NULL,
    broken_passes INTEGER NOT NULL,
    fit_puteins TEXT,
    broken_penalty FLOAT NOT NULL,
    final_selection_threshold FLOAT NOT NULL,
    keep_threshold FLOAT NOT NULL,
    frame_factor FLOAT NOT NULL,
    length_bonus FLOAT NOT NULL,
    orfid_min_score INTEGER NOT NULL,
    make_chains_files TEXT NOT NULL,
    debugging TEXT,
    script_input TEXT NOT NULL,
    run_datetime TIMESTAMP,
    retrotector_version TEXT NOT NULL,
    db_name TEXT NOT NULL,
    db_last_modified_datetime TIMESTAMP
);

-- Table: herv_chain (was pseugid)
CREATE TABLE herv_chain (
    id SERIAL PRIMARY KEY,
    -- seq_id INTEGER REFERENCES seq(id) ON DELETE CASCADE,
    run_metadata_id INTEGER REFERENCES run_metadata(id) ON DELETE SET NULL,
    type_of_chain chain_type NOT NULL,
    chain_level INTEGER NOT NULL,
    chain_start_idx INTEGER NOT NULL,
    chain_end_idx INTEGER NOT NULL,
    retrovirus_type TEXT NOT NULL,
    score INTEGER NOT NULL,
    integration_sites TEXT
);

-- Table: ltr
CREATE TABLE ltr (
    id SERIAL PRIMARY KEY,
    herv_chain_id INTEGER REFERENCES herv_chain(id) ON DELETE CASCADE,
    -- run_metadata_id INTEGER REFERENCES run_metadata(id) ON DELETE SET NULL,
    is_primary BOOLEAN NOT NULL,
    ltr_type ltr_type NOT NULL,
    factor_score FLOAT,
    virus_genus TEXT,
    peak_loc INTEGER,
    init_idx INTEGER NOT NULL,
    fin_idx INTEGER NOT NULL,
    adenylation_loc TEXT,
    adenylation_seq TEXT,
    u5nn_score FLOAT NOT NULL,
    u5nn_idx INTEGER NOT NULL,
    gtmodifier_score FLOAT NOT NULL,
    u3nn_score FLOAT NOT NULL,
    u3nn_idx INTEGER NOT NULL,
    tataa_score FLOAT NOT NULL,
    tataa_idx INTEGER NOT NULL,
    meme50_score FLOAT NOT NULL,
    meme50_idx INTEGER NOT NULL,
    motifs1_score FLOAT NOT NULL,
    motifs1_idx INTEGER NOT NULL,
    motifs2_score FLOAT NOT NULL,
    motifs2_idx INTEGER NOT NULL,
    transsites_score FLOAT NOT NULL,
    cpgmodifier_score FLOAT NOT NULL,
    spl8modifier_score FLOAT NOT NULL,
    limiters TEXT,
    tsd5 TEXT,
    tsd3 TEXT,
    similarity_start INT,
    similarity_end INT
);


-- Table: motifs
CREATE TABLE motifs (
    id SERIAL PRIMARY KEY,
    herv_chain_id INTEGER REFERENCES herv_chain(id) ON DELETE CASCADE,
    type motif_type NOT NULL,
    pos_init INTEGER NOT NULL,
    pos_end INTEGER NOT NULL,
    score INTEGER NOT NULL
);

-- Table: retrovirus_type_probs
CREATE TABLE retrovirus_type_probs (
    id SERIAL PRIMARY KEY,
    herv_chain_id INTEGER REFERENCES herv_chain(id) ON DELETE CASCADE,
    A FLOAT NOT NULL,
    B FLOAT NOT NULL,
    C FLOAT NOT NULL,
    D FLOAT NOT NULL,
    E FLOAT NOT NULL,
    L FLOAT NOT NULL,
    S FLOAT NOT NULL,
    G FLOAT NOT NULL,
    O FLOAT NOT NULL
);

-- Table: subgenes
CREATE TABLE subgenes (
    id SERIAL PRIMARY KEY,
    herv_chain_id INTEGER REFERENCES herv_chain(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    type TEXT,
    score INTEGER NOT NULL,
    hotspot INTEGER NOT NULL
);

-- Table: domains
CREATE TABLE domains (
    id SERIAL PRIMARY KEY,
    subgene_id INTEGER REFERENCES subgenes(id) ON DELETE CASCADE,
    idx INTEGER,
    type TEXT NOT NULL,
    origin TEXT,
    score INTEGER NOT NULL,
    hotspot INTEGER NOT NULL,
    frame INTEGER NOT NULL,
    pos_init INTEGER NOT NULL,
    pos_fin INTEGER NOT NULL,
    match_input TEXT NOT NULL,
    reference_match TEXT NOT NULL,
    n_bases INTEGER NOT NULL
);


CREATE TABLE ltrs_of_hervchain (
    id SERIAL PRIMARY KEY,
    herv_chain_id INTEGER NOT NULL REFERENCES herv_chain(id) ON DELETE CASCADE,
    ltr_id INTEGER NOT NULL REFERENCES ltr(id) ON DELETE CASCADE
);


