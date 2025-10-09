#!/usr/bin/env python3
"""
Conversation Storage System
Stores and retrieves conversation history for context and continuity
"""

import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

CONFIG_DIR = Path.home() / ".gh-ai-assistant"
CONVERSATIONS_DB = CONFIG_DIR / "conversations.db"


@dataclass
class Message:
    """Individual message in conversation"""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime
    model_used: Optional[str] = None
    tokens_used: Optional[int] = None
    
    def to_dict(self) -> Dict:
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat(),
            'model_used': self.model_used,
            'tokens_used': self.tokens_used
        }


@dataclass
class Conversation:
    """Complete conversation session"""
    session_id: str
    started_at: datetime
    last_message_at: datetime
    message_count: int
    total_tokens: int
    summary: Optional[str] = None


class ConversationStore:
    """
    Manages conversation storage and retrieval
    """
    
    def __init__(self, db_path: Path = CONVERSATIONS_DB):
        self.db_path = db_path
        self._ensure_db()
        
    def _ensure_db(self):
        """Initialize conversation database"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                session_id TEXT PRIMARY KEY,
                started_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_message_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                summary TEXT,
                metadata TEXT
            )
        ''')
        
        # Messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                model_used TEXT,
                tokens_used INTEGER,
                FOREIGN KEY (session_id) REFERENCES conversations(session_id)
            )
        ''')
        
        # Index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_session 
            ON messages(session_id, timestamp)
        ''')
        
        conn.commit()
        conn.close()
        
    def create_session(self, session_id: str = None) -> str:
        """Create new conversation session"""
        if not session_id:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR IGNORE INTO conversations (session_id)
            VALUES (?)
        ''', (session_id,))
        
        conn.commit()
        conn.close()
        
        return session_id
        
    def add_message(self, session_id: str, message: Message):
        """Add message to conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ensure session exists
        self.create_session(session_id)
        
        # Insert message
        cursor.execute('''
            INSERT INTO messages 
            (session_id, role, content, timestamp, model_used, tokens_used)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            message.role,
            message.content,
            message.timestamp,
            message.model_used,
            message.tokens_used
        ))
        
        # Update conversation metadata
        cursor.execute('''
            UPDATE conversations
            SET last_message_at = ?,
                message_count = message_count + 1,
                total_tokens = total_tokens + ?
            WHERE session_id = ?
        ''', (
            message.timestamp,
            message.tokens_used or 0,
            session_id
        ))
        
        conn.commit()
        conn.close()
        
    def get_messages(self, session_id: str, limit: int = None) -> List[Message]:
        """Get messages from conversation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if limit:
            cursor.execute('''
                SELECT role, content, timestamp, model_used, tokens_used
                FROM messages
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session_id, limit))
        else:
            cursor.execute('''
                SELECT role, content, timestamp, model_used, tokens_used
                FROM messages
                WHERE session_id = ?
                ORDER BY timestamp ASC
            ''', (session_id,))
        
        messages = []
        for row in cursor.fetchall():
            messages.append(Message(
                role=row[0],
                content=row[1],
                timestamp=datetime.fromisoformat(row[2]) if isinstance(row[2], str) else row[2],
                model_used=row[3],
                tokens_used=row[4]
            ))
        
        conn.close()
        
        # If limit was specified, reverse to get chronological order
        if limit:
            messages.reverse()
        
        return messages
        
    def get_recent_context(self, session_id: str, 
                          message_count: int = 10) -> List[Dict]:
        """
        Get recent messages formatted for AI context
        Returns messages in format suitable for OpenRouter/OpenAI API
        """
        messages = self.get_messages(session_id, limit=message_count)
        
        return [
            {
                'role': msg.role,
                'content': msg.content
            }
            for msg in messages
        ]
        
    def get_session_info(self, session_id: str) -> Optional[Conversation]:
        """Get conversation session information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, started_at, last_message_at, 
                   message_count, total_tokens, summary
            FROM conversations
            WHERE session_id = ?
        ''', (session_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return Conversation(
                session_id=row[0],
                started_at=datetime.fromisoformat(row[1]) if isinstance(row[1], str) else row[1],
                last_message_at=datetime.fromisoformat(row[2]) if isinstance(row[2], str) else row[2],
                message_count=row[3],
                total_tokens=row[4],
                summary=row[5]
            )
        
        return None
        
    def list_sessions(self, limit: int = 10) -> List[Conversation]:
        """List recent conversation sessions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, started_at, last_message_at,
                   message_count, total_tokens, summary
            FROM conversations
            ORDER BY last_message_at DESC
            LIMIT ?
        ''', (limit,))
        
        sessions = []
        for row in cursor.fetchall():
            sessions.append(Conversation(
                session_id=row[0],
                started_at=datetime.fromisoformat(row[1]) if isinstance(row[1], str) else row[1],
                last_message_at=datetime.fromisoformat(row[2]) if isinstance(row[2], str) else row[2],
                message_count=row[3],
                total_tokens=row[4],
                summary=row[5]
            ))
        
        conn.close()
        return sessions
        
    def get_active_session(self) -> Optional[str]:
        """Get most recent active session (within last hour)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        one_hour_ago = datetime.now() - timedelta(hours=1)
        
        cursor.execute('''
            SELECT session_id
            FROM conversations
            WHERE last_message_at > ?
            ORDER BY last_message_at DESC
            LIMIT 1
        ''', (one_hour_ago,))
        
        row = cursor.fetchone()
        conn.close()
        
        return row[0] if row else None
        
    def export_conversation(self, session_id: str, 
                           format: str = 'json') -> str:
        """Export conversation to file"""
        messages = self.get_messages(session_id)
        session = self.get_session_info(session_id)
        
        if format == 'json':
            export_data = {
                'session_id': session_id,
                'started_at': session.started_at.isoformat() if session else None,
                'message_count': len(messages),
                'messages': [msg.to_dict() for msg in messages]
            }
            return json.dumps(export_data, indent=2)
        
        elif format == 'markdown':
            lines = [
                f"# Conversation: {session_id}",
                f"Started: {session.started_at if session else 'Unknown'}",
                f"Messages: {len(messages)}",
                "",
                "---",
                ""
            ]
            
            for msg in messages:
                role_emoji = "👤" if msg.role == "user" else "🤖"
                lines.append(f"## {role_emoji} {msg.role.title()}")
                if msg.model_used:
                    lines.append(f"*Model: {msg.model_used}*")
                lines.append("")
                lines.append(msg.content)
                lines.append("")
                lines.append("---")
                lines.append("")
            
            return "\n".join(lines)
        
        return ""


def main():
    """Demo conversation storage"""
    print("=" * 60)
    print("CONVERSATION STORAGE SYSTEM DEMO")
    print("=" * 60)
    print()
    
    store = ConversationStore()
    
    # Create session
    session_id = store.create_session("demo_session")
    print(f"Created session: {session_id}")
    print()
    
    # Add some messages
    messages = [
        Message(
            role="user",
            content="What are the best free AI models?",
            timestamp=datetime.now(),
            model_used=None,
            tokens_used=10
        ),
        Message(
            role="assistant",
            content="The best free models include DeepSeek R1, Google Gemini, and Meta Llama 3.2.",
            timestamp=datetime.now(),
            model_used="google/gemini-2.0-flash-exp:free",
            tokens_used=25
        ),
        Message(
            role="user",
            content="How do I use them?",
            timestamp=datetime.now(),
            model_used=None,
            tokens_used=8
        )
    ]
    
    for msg in messages:
        store.add_message(session_id, msg)
        print(f"Added: {msg.role} - {msg.content[:50]}...")
    
    print()
    print("=" * 60)
    print("SESSION INFO")
    print("=" * 60)
    
    session = store.get_session_info(session_id)
    if session:
        print(f"Session ID: {session.session_id}")
        print(f"Started: {session.started_at}")
        print(f"Messages: {session.message_count}")
        print(f"Total Tokens: {session.total_tokens}")
    
    print()
    print("=" * 60)
    print("RECENT CONTEXT (for AI)")
    print("=" * 60)
    
    context = store.get_recent_context(session_id, message_count=5)
    print(json.dumps(context, indent=2))
    
    print()
    print("=" * 60)
    print("EXPORT (Markdown)")
    print("=" * 60)
    
    markdown = store.export_conversation(session_id, format='markdown')
    print(markdown[:500] + "...")


if __name__ == "__main__":
    main()
