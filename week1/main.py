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
    run_data_profile(GOLD_DIR / DB_NAME)

def run_gold():
    load_all_jsons(SILVER_DIR, GOLD_DIR)

def run_silver():
    process_all_html(BRONZE_DIR, SILVER_DIR)

def run_bronze():
    ingest_all_mhtml(SOURCE_DIR, BRONZE_DIR)

def main():
    print("Starting ETL pipeline...")
    stages = [
        ("[1/4] Bronze: ingesting source files...",          run_bronze),
        ("[2/4] Silver: cleaning and processing HTML...",    run_silver),
        ("[3/4] Gold: loading structured data...",           run_gold),
        ("[4/4] Profiling final database...",                run_profiler),
    ]
    for message, stage in stages:
        print(message)
        stage()
    print("Pipeline complete.")

if __name__ == "__main__":
    main()
