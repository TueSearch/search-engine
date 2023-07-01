-- Create table `document`
CREATE TABLE IF NOT EXISTS documents
(
    -- Python visible fields
    id                      BIGINT AUTO_INCREMENT PRIMARY KEY,
    job_id                  BIGINT,
    -- Raw data field
    html                    LONGTEXT DEFAULT (''),
    -- Raw text fields
    title                   LONGTEXT DEFAULT (''),
    meta_description        LONGTEXT DEFAULT (''),
    meta_keywords           LONGTEXT DEFAULT (''),
    meta_author             LONGTEXT DEFAULT (''),
    h1                      LONGTEXT DEFAULT (''),
    h2                      LONGTEXT DEFAULT (''),
    h3                      LONGTEXT DEFAULT (''),
    h4                      LONGTEXT DEFAULT (''),
    h5                      LONGTEXT DEFAULT (''),
    h6                      LONGTEXT DEFAULT (''),
    body                    LONGTEXT DEFAULT (''),
    -- Processed text fields
    title_tokens            LONGTEXT DEFAULT ('[]'),
    meta_description_tokens LONGTEXT DEFAULT ('[]'),
    meta_keywords_tokens    LONGTEXT DEFAULT ('[]'),
    meta_author_tokens      LONGTEXT DEFAULT ('[]'),
    h1_tokens               LONGTEXT DEFAULT ('[]'),
    h2_tokens               LONGTEXT DEFAULT ('[]'),
    h3_tokens               LONGTEXT DEFAULT ('[]'),
    h4_tokens               LONGTEXT DEFAULT ('[]'),
    h5_tokens               LONGTEXT DEFAULT ('[]'),
    h6_tokens               LONGTEXT DEFAULT ('[]'),
    body_tokens             LONGTEXT DEFAULT ('[]'),
    -- Classification
    relevant                BOOLEAN  DEFAULT TRUE
) ENGINE = RocksDB;