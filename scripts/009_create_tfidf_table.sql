CREATE TABLE IF NOT EXISTS tfidfs
(
    id                BIGINT PRIMARY KEY,
    title             BLOB,
    meta_description  BLOB,
    meta_keywords     BLOB,
    meta_author       BLOB,
    h1                BLOB,
    h2                BLOB,
    h3                BLOB,
    h4                BLOB,
    h5                BLOB,
    h6                BLOB,
    body              BLOB,
    -- Other fields
    created_date      DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_time_changed DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    -- Foreign key
    FOREIGN KEY (id) REFERENCES documents (id) ON DELETE CASCADE ON UPDATE CASCADE
);