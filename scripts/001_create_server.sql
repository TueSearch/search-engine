-- Create table `server`
CREATE TABLE IF NOT EXISTS server
(
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(128) UNIQUE NOT NULL,
    is_black_list BOOLEAN  DEFAULT 0,
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE = RocksDB;
