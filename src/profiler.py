import os
import sqlite3
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


QUERY_DIR = Path("queries")
COUNT_JOBS_QUERY = QUERY_DIR / "count_jobs.sql"
COUNT_NULL_TITLES_QUERY = QUERY_DIR / "count_null_titles.sql"
COUNT_NULL_COMPANIES_QUERY = QUERY_DIR / "count_null_companies.sql"
COUNT_NULL_DESCRIPTIONS_QUERY = QUERY_DIR / "count_null_descriptions.sql"
COUNT_AVG_DESC_LENGTH_QUERY = QUERY_DIR / "count_avg_desc_length.sql"
COUNT_SHORTEST_DESC_QUERY = QUERY_DIR / "count_shortest_desc.sql"
COUNT_LONGEST_DESC_QUERY = QUERY_DIR / "count_longest_desc.sql"


def run_data_profile(db_path):
    if not input_db_isValid(db_path):
        return

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(COUNT_JOBS_QUERY.read_text(encoding="utf-8"))
        total_records = cursor.fetchone()[0]
        cursor.execute(COUNT_NULL_TITLES_QUERY.read_text(encoding="utf-8"))
        null_titles = cursor.fetchone()[0]
        cursor.execute(COUNT_NULL_COMPANIES_QUERY.read_text(encoding="utf-8"))
        null_companies = cursor.fetchone()[0]
        cursor.execute(COUNT_NULL_DESCRIPTIONS_QUERY.read_text(encoding="utf-8"))
        null_descriptions = cursor.fetchone()[0]
        cursor.execute(COUNT_AVG_DESC_LENGTH_QUERY.read_text(encoding="utf-8"))
        avg_length = cursor.fetchone()[0]
        cursor.execute(COUNT_SHORTEST_DESC_QUERY.read_text(encoding="utf-8"))
        shortest = cursor.fetchone()
        cursor.execute(COUNT_LONGEST_DESC_QUERY.read_text(encoding="utf-8"))
        longest = cursor.fetchone()

    print(
        f"--- 🔍 DATA QUALITY REPORT ---"
        f"\n📊 Total Records: {total_records}"
        f"\n❓ Missing Values -> job_title: {null_titles}, "
        f"company: {null_companies}, description: {null_descriptions}"
        f"\n📝 Avg Description Length: {avg_length:.2f} chars"
        f"\n⚠️ Shortest Description: {shortest[2]} chars"
        f"\n    ↳ source_id: {shortest[0]} | job_title: {shortest[1]}"
        f"\n🚨 Longest Description: {longest[2]} chars"
        f"\n    ↳ source_id: {longest[0]} | job_title: {longest[1]}"
    )

def input_db_isValid(db_path):
    if not os.path.isfile(db_path):
        logging.error(f"Database not found: {db_path}")
        return False
    if not os.access(db_path, os.R_OK):
        logging.error(f"Database not readable: {db_path}")
        return False
    return True