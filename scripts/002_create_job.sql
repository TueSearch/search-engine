CREATE TABLE IF NOT EXISTS job
(
    id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    url      VARCHAR(256) UNIQUE NOT NULL,
    server   TEXT,
    priority INT     DEFAULT 0 NOT NULL,
    done     BOOLEAN DEFAULT FALSE NOT NULL,
    success  BOOLEAN DEFAULT NULL,
    CHECK ((done AND success IS NOT NULL) OR (NOT done AND success IS NULL))
);