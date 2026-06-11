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
    stats = get_data_profile_stats(db_path)
    print_data_profile_report(stats)


def input_db_isValid(db_path):
    if not os.path.isfile(db_path):
        logging.error(f"Database not found: {db_path}")
        return False
    if not os.access(db_path, os.R_OK):
        logging.error(f"Database not readable: {db_path}")
        return False
    return True


def get_data_profile_stats(db_path):
    stats = {
        "total_records":0,
        "null_titles": 0,
        "null_companies": 0,
        "null_descriptions": 0,
        "avg_length": 0.0,
        "shortest_desc": (None, None, None),
        "longest_desc": (None, None, None)
    }
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(COUNT_JOBS_QUERY.read_text(encoding="utf-8"))
            stats["total_records"] = cursor.fetchone()[0]
            cursor.execute(COUNT_NULL_TITLES_QUERY.read_text(encoding="utf-8"))
            stats["null_titles"] = cursor.fetchone()[0]
            cursor.execute(COUNT_NULL_COMPANIES_QUERY.read_text(encoding="utf-8"))
            stats["null_companies"] = cursor.fetchone()[0]
            cursor.execute(COUNT_NULL_DESCRIPTIONS_QUERY.read_text(encoding="utf-8"))
            stats["null_descriptions"] = cursor.fetchone()[0]
            cursor.execute(COUNT_AVG_DESC_LENGTH_QUERY.read_text(encoding="utf-8"))
            stats["avg_length"] = cursor.fetchone()[0]
            cursor.execute(COUNT_SHORTEST_DESC_QUERY.read_text(encoding="utf-8"))
            stats["shortest_desc"] = cursor.fetchone()
            cursor.execute(COUNT_LONGEST_DESC_QUERY.read_text(encoding="utf-8"))
            stats["longest_desc"] = cursor.fetchone()
    except sqlite3.Error as code:
        logging.error(f"Profile Error: {code}")
    return stats


def print_data_profile_report(stats):
    print(
        f"--- 🔍 DATA QUALITY REPORT ---"
        f"\n📊 Total Records: {stats['total_records']}"
        f"\n❓ Missing Values -> job_title: {stats['null_titles']}, "
        f"company: {stats['null_companies']}, "
        f"description: {stats['null_descriptions']}"
        f"\n📝 Avg Description Length: {stats['avg_length']:.2f} chars"
        f"\n⚠️ Shortest Description: {stats['shortest_desc'][2]} chars"
        f"\n    ↳ source_id: {stats['shortest_desc'][0]} | "
        f"job_title: {stats['shortest_desc'][1]}"
        f"\n🚨 Longest Description: {stats['longest_desc'][2]} chars"
        f"\n    ↳ source_id: {stats['longest_desc'][0]} | "
        f"job_title: {stats['longest_desc'][1]}"
    )