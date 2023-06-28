-- Create table `document`
CREATE TABLE IF NOT EXISTS document
(
    id                       BIGINT AUTO_INCREMENT PRIMARY KEY,
    job_id                   BIGINT,
    title                    TEXT,
    body                     LONGTEXT,
    title_tokens             LONGTEXT,
    body_tokens              LONGTEXT,
    all_harvested_links      LONGTEXT,
    relevant_links           LONGTEXT,
    body_global_tfidf_vector BLOB,
    relevant                 BOOLEAN DEFAULT TRUE,
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES job(id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = RocksDB;