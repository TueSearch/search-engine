-- Create table `job`
CREATE TABLE IF NOT EXISTS jobs
(
    -- Python visible fields
    id                      BIGINT AUTO_INCREMENT PRIMARY KEY,
    url                     VARCHAR(750) UNIQUE    NOT NULL,
    server_id               BIGINT,
    parent_id               BIGINT   DEFAULT NULL,
    anchor_text             LONGTEXT DEFAULT (''),
    anchor_text_tokens      LONGTEXT DEFAULT ('[]'),
    surrounding_text        LONGTEXT DEFAULT (''),
    surrounding_text_tokens LONGTEXT DEFAULT ('[]'),
    title_text              LONGTEXT DEFAULT (''),
    title_text_tokens       LONGTEXT DEFAULT ('[]'),
    priority                FLOAT    DEFAULT 0.0   NOT NULL,
    done                    BOOLEAN  DEFAULT FALSE NOT NULL,
    success                 BOOLEAN  DEFAULT NULL,
    -- Checks
    CHECK ((done AND success IS NOT NULL) OR (NOT done AND success IS NULL)),
    CHECK ((done = FALSE AND success IS NULL) OR
           (done = TRUE AND success IS NOT NULL)),
    -- Foreign keys
    FOREIGN KEY (server_id) REFERENCES servers (id)
) ENGINE = RocksDB;