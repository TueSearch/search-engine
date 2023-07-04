ALTER TABLE tfidfs
    MODIFY COLUMN title LONGBLOB,
    MODIFY COLUMN meta_description LONGBLOB,
    MODIFY COLUMN meta_keywords LONGBLOB,
    MODIFY COLUMN meta_author LONGBLOB,
    MODIFY COLUMN h1 LONGBLOB,
    MODIFY COLUMN h2 LONGBLOB,
    MODIFY COLUMN h3 LONGBLOB,
    MODIFY COLUMN h4 LONGBLOB,
    MODIFY COLUMN h5 LONGBLOB,
    MODIFY COLUMN h6 LONGBLOB,
    MODIFY COLUMN body LONGBLOB;