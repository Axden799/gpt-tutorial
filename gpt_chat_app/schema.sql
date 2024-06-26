DROP TABLE IF EXISTS chat;

CREATE TABLE chat (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  message TEXT NOT NULL,
  reply INTEGER NOT NULL DEFAULT 0,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
