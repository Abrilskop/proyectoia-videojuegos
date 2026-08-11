import sqlite3
import time


class Store:
    """Persistencia local (SQLite): reputación por jugador y auditoría de decisiones."""

    def __init__(self, db_path):
        self.conn = sqlite3.connect(str(db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS players(
                guild_id   TEXT NOT NULL,
                user_id    TEXT NOT NULL,
                reputation REAL NOT NULL DEFAULT 0.5,
                messages   INTEGER NOT NULL DEFAULT 0,
                updated_at REAL NOT NULL,
                PRIMARY KEY (guild_id, user_id)
            );
            CREATE TABLE IF NOT EXISTS decisions(
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id   TEXT NOT NULL,
                user_id    TEXT NOT NULL,
                channel_id TEXT NOT NULL DEFAULT '',
                message    TEXT NOT NULL,
                decision   TEXT NOT NULL,
                prob       REAL,
                action     TEXT NOT NULL,
                created_at REAL NOT NULL
            );
            """
        )
        self.conn.commit()

    def get_reputation(self, guild_id, user_id):
        row = self.conn.execute(
            "SELECT reputation FROM players WHERE guild_id=? AND user_id=?",
            (guild_id, user_id),
        ).fetchone()
        return row["reputation"] if row else 0.5

    def adjust_reputation(self, guild_id, user_id, delta):
        current = self.get_reputation(guild_id, user_id)
        new_rep = max(0.0, min(1.0, current + delta))
        self.conn.execute(
            """
            INSERT INTO players(guild_id, user_id, reputation, messages, updated_at)
            VALUES (?, ?, ?, 1, ?)
            ON CONFLICT(guild_id, user_id) DO UPDATE SET
                reputation = excluded.reputation,
                messages = players.messages + 1,
                updated_at = excluded.updated_at
            """,
            (guild_id, user_id, new_rep, time.time()),
        )
        self.conn.commit()
        return new_rep

    def add_decision(self, guild_id, user_id, channel_id, message, decision_label, prob, action):
        self.conn.execute(
            """
            INSERT INTO decisions(guild_id, user_id, channel_id, message, decision, prob, action, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (guild_id, user_id, channel_id, message, decision_label, prob, action, time.time()),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
