#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
retrotector.py

Command-line tool to parse Retrotector JSON output files and insert structured data into a database.

Author: Mauricio Moldes Quaresma, Joao Medonca <mauricio.moldes.quaresma@rigshopitalet.dk>
Created: 2025-08-05
Version: 0.1.0
License: MIT

Description:
    This tool is designed to process output from Retrotector (in JSON format),
    extract relevant structural annotations, and insert them into a PostgreSQL
    (or other SQL-compliant) database for downstream querying and analysis.

Usage:
    python retrotector.py --input file.json --db postgresql://user:pass@host/db

"""

__author__ = "Mauqua"
__version__ = "0.1.0"
__license__ = "MIT"


import argparse
import json
from datetime import datetime
import psycopg2
from psycopg2 import sql

def load_retrotector_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def parse_run_metadata(json_data):
    """
    Parse the Retrotector JSON header and footer sections
    into a dictionary matching the run_metadata DB schema.
    """
    header = json_data.get("header", {})
    footer = json_data.get("footer", {})

    # Helper to convert string boolean to Python bool
    def to_bool(val):
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            return val.lower() in ("yes", "true", "1")
        return bool(val)

    # Convert the footer datetime strings to Python datetime objects
    def parse_datetime(dt_str):
        # Example string: "Mon Aug 04 04:51:37 GMT 2025"
        try:
            return datetime.strptime(dt_str, "%a %b %d %H:%M:%S GMT %Y")
        except Exception:
            return None

    metadata = {
        "executer": footer.get("executer") or header.get("Executor"),
        "dna_file": footer.get("DNAFile") or header.get("DNAFile"),
        "selected": header.get("Selected"),
        "database": footer.get("Database") or header.get("Database"),
        "execution_duration": int(footer.get("execution_duration", 0)),
        "selection_threshold": float(footer.get("SelectionThreshold", 0)),
        "input_file": footer.get("InputFile") or header.get("InputFile", ""),
        "improve_hits_max": int(footer.get("ImproveHitsMax", 0)),
        "conservation_factor": int(footer.get("ConservationFactor", 0)),
        "subgene_hits_max": int(footer.get("SubGeneHitsMax", 0)),
        "script_path": footer.get("ScriptPath", ""),
        "max_subgene_skip": int(footer.get("MaxSubGeneSkip", 0)),
        "strand": footer.get("Strand", ""),
        "sdfactor": to_bool(footer.get("SDFactor", False)),
        "broken_passes": int(footer.get("BrokenPasses", 0)),
        "fit_puteins": footer.get("FitPuteins"),
        "broken_penalty": float(footer.get("BrokenPenalty", 0)),
        "final_selection_threshold": float(footer.get("FinalSelectionThreshold", 0)),
        "keep_threshold": float(footer.get("KeepThreshold", 0)),
        "frame_factor": float(footer.get("FrameFactor", 0)),
        "length_bonus": float(footer.get("LengthBonus", 0)),
        "orfid_min_score": int(footer.get("ORFIDMinScore", 0)),
        "make_chains_files": footer.get("MakeChainsFiles", ""),
        "debugging": footer.get("Debugging"),
        "script_input": footer.get("script_input", ""),
        "run_datetime": parse_datetime(footer.get("run_datetime")),
        "retrotector_version": footer.get("retrotector_version", ""),
        "db_name": footer.get("db_name", ""),
        "db_last_modified_datetime": parse_datetime(footer.get("db_last_modified_datetime")),
    }

    return metadata

def insert_run_metadata(conn, metadata):
    """
    Insert the run_metadata dictionary into the run_metadata table.
    
    :param conn: psycopg2 connection object
    :param metadata: dict with keys matching run_metadata columns
    """
    columns = list(metadata.keys())
    values = [metadata[col] for col in columns]

    # Build the INSERT query dynamically to avoid mistakes
    query = sql.SQL("INSERT INTO run_metadata ({fields}) VALUES ({placeholders}) RETURNING id").format(
        fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
        placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
    )

    with conn.cursor() as cur:
        cur.execute(query, values)
        inserted_id = cur.fetchone()[0]
        conn.commit()
        return inserted_id
    
def parse_ltrs(json_data: dict) -> list[dict]:
    """
    Parses both 'soloLTRs' (from top level) and 'LTRs' (from each chain in pseuGID).
    Adds 'herv_chain_index' to LTRs to track their parent.
    Returns a list of LTR dictionaries ready for SQL insertion.
    """

    ltr_entries = []

    # 1. Parse soloLTRs
    for entry in json_data.get("soloLTRs", []):
        ltr_entries.append({
            "herv_chain_index": None,  # Will be linked if logic exists to associate with chains
            "is_primary": entry.get("primary", False),
            "ltr_type": "solo",
            "factor_score": None,
            "virus_genus": None,
            "peak_loc": entry.get("peak_loc"),
            "init_idx": entry["init_idx"],
            "fin_idx": entry["fin_idx"],
            "adenylation_loc": entry.get("adenylation_loc"),
            "adenylation_seq": entry.get("adenylation_seq"),
            "u5nn_score": entry.get("U5NN_score"),
            "u5nn_idx": entry.get("U5NN_loc"),
            "gtmodifier_score": entry.get("GT_score"),
            "u3nn_score": entry.get("U3NN_score"),
            "u3nn_idx": entry.get("U3NN_loc"),
            "tataa_score": entry.get("TATAA_score"),
            "tataa_idx": entry.get("TATAA_loc"),
            "meme50_score": entry.get("MEME50_score"),
            "meme50_idx": entry.get("MEME50_loc"),
            "motifs1_score": entry.get("Mot1_score"),
            "motifs1_idx": entry.get("Mot1_loc"),
            "motifs2_score": entry.get("Mot2_score"),
            "motifs2_idx": entry.get("Mot2_loc"),
            "transsites_score": entry.get("Trans_score"),
            "cpgmodifier_score": entry.get("CpG_score"),
            "spl8modifier_score": entry.get("Spl8_score"),
            "limiters": None,
            "tsd5": entry.get("TSD5"),
            "tsd3": entry.get("TSD3"),
            "similarity_start": None,
            "similarity_end": None
        })

    # 2. Parse full LTRs from each HERV chain (pseuGID)
    for chain_index, chain in enumerate(json_data.get("pseuGID", [])):
        for entry in chain.get("LTRs", []):  # LTRs inside each chain
            ltr_entries.append({
                "herv_chain_index": chain_index,
                "is_primary": entry.get("primary", False),
                "ltr_type": entry.get("LTR_type"),
                "factor_score": entry.get("factor_score"),
                "virus_genus": entry.get("virus_genus"),
                "peak_loc": None,
                "init_idx": entry["init_idx"],
                "fin_idx": entry["fin_idx"],
                "adenylation_loc": entry.get("adenylation_loc"),
                "adenylation_seq": entry.get("adenylation_seq"),
                "u5nn_score": entry.get("U5NN_score"),
                "u5nn_idx": entry.get("U5NN_idx"),
                "gtmodifier_score": entry.get("GTModifier_score"),
                "u3nn_score": entry.get("U3NN_score"),
                "u3nn_idx": entry.get("U3NN_idx"),
                "tataa_score": entry.get("TATAA_score"),
                "tataa_idx": entry.get("TATAA_idx"),
                "meme50_score": entry.get("MEME50_score"),
                "meme50_idx": entry.get("MEME50_idx"),
                "motifs1_score": entry.get("Motifs1_score"),
                "motifs1_idx": entry.get("Motifs1_idx"),
                "motifs2_score": entry.get("Motifs2_score"),
                "motifs2_idx": entry.get("Motifs2_idx"),
                "transsites_score": entry.get("Transsites_score"),
                "cpgmodifier_score": entry.get("CpGModifier_score"),
                "spl8modifier_score": entry.get("Spl8Modifier_score"),
                "limiters": entry.get("Limiters"),
                "tsd5": None,
                "tsd3": None,
                "similarity_start": entry.get("similarity_start"),
                "similarity_end": entry.get("similarity_end")
            })

    return ltr_entries




def insert_ltrs(conn, ltr_list, herv_chain_id):
    """
    Inserts LTR (both soloLTRs and full LTRs) into the ltr table using dynamic SQL.
    
    :param conn: psycopg2 connection
    :param ltr_list: list of parsed LTR dicts
    :param herv_chain_id: int
    """
    with conn.cursor() as cur:
        for ltr_entry in ltr_list:
            data = ltr_entry.copy()
            data.pop("herv_chain_index", None)  # REMOVE herv_chain_key key not present in the DB
            data["herv_chain_id"] = herv_chain_id

            columns = list(data.keys())
            values = [data[col] for col in columns]

            query = sql.SQL("INSERT INTO ltr ({fields}) VALUES ({placeholders}) RETURNING id").format(
                fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
                placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
            )

            cur.execute(query, values)
            inserted_id = cur.fetchone()[0]           

        conn.commit()

def get_herv_chain_blocks(json_data: dict) -> list[dict]:
    """
    Returns the full list of chain blocks from the JSON.
    Each block contains nested subgenes, motifs, etc.
    """
    return json_data.get("pseuGID", [])

def extract_herv_chain_metadata(chain_block: dict) -> dict:
    """
    From a full chain block, extract only metadata fields needed for DB insertion.
    """
    return {
        "chain_level": chain_block["chain_level"],
        "chain_start_idx": chain_block["chain_start_idx"],
        "chain_end_idx": chain_block["chain_end_idx"],
        "retrovirus_type": chain_block["retrovirus_type"],
        "score": int(chain_block["score"]),
        "type_of_chain": chain_block["type_of_chain"],
        "integration_sites": chain_block.get("integration_sites"),
    }

def parse_herv_chains(json_data: dict) -> list[dict]:
    """
    Parses all HERV chains from the JSON data into a list of dicts for DB insertion.
    """
    chains = []

    for chain in json_data.get("pseuGID", []):
        chains.append({
            "chain_level": chain["chain_level"],
            "chain_start_idx": chain["chain_start_idx"],
            "chain_end_idx": chain["chain_end_idx"],
            "retrovirus_type": chain["retrovirus_type"],
            "score": int(chain["score"]),
            "type_of_chain": chain["type_of_chain"],
            "integration_sites": chain.get("integration_sites"),
        })

    return chains

def insert_herv_chain(conn, herv_chain_entry, run_metadata_pk):
    """
    Inserts a single HERV chain into the herv_chain table.

    Args:
        conn: psycopg2 connection object.
        herv_chain_entry (dict): Parsed data from JSON for a single HERV chain.
        run_metadata_pk (int): Foreign key reference to run_metadata table.

    Returns:
        int: ID of the inserted HERV chain.
    """
    # Merge the foreign key into the entry dictionary
    data = herv_chain_entry.copy()
    data['run_metadata_id'] = run_metadata_pk

    columns = list(data.keys())
    values = [data[col] for col in columns]

    query = sql.SQL("INSERT INTO herv_chain ({fields}) VALUES ({placeholders}) RETURNING id").format(
        fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
        placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
    )

    with conn.cursor() as cur:
        cur.execute(query, values)
        inserted_id = cur.fetchone()[0]
        conn.commit()
        return inserted_id

 
def parse_subgenes(json_data: dict) -> list[dict]:
    """
    Extracts all subgenes from all chains in the JSON.
    """
    subgenes = []
    for chain in json_data.get("pseuGID", []):
        for subgene in chain.get("subgenes", []):
            subgenes.append({
                "name": subgene.get("name"),
                "type": subgene.get("type"),
                "score": subgene.get("score"),
                "hotspot": subgene.get("hotspot")
            })
    return subgenes

def insert_subgenes(cursor, subgenes: list[dict], herv_chain_id: int):
    """
    Inserts subgenes associated with a given HERV chain ID into the database.
    """
    for subgene in subgenes:
        cursor.execute(
            """
            INSERT INTO subgenes (herv_chain_id, name, type, score, hotspot)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                herv_chain_id,
                subgene["name"],
                subgene["type"],
                subgene["score"],
                subgene["hotspot"]
            )
        )

