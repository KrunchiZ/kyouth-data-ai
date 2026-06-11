CREATE TABLE IF NOT EXISTS jobs_quarantine AS
SELECT * FROM jobs
WHERE 1=0;

INSERT OR REPLACE INTO jobs_quarantine
SELECT * FROM jobs
WHERE quality = "LOW"
AND source_id NOT IN (
    SELECT source_id FROM jobs_quarantine
    WHERE content_hash = jobs.content_hash
);