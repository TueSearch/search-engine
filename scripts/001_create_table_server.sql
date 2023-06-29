-- Create table `server`
CREATE TABLE IF NOT EXISTS servers
(
    -- Python visible fields
    id                BIGINT AUTO_INCREMENT PRIMARY KEY,
    name              VARCHAR(128) UNIQUE NOT NULL,
    is_black_list     BOOLEAN  DEFAULT 0,
    -- Other fields
    created_date      DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_time_changed DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE = RocksDB;
