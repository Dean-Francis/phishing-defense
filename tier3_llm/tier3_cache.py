import sqlite3
import hashlib
import json
import time
import os
from typing import Optional, Dict, Any


class LLMCache:
    """SQLite-based cache for LLM responses to reduce API calls and costs.

    Features:
    - MD5 hash keys for normalized URL/text inputs
    - Configurable TTL (time-to-live) for cache entries
    - Thread-safe SQLite operations
    """

    def __init__(self, db_path: str = 'tier3_llm/cache/llm_cache.db', ttl_hours: int = 24):
        """Initialize the LLM cache.

        Args:
            db_path: Path to SQLite database file
            ttl_hours: Hours before cache entries expire (default 24)
        """
        self.db_path = db_path
        self.ttl_seconds = ttl_hours * 3600
        self._init_db()

    def _init_db(self) -> None:
        """Create cache directory and table if they don't exist."""
        # Create directory if needed
        cache_dir = os.path.dirname(self.db_path)
        if cache_dir and not os.path.exists(cache_dir):
            os.makedirs(cache_dir, exist_ok=True)

        # Create table
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS llm_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cache_key TEXT UNIQUE NOT NULL,
                response_json TEXT NOT NULL,
                created_at REAL NOT NULL
            )
        ''')
        # Create index on cache_key for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_cache_key ON llm_cache(cache_key)
        ''')
        conn.commit()
        conn.close()

    def _generate_key(self, url: str, text: str) -> str:
        """Generate MD5 hash key from normalized URL and text.

        Args:
            url: URL to include in key
            text: Text to include in key

        Returns:
            MD5 hash string
        """
        # Normalize inputs: lowercase URL, strip whitespace from both
        combined = f"{url.lower().strip()}||{text.strip()}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()

    def get(self, url: str, text: str) -> Optional[Dict[str, Any]]:
        """Get cached response if exists and not expired.

        Args:
            url: URL to look up
            text: Text to look up

        Returns:
            Cached response dict or None if miss/expired
        """
        cache_key = self._generate_key(url, text)
        current_time = time.time()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT response_json, created_at FROM llm_cache WHERE cache_key = ?',
            (cache_key,)
        )
        row = cursor.fetchone()
        conn.close()

        if row is None:
            return None

        response_json, created_at = row

        # Check if expired
        if current_time - created_at > self.ttl_seconds:
            # Entry expired, return None (will be replaced on next set)
            return None

        return json.loads(response_json)

    def set(self, url: str, text: str, response: Dict[str, Any]) -> None:
        """Store response in cache with current timestamp.

        Args:
            url: URL key
            text: Text key
            response: Response dictionary to cache
        """
        cache_key = self._generate_key(url, text)
        response_json = json.dumps(response)
        current_time = time.time()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Use INSERT OR REPLACE to handle duplicates
        cursor.execute('''
            INSERT OR REPLACE INTO llm_cache (cache_key, response_json, created_at)
            VALUES (?, ?, ?)
        ''', (cache_key, response_json, current_time))

        conn.commit()
        conn.close()

    def clear(self) -> None:
        """Clear all entries from cache (useful for testing)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM llm_cache')
        conn.commit()
        conn.close()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with entry_count and oldest/newest timestamps
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*), MIN(created_at), MAX(created_at) FROM llm_cache')
        row = cursor.fetchone()
        conn.close()

        return {
            'entry_count': row[0],
            'oldest_entry': row[1],
            'newest_entry': row[2]
        }
