CREATE TABLE IF NOT EXISTS jobs_quarantine AS
SELECT * FROM jobs
WHERE 1=0;

INSERT OR IGNORE INTO jobs_quarantine
SELECT * FROM jobs
WHERE quality = 'LOW';

DELETE FROM jobs
WHERE quality = 'LOW';