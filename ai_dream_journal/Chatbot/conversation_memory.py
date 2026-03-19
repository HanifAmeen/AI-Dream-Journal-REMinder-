import sqlite3
import uuid


class ConversationMemory:
    def __init__(self, db_path="dreams.db"):
        self.db_path = db_path
        self._init_db()

    # ----------------------------------
    # Create tables if they don't exist
    # ----------------------------------
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            user_id TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()

    # ----------------------------------
    # Start new chat
    # ----------------------------------
    def start_new_conversation(self, user_id):
        conversation_id = str(uuid.uuid4())

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO conversations (id, user_id) VALUES (?, ?)",
            (conversation_id, user_id)
        )

        conn.commit()
        conn.close()

        return conversation_id

    # ----------------------------------
    # Save message
    # ----------------------------------
    def add_message(self, conversation_id, role, content, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO messages (conversation_id, role, content, user_id)
            VALUES (?, ?, ?, ?)
            """,
            (conversation_id, role, content, user_id)
        )

        conn.commit()
        conn.close()

    # ----------------------------------
    # Return formatted history for LLM
    # ----------------------------------
    def get_history(self, conversation_id, user_id, limit=10):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ? AND user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (conversation_id, user_id, limit)
        )

        rows = cur.fetchall()
        conn.close()

        rows.reverse()

        formatted = []
        for role, content in rows:
            if role == "user":
                formatted.append(f"User: {content}")
            else:
                formatted.append(f"Spectre: {content}")

        return "\n".join(formatted)

    # ----------------------------------
    # Return messages for frontend
    # ----------------------------------
    def get_messages(self, conversation_id, user_id):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute(
            """
            SELECT role, content
            FROM messages
            WHERE conversation_id = ? AND user_id = ?
            ORDER BY id
            """,
            (conversation_id, user_id)
        )

        rows = cur.fetchall()
        conn.close()

        messages = []

        for role, content in rows:
            messages.append({
                "role": role,
                "content": content
            })

        return messages
