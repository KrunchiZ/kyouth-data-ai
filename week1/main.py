from pathlib import Path
from src.ingestor import ingest_all_mhtml
from src.processor import process_all_html
from src.loader import load_all_jsons
from src.profiler import run_data_profile
import sys

SOURCE_DIR = Path("data/0_source")
BRONZE_DIR = Path("data/1_bronze")
SILVER_DIR = Path("data/2_silver")
GOLD_DIR = Path("data/3_gold")
DB_NAME = "jobs.db"

def run_profiler():
    print("📊 Profiling: ...")
    run_data_profile(GOLD_DIR / DB_NAME)

def run_gold():
    print("🥇 Gold: ...")
    load_all_jsons(SILVER_DIR, GOLD_DIR)

def run_silver():
    print("🥈 Silver: ...")
    process_all_html(BRONZE_DIR, SILVER_DIR)

def run_bronze():
    print("🥉 Bronze: ...")
    ingest_all_mhtml(SOURCE_DIR, BRONZE_DIR)

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <command>")
        return
    match sys.argv[1]:
        case "ingest":
            run_bronze()
        case "process":
            run_silver()
        case "load":
            run_gold()
        case "profile":
            run_profiler()
        case _: # default case
            print(f"Unknown command: {sys.argv[1]}")
            
if __name__ == "__main__":
    main()
