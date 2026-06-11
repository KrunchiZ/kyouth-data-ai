import os
import sqlite3
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def run_data_profile(db_path):
    # Data Profiling: Write scripts to check for data quality post-load.
    # Here are the following metrics to audit:
    # - Total records
    # - Null values in `job_title`, `company`, or `description`
    # - Average `description` length
    # - Shortest `description` length, along with its `source_id` and `job_title`
    # - Longest `description` length, along with its `source_id` and `job_title`
    #
    # Example Output:
    # --- 🔍 DATA QUALITY REPORT ---
    # 📈 Total Records: 67
    # ❓ Missing Values -> job_title: 0, company: 0, description: 0
    # 📝 Avg Description Length: 1740 chars
    # ⚠️ Shortest Description: 53 chars
    #    ↳ source_id: <SOURCE_ID> | job_title: <JOB_TITLE>
    # 🚨 Longest Description: 2854 chars
    #    ↳ source_id: <SOURCE_ID> | job_title: <JOB_TITLE>
    if not input_db_isValid(db_path):
        return

def input_db_isValid(db_path):
    if not os.path.isfile(db_path):
        logging.error(f"Database not found: {db_path}")
        return False
    if not os.access(db_path, os.R_OK):
        logging.error(f"Database not readable: {db_path}")
        return False
    return True