def parse_domains(json_data):
    """
    Extracts domains from the nested JSON under each subgene in each pseuGID.
    
    Returns:
        List of dicts, where each dict represents a domain entry.
        The subgene_id must be assigned during insert, so this function leaves it as a placeholder (e.g., None).
    """
    domain_entries = []

    for chain in json_data.get("pseuGID", []):
        for subgene in chain.get("subgenes", []):
            for domain in subgene.get("domains", []):
                entry = {
                    "subgene_id": None,  # To be filled in when inserting
                    "idx": domain.get("idx"),
                    "type": domain["type"],
                    "origin": domain.get("origin"),
                    "score": domain["score"],
                    "hotspot": domain["hotspot"],
                    "frame": domain["frame"],
                    "pos_init": domain["pos_init"],
                    "pos_fin": domain["pos_fin"],
                    "match_input": domain["match_input"],
                    "reference_match": domain["reference_match"],
                    "n_bases": domain["n_bases"],
                }
                domain_entries.append(entry)

    return domain_entries

def parse_subgenes_and_domains(chain_block: dict) -> tuple[list[dict], list[dict]]:
    """
    Parses subgenes and domains from a single chain block.
    
    Returns:
        subgenes (list[dict]): Each subgene has a unique 'subgene_index' (within this block).
        domains (list[dict]): Each domain links to its parent subgene via 'subgene_index'.
    """
    subgenes = []
    domains = []
    subgene_counter = 0  # Local counter, resets for each chain_block

    for subgene in chain_block.get("subgenes", []):
        parsed_subgene = {
            "subgene_index": subgene_counter,
            "name": subgene.get("name"),
            "type": subgene.get("type"),
            "score": subgene.get("score"),
            "hotspot": subgene.get("hotspot"),
            # 'herv_chain_id' will be attached later during DB insertion
        }
        subgenes.append(parsed_subgene)

        for domain in subgene.get("domains", []):
            parsed_domain = {
                "subgene_index": subgene_counter,
                "idx": domain.get("idx"),
                "type": domain.get("type"),
                "origin": domain.get("origin"),
                "score": domain.get("score"),
                "hotspot": domain.get("hotspot"),
                "frame": domain.get("frame"),
                "pos_init": domain.get("pos_init"),
                "pos_fin": domain.get("pos_fin"),
                "match_input": domain.get("match_input"),
                "reference_match": domain.get("reference_match"),
                "n_bases": domain.get("n_bases"),
            }
            domains.append(parsed_domain)

        subgene_counter += 1

    return subgenes, domains


def insert_subgenes_domains(conn, subgenes: list[dict], domains: list[dict], herv_chain_id: int):
    """
    Inserts subgenes and domains into the database.
    
    Args:
        conn: psycopg2 connection object
        subgenes: List of parsed subgenes (from `parse_subgenes_and_domains`)
        domains: List of parsed domains (from `parse_subgenes_and_domains`)
        herv_chain_id: The foreign key to be added to subgenes
    """
    subgene_index_to_id = {}

    with conn.cursor() as cur:
        # Insert subgenes
        for subgene in subgenes:
            subgene_data = subgene.copy()
            subgene_data['herv_chain_id'] = herv_chain_id
            subgene_index = subgene_data.pop('subgene_index')  # Remove pseudo index
            subgene_data.pop('chain_index', None)


            columns = list(subgene_data.keys())
            values = [subgene_data[col] for col in columns]

            insert_query = sql.SQL("""
                INSERT INTO subgenes ({fields}) VALUES ({placeholders}) RETURNING id
            """).format(
                fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
                placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
            )

            cur.execute(insert_query, values)
            subgene_db_id = cur.fetchone()[0]

            # Map pseudo index to real DB ID
            subgene_index_to_id[subgene_index] = subgene_db_id

        # Insert domains
        for domain in domains:
            domain_data = domain.copy()
            subgene_index = domain_data.pop('subgene_index')  # Get pseudo index
            domain_data['subgene_id'] = subgene_index_to_id[subgene_index]

            columns = list(domain_data.keys())
            values = [domain_data[col] for col in columns]

            insert_query = sql.SQL("""
                INSERT INTO domains ({fields}) VALUES ({placeholders})
            """).format(
                fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
                placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
            )

            cur.execute(insert_query, values)

        conn.commit()



def parse_motifs(chain_block: dict) -> list[dict]:
    """
    Parses motifs of various types from a single chain block.
    Returns a flat list of motif dicts.
    """
    motif_entries = []
    motif_types = ['Slippery', 'PseudoKnot', 'SpliceAcceptor', 'SpliceDonor']

    for motif_type in motif_types:
        key = f"{motif_type}_motifs"
        for motif in chain_block.get(key, []):
            motif_entries.append({
                "type": motif_type,
                "pos_init": motif.get("pos_init"),
                "pos_end": motif.get("pos_end"),
                "score": motif.get("score")
            })

    return motif_entries




def insert_motifs(conn, motifs: list[dict], herv_chain_id: int):
    """
    Insert multiple motifs dynamically into the motifs table.

    Args:
        conn: psycopg2 connection object.
        motifs: list of motif dicts, each dict has motif data (keys match DB columns except herv_chain_id)
        herv_chain_id: foreign key to link motif to a herv_chain

    """

    with conn.cursor() as cur:
        for motif in motifs:
            # Copy motif dict and add foreign key
            data = motif.copy()
            data['herv_chain_id'] = herv_chain_id

            columns = list(data.keys())
            values = [data[col] for col in columns]

            query = sql.SQL("INSERT INTO motifs ({fields}) VALUES ({placeholders})").format(
                fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
                placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
            )

            cur.execute(query, values)

    conn.commit()


def insert_ltrs_of_hervchain(conn, ltr_chain_links: list[dict]):
    """
    Insert links between LTRs and HERV chains.

    Each item in ltr_chain_links should be a dict with:
        - herv_chain_id: int
        - ltr_id: int
    """
    for link in ltr_chain_links:
        conn.execute(
            """
            INSERT INTO ltrs_of_hervchain (herv_chain_id, ltr_id)
            VALUES (%s, %s)
            """,
            (link["herv_chain_id"], link["ltr_id"])
        )

def parse_and_load_retroctector(data,conn):
    # 1 - Parse and Insert run_metadata

    run_metadata = parse_run_metadata(data) 
    run_metadata_pk_id = insert_run_metadata(conn,run_metadata)

    # 2 - Get all chain blocks Parse all herv chain 
    chain_blocks = get_herv_chain_blocks(data)        

    for chain_block  in chain_blocks: # supports the option for multiple chains in a sequence 
        
        # 3 - Insert HERV chain and get its DB ID  
        chain_metadata = extract_herv_chain_metadata(chain_block)            
        herv_chain_id  = insert_herv_chain(conn, chain_metadata, run_metadata_pk_id)

        # 4. Parse subgenes and domains

        subgenes, domains = parse_subgenes_and_domains(chain_block) # pass chain data only 
        insert_subgenes_domains(conn,subgenes,domains,herv_chain_id )
        
        # 5-  Parse motifs 
            
        motifs = parse_motifs(chain_block) 
        insert_motifs(conn, motifs, herv_chain_id )

        # 6 -  LTR and SoloLTR 

        ltr = parse_ltrs(data)
        insert_ltrs(conn,ltr,herv_chain_id )  

def parse_args():
    parser = argparse.ArgumentParser(description="Parse and insert Retrotector JSON into the database.")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input JSON file"
    )
    return parser.parse_args()


def main():
    conn_params = {
        "host": "",
        "database": "",
        "user": "",
        "password": "",
        "port": ,
    }

    try:
        args = parse_args()
        print(f"Loading: {args.input}") 

        conn = psycopg2.connect(**conn_params)
        print("Connected to DB")

        data = load_retrotector_json(args.input)
        parse_and_load_retroctector(data, conn)

    except Exception as e:
        print(f"Error: {e}")

    finally:
        if conn:
            conn.close()
            print("DB connection closed")

if __name__ == "__main__":
    main()

