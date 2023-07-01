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
    -- Foreign key
    FOREIGN KEY (id) REFERENCES documents (id) ON DELETE CASCADE ON UPDATE CASCADE
);