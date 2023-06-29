-- Create table `document`
CREATE TABLE IF NOT EXISTS documents
(
    -- Python visible fields
    id                BIGINT AUTO_INCREMENT PRIMARY KEY,
    job_id            BIGINT,
    html              LONGTEXT,
    title             TEXT,
    body              LONGTEXT,
    links             LONGTEXT DEFAULT ('[]'),
    title_tokens      LONGTEXT DEFAULT ('[]'),
    body_tokens       LONGTEXT DEFAULT ('[]'),
    body_tfidf        BLOB,
    relevant          BOOLEAN  DEFAULT TRUE,
    -- Other fields
    created_date      DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_time_changed DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES jobs (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = RocksDB;