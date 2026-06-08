from pathlib import Path
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_jsons
from src.run_data_profile import run_data_profile

SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")
SILVER_DIR = Path("data/2_silver")
GOLD_DIR = Path("data/3_gold")
DB_NAME = "jobs.db"

def run_profiler():
    db_path = GOLD_DIR/DB_NAME
    run_data_profile(db_path)

def run_gold():
    load_all_jsons(SILVER_DIR, GOLD_DIR)

def run_silver():
    process_all_html(BRONZE_DIR, SILVER_DIR)

def run_bronze():
    ingest_all_mhtml(SOURCE_DIR, BRONZE_DIR)

def main():
	# ORCHESTRATION TO BE IMPLEMENTED HERE
