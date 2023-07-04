-- Create table `server`
CREATE TABLE IF NOT EXISTS servers
(
    -- Python visible fields
    id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
    name               VARCHAR(128) UNIQUE NOT NULL,
    is_black_list      BOOLEAN  DEFAULT 0,
    page_rank          FLOAT    DEFAULT 0,
    total_jobs         BIGINT   DEFAULT 0,
    total_done_jobs    BIGINT   DEFAULT 0,
    success_jobs       BIGINT   DEFAULT 0,
    relevant_documents BIGINT   DEFAULT 0,
    -- Python invisible fields
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL,
    -- Check constraints
    CHECK (total_done_jobs <= total_jobs),
    CHECK (success_jobs <= total_done_jobs),
    CHECK (relevant_documents <= success_jobs)
) ENGINE = RocksDB;
