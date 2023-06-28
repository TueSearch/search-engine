CREATE TABLE IF NOT EXISTS document
(
    id                       BIGINT AUTO_INCREMENT PRIMARY KEY,
    url                      VARCHAR(256) UNIQUE NOT NULL,
    server                   TEXT,
    title                    TEXT,
    body                     LONGTEXT,
    title_tokens             TEXT,
    body_tokens              LONGTEXT,
    all_harvested_links      TEXT,
    relevant_links           TEXT,
    body_global_tfidf_vector BLOB,
    relevant                 BOOLEAN DEFAULT TRUE
) ENGINE = RocksDB;