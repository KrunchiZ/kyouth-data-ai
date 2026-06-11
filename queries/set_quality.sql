UPDATE jobs
SET quality = 'LOW'
WHERE 
    LENGTH(description) < 100
    OR job_title IS NULL 
    OR company IS NULL 
    OR description IS NULL;

UPDATE jobs
SET quality = 'HIGH'
WHERE
    QUALITY IS NULL;