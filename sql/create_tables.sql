-- Schema declaration matching the existing database's urls table.
-- This file is provided as a schema reference; the populated database is not modified.
CREATE TABLE IF NOT EXISTS urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Unique integer row identifier.
    url TEXT NOT NULL UNIQUE              -- Stored URL string; UNIQUE prevents duplicates.
);
