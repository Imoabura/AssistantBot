DROP TABLE IF EXISTS user;

CREATE TABLE IF NOT EXISTS user (
    UserID integer PRIMARY KEY,
    UseDMs integer DEFAULT 0,
    UserTimeZone integer DEFAULT 0
);