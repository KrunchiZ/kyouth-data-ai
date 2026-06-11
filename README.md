# Resume Skill Gap Analyzer — Data Pipeline (Week 1)

## Project Description

This project is **Week 1** of a three-week Resume Skill Gap Analyzer. The goal of the analyzer is to identify skill gaps between a candidate's resume and the current job market for Data, AI, and Python roles.

Week 1 focuses entirely on the **data engineering foundation**: a robust, local ETL pipeline (Extract, Transform, Load) that extracts raw job listing data from `.mhtml` files, cleans and structures it, and stores it in a relational SQLite database (`jobs.db`) — the data deliverable that will be integrated in Week 3.

```
[SOURCE] -> [EXTRACT] -> [CLEAN/PROCESS] -> [LOAD] -> [DATABASE]
```

The pipeline follows a simplified **Medallion Architecture**, progressing data through four ordered layers:

| Layer | Folder | Description |
|-------|--------|-------------|
| Source | `0_source/` | Original `.mhtml` files as downloaded |
| Bronze | `1_bronze/` | Raw HTML extracted from `.mhtml` |
| Silver | `2_silver/` | Cleaned, structured JSON records |
| Gold | `3_gold/` | Final SQLite database (`jobs.db`) |

The final `jobs.db` contains a single table with the following schema:

```
source_id | job_title | company | description | tech_stack | quality | content_hash
```

A central orchestrator (`main.py`) wires all stages together and exposes a CLI with granular or end-to-end execution modes.
<br/><br/>

## Setup Instructions

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | **3.14.x** |
| [uv](https://docs.astral.sh/uv/getting-started/installation/) | latest |

> All Python dependencies are pinned to exact versions in `pyproject.toml`. Do not manually upgrade packages.

> Install `SQLite3 Editor` extension on `VS Code` for better database reading.

---

### 1. Clone the repository

```bash
git clone [github_repo_link] [folder_name]
cd [folder_name]
```

---

### 2. Install `uv` (if not already installed)

**macOS / Linux (Ubuntu / Debian):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Linux (Fedora / Red Hat):**
```bash
sudo dnf install uv -y
```

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
After installation, restart your terminal and verify:

```bash
uv --version
```

---

### 3. Install the correct Python version

`uv` can manage Python versions directly. Run:

```bash
uv python install 3.14
```

---

### 4. Create the virtual environment and install dependencies

```bash
uv sync
```

This reads `pyproject.toml`, pins all exact versions, and creates a `.venv` directory at the project root. You only need to run this once (or again after any dependency changes).

---

### 5. Activate the virtual environment (optional)

`uv run` (used in all commands below) automatically uses the `.venv` without manual activation. However, if you need to activate it for other tooling:

**macOS / Linux:**
```bash
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
.venv\Scripts\activate.bat
```

**To deactivate when done:**
```bash
deactivate
```

<br/>

## Usage

All commands use `uv run` so they work consistently across platforms without needing manual venv activation.

### Run the full pipeline (recommended)

```bash
uv run main.py all
```

Executes all stages in sequence: ingest → process → load → profile.

### Run individual stages

```bash
# Stage 1 — Extract raw HTML from .mhtml source files into 1_bronze/
uv run main.py ingest

# Stage 2 — Clean and parse HTML into structured JSON in 2_silver/
uv run main.py process

# Stage 3 — Load cleaned JSON records into SQLite in 3_gold/
uv run main.py load

# Stage 4 — Performs data profiling on the SQLite database/
uv run main.py profile
```

### Expected input

Place raw `.mhtml` files into the `0_source/` directory before running:

```
data/
    0_source/
        *.mhtml         ← raw webpage archive files (one per source)
```

### Expected output

After a successful `all` run:

```
data/
    1_bronze/
        *.html          ← raw .html files (one per source)
    2_silver/
        *.json          ← cleaned .json files (one per source)
    3_gold/
        jobs.db         ← SQLite database with deduplicated job records
```

>You can inspect the final database with `SQLite3 editor` on `VS Code`.

### Code formatting

All Python code is formatted with `ruff` (version `0.15.*`):

```bash
uv run ruff format .
uv run ruff check .
```
<br/>

## Technical Reflections

### Day 1: The Extractor (Medallion & Lakehouses)

**Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?**

- **Answer**: Keeping raw HTML in the Bronze layer preserves the ground truth of what was originally captured. If a parsing bug is discovered later — for example, a regex that misread salary ranges — you can re-run only the transformation stage without re-scraping or re-downloading anything. This makes the entire pipeline **re-entrant and recoverable**: the source of truth never gets overwritten. In a production Data Lake context, this mirrors the principle of landing raw files in object storage (e.g., S3) before any transformation touches them, so audits, backtracking, and schema migrations are always possible without data loss.

### Day 2: Treatment Plant (ETL vs ELT & Scale)

**Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?**

- **Answer**: Cloud warehouses like BigQuery and Snowflake have massive, elastic compute built in — it's cheaper and faster to land raw data immediately and transform it later using the warehouse's own SQL engine at scale, rather than pre-cleaning it on a single machine before loading. Storing raw data first also means the warehouse always retains the original copy, enabling schema evolution without re-ingestion. Sequential file processing (our local pipeline) becomes a bottleneck as volume grows: one slow or malformed file blocks everything behind it. Distributed systems like Apache Spark partition data across many workers so thousands of files are processed in parallel — a single bad record fails only its own partition, not the entire job, dramatically improving both throughput and fault tolerance.

### Day 3: The Blueprint & The Vault (Storage & Contracts)

**What should happen if an important field like `job_title` disappears? Why fail early instead of silently inserting `nulls` into DB? How does `INSERT OR IGNORE` help prevent duplicate records?**

- **Answer**: If a critical field like `job_title` is missing, the pipeline should **raise an exception and halt** rather than insert a null. Silent nulls are dangerous because they propagate invisibly downstream — dashboards show blank rows, aggregations become meaningless, and the root cause (a changed HTML structure or a broken parser) goes undetected until a stakeholder notices wrong numbers. Failing early at the contract boundary means the problem surfaces immediately, close to its source, where it's easiest to fix. `INSERT OR IGNORE` complements this by making loads **idempotent**: re-running the pipeline after a partial failure won't create duplicate rows — records already present (matched by their unique `source_id`) are silently skipped, keeping the database consistent without any manual cleanup.

### Day 4: The QA Inspector & Orchestrator (Orchestration & DAGs)

**What happens if `processor.py` crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?**

- **Answer**: If `processor.py` crashes mid-run, our manual orchestrator has no built-in mechanism to know which files succeeded and which didn't — a naive retry would either reprocess everything from scratch or leave the pipeline in an unknown partial state. Production orchestrators like Apache Airflow model pipelines as **DAGs (Directed Acyclic Graphs)**, where each task tracks its own success/failure state persistently. A crash in one task leaves all prior tasks marked complete; on retry, only the failed task and its dependents re-execute. Airflow also provides scheduling, alerting, SLA monitoring, and backfill capabilities — concerns that would require significant custom engineering to replicate in a plain Python script, and that would still lack the operational visibility of a proper orchestration UI.
