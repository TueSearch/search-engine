-- Create table `job`
CREATE TABLE IF NOT EXISTS jobs
(
    -- Python visible fields
    id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
    url                VARCHAR(750) UNIQUE    NOT NULL,
    server_id          BIGINT,
    priority           INT      DEFAULT 0     NOT NULL,
    being_crawled      BOOLEAN  DEFAULT FALSE,
    done               BOOLEAN  DEFAULT FALSE NOT NULL,
    success            BOOLEAN  DEFAULT NULL,
    created_date       DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_time_changed DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    -- Other fields
    CHECK ((done AND success IS NOT NULL) OR (NOT done AND success IS NULL)),
    CHECK ((being_crawled = FALSE AND done = FALSE OR success IS NULL) OR
           (being_crawled = TRUE AND done = FALSE AND success IS NULL) OR
           (being_crawled = FALSE AND done = TRUE OR success IS NOT NULL)),
    FOREIGN KEY (server_id) REFERENCES servers (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = RocksDB;