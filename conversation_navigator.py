#!/usr/bin/env python3
"""
Conversation Navigator & Context Snapshots
Provides instant clarity on "where you are" in complex, multi-layer AI sessions.

Features:
- Conversation recap (last N exchanges)
- Context snapshot (current state summary)
- Timeline view (chronological session log)
- Bridge status check (are we parked?)
- Quick resume helper (what was I doing?)
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


CONFIG_DIR = Path.home() / ".gh-ai-assistant"
CONVERSATION_DB = CONFIG_DIR / "conversations.db"
BRIDGE_DB = CONFIG_DIR / "memory_bridge.db"
SESSION_FILE = CONFIG_DIR / "user_session.json"


@dataclass
class ConversationState:
    """Current conversation state snapshot"""
    session_active: bool
    user_name: str
    assistant_name: str
    current_model: str
    conversation_count: int
    last_exchange_time: datetime
    bridge_active: bool
    bridge_reason: Optional[str]
    last_user_message: str
    last_assistant_message: str
    pending_prompt: Optional[str]
    context_summary: str
    
    def format_summary(self) -> str:
        """Format human-readable summary"""
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════════════════╗")
        lines.append("║                    CONVERSATION STATE SNAPSHOT                       ║")
        lines.append("╚══════════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append(f"👤 USER: {self.user_name}")
        lines.append(f"🤖 ASSISTANT: {self.assistant_name}")
        lines.append(f"📊 CONVERSATION: #{self.conversation_count}")
        lines.append(f"⏰ LAST ACTIVE: {self.last_exchange_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        
        if self.bridge_active:
            lines.append("🌉 STATUS: MEMORY BRIDGE ACTIVE")
            lines.append(f"   Reason: {self.bridge_reason}")
            lines.append("   Your conversation is safely preserved")
            lines.append("   Waiting for model recovery...")
        else:
            lines.append(f"✅ STATUS: ACTIVE on {self.current_model}")
        
        lines.append("")
        lines.append("💬 LAST EXCHANGE:")
        lines.append(f"   You: {self.last_user_message[:100]}...")
        lines.append(f"   AI: {self.last_assistant_message[:100]}...")
        
        if self.pending_prompt:
            lines.append("")
            lines.append("⏳ PENDING:")
            lines.append(f"   {self.pending_prompt[:100]}...")
        
        lines.append("")
        lines.append("📝 CONTEXT:")
        lines.append(f"   {self.context_summary}")
        lines.append("")
        
        return "\n".join(lines)


class ConversationNavigator:
    """
    Provides instant clarity on conversation state.
    
    Never feel lost again—know exactly where you are at any moment.
    """
    
    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.conversation_db = CONVERSATION_DB
        self.bridge_db = BRIDGE_DB
        self.session_file = SESSION_FILE
        
    def get_current_state(self) -> Optional[ConversationState]:
        """Get complete current state snapshot"""
        # Load session
        if not self.session_file.exists():
            return None
            
        with open(self.session_file, 'r') as f:
            session = json.load(f)
        
        # Check bridge status
        bridge_active = False
        bridge_reason = None
        pending_prompt = None
        
        if self.bridge_db.exists():
            conn = sqlite3.connect(self.bridge_db)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT state, user_prompt, continuation_prompt
                FROM bridge_activations
                WHERE successful = 0
                ORDER BY activation_time DESC
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            if result and result[0] == 'activated':
                bridge_active = True
                pending_prompt = result[1]
                bridge_reason = "All models exhausted, waiting for recovery"
            
            conn.close()
        
        # Get last exchange
        last_user = "No previous messages"
        last_assistant = "No previous messages"
        last_time = datetime.now()
        
        if self.conversation_db.exists():
            conn = sqlite3.connect(self.conversation_db)
            cursor = conn.cursor()
            
            # Get last 2 messages
            cursor.execute('''
                SELECT role, content, timestamp
                FROM messages
                ORDER BY timestamp DESC
                LIMIT 2
            ''')
            
            messages = cursor.fetchall()
            
            if len(messages) >= 2:
                if messages[0][0] == 'assistant':
                    last_assistant = messages[0][1]
                    last_user = messages[1][1]
                else:
                    last_user = messages[0][1]
                    last_assistant = messages[1][1]
                    
                last_time = datetime.fromisoformat(messages[0][2])
            
            conn.close()
        
        # Generate context summary
        context_summary = self._generate_context_summary()
        
        return ConversationState(
            session_active=True,
            user_name=session.get('user_name', 'User'),
            assistant_name=session.get('assistant_name', 'Assistant'),
            current_model=session.get('preferred_model', 'Unknown'),
            conversation_count=session.get('total_conversations', 0),
            last_exchange_time=last_time,
            bridge_active=bridge_active,
            bridge_reason=bridge_reason,
            last_user_message=last_user,
            last_assistant_message=last_assistant,
            pending_prompt=pending_prompt,
            context_summary=context_summary
        )
    
    def _generate_context_summary(self) -> str:
        """Generate brief context summary from recent messages"""
        if not self.conversation_db.exists():
            return "New conversation, no context yet"
        
        conn = sqlite3.connect(self.conversation_db)
        cursor = conn.cursor()
        
        # Get last 5 messages
        cursor.execute('''
            SELECT content FROM messages
            ORDER BY timestamp DESC
            LIMIT 5
        ''')
        
        messages = [msg[0] for msg in cursor.fetchall()]
        conn.close()
        
        # Extract keywords/topics
        all_text = " ".join(messages).lower()
        
        # Common technical terms
        topics = []
        keywords = {
            'authentication': 'Auth system',
            'fastapi': 'FastAPI',
            'jwt': 'JWT tokens',
            'database': 'Database',
            'api': 'API development',
            'memory': 'Memory management',
            'bridge': 'Memory bridge',
            'transfer': 'Context transfer',
            'model': 'Model selection',
            'session': 'Session handling'
        }
        
        for keyword, topic in keywords.items():
            if keyword in all_text:
                topics.append(topic)
        
        if topics:
            return f"Working on: {', '.join(topics[:3])}"
        else:
            return "General development discussion"
    
    def get_conversation_recap(self, last_n: int = 10) -> List[Dict]:
        """Get last N conversation exchanges"""
        if not self.conversation_db.exists():
            return []
        
        conn = sqlite3.connect(self.conversation_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp
            FROM messages
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (last_n,))
        
        messages = cursor.fetchall()
        conn.close()
        
        # Reverse to chronological order
        messages = list(reversed(messages))
        
        return [
            {
                'role': msg[0],
                'content': msg[1],
                'timestamp': msg[2]
            }
            for msg in messages
        ]
    
    def format_recap(self, messages: List[Dict]) -> str:
        """Format recap for display"""
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════════════════╗")
        lines.append("║                      CONVERSATION RECAP                              ║")
        lines.append("╚══════════════════════════════════════════════════════════════════════╝")
        lines.append("")
        
        for i, msg in enumerate(messages, 1):
            timestamp = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M:%S')
            role_icon = "👤" if msg['role'] == 'user' else "🤖"
            role_label = "YOU" if msg['role'] == 'user' else "AI"
            
            # Truncate long messages
            content = msg['content']
            if len(content) > 150:
                content = content[:150] + "..."
            
            lines.append(f"{i}. [{timestamp}] {role_icon} {role_label}:")
            lines.append(f"   {content}")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_timeline_view(self, hours: int = 24) -> Dict:
        """Get chronological timeline of session activity"""
        if not self.conversation_db.exists():
            return {'total_messages': 0, 'exchanges': []}
        
        cutoff = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect(self.conversation_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT role, content, timestamp
            FROM messages
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        ''', (cutoff.isoformat(),))
        
        messages = cursor.fetchall()
        conn.close()
        
        # Group into exchanges
        exchanges = []
        current_exchange = {'user': None, 'assistant': None, 'time': None}
        
        for role, content, timestamp in messages:
            if role == 'user':
                if current_exchange['user'] is not None:
                    # Save previous exchange
                    exchanges.append(current_exchange.copy())
                current_exchange = {'user': content[:100], 'assistant': None, 'time': timestamp}
            elif role == 'assistant':
                current_exchange['assistant'] = content[:100]
                exchanges.append(current_exchange.copy())
                current_exchange = {'user': None, 'assistant': None, 'time': None}
        
        return {
            'total_messages': len(messages),
            'total_exchanges': len(exchanges),
            'exchanges': exchanges,
            'time_period': f'Last {hours} hours'
        }
    
    def format_timeline(self, timeline: Dict) -> str:
        """Format timeline for display"""
        lines = []
        lines.append("╔══════════════════════════════════════════════════════════════════════╗")
        lines.append("║                      SESSION TIMELINE                                ║")
        lines.append("╚══════════════════════════════════════════════════════════════════════╝")
        lines.append("")
        lines.append(f"📅 Period: {timeline['time_period']}")
        lines.append(f"💬 Total Messages: {timeline['total_messages']}")
        lines.append(f"🔄 Total Exchanges: {timeline['total_exchanges']}")
        lines.append("")
        
        for i, exchange in enumerate(timeline['exchanges'], 1):
            time = datetime.fromisoformat(exchange['time']).strftime('%H:%M:%S')
            lines.append(f"{i}. [{time}]")
            if exchange['user']:
                lines.append(f"   👤 {exchange['user']}...")
            if exchange['assistant']:
                lines.append(f"   🤖 {exchange['assistant']}...")
            lines.append("")
        
        return "\n".join(lines)
    
    def check_bridge_status(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """Check if memory bridge is active"""
        if not self.bridge_db.exists():
            return False, None, None
        
        conn = sqlite3.connect(self.bridge_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT state, user_prompt, expected_recovery_time
            FROM bridge_activations
            WHERE successful = 0
            ORDER BY activation_time DESC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] == 'activated':
            return True, result[1], f"{result[2]} seconds"
        
        return False, None, None
    
    def get_quick_resume_info(self) -> str:
        """Get quick info for resuming conversation"""
        state = self.get_current_state()
        
        if not state:
            return "No active session. Start with: python session_manager.py --init"
        
        if state.bridge_active:
            return f"""
🌉 MEMORY BRIDGE ACTIVE

Your conversation is safely preserved.

WHAT WAS I DOING?
  You asked: "{state.pending_prompt[:150]}..."

WHEN WILL IT RESUME?
  Waiting for any cloud model to become available
  Typically: 2-5 minutes

WHAT SHOULD I DO?
  Option 1: Wait - conversation will resume automatically
  Option 2: Check model status: python gh_ai_core.py models
  Option 3: Use local model: python gh_ai_core.py ask --ollama "your question"

YOUR CONTEXT IS SAFE. Nothing is lost.
""".strip()
        else:
            return f"""
✅ ACTIVE SESSION

WHAT WAS I DOING?
  Last exchange: "{state.last_user_message[:150]}..."
  AI responded: "{state.last_assistant_message[:150]}..."

CURRENT STATE:
  Model: {state.current_model}
  Conversation: #{state.conversation_count}
  Time: {state.last_exchange_time.strftime('%H:%M:%S')}

READY TO CONTINUE!
  Use: python gh_ai_core.py chat
  Or: python gh_ai_core.py ask "your question"
""".strip()


def main():
    """CLI for conversation navigation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Conversation Navigator - Never lose track of where you are"
    )
    
    parser.add_argument('--status', action='store_true',
                       help='Show current conversation state')
    parser.add_argument('--recap', type=int, metavar='N', default=10,
                       help='Show last N exchanges (default: 10)')
    parser.add_argument('--timeline', type=int, metavar='HOURS', default=24,
                       help='Show timeline for last N hours (default: 24)')
    parser.add_argument('--bridge', action='store_true',
                       help='Check bridge status')
    parser.add_argument('--resume', action='store_true',
                       help='Get quick resume information')
    parser.add_argument('--where-am-i', action='store_true',
                       help='Complete orientation (status + recap + resume)')
    
    args = parser.parse_args()
    
    navigator = ConversationNavigator()
    
    if args.where_am_i:
        # Complete orientation
        print()
        state = navigator.get_current_state()
        if state:
            print(state.format_summary())
            print()
            
        recap = navigator.get_conversation_recap(5)
        if recap:
            print(navigator.format_recap(recap))
            
        print()
        print(navigator.get_quick_resume_info())
        print()
        
    elif args.status:
        state = navigator.get_current_state()
        if state:
            print()
            print(state.format_summary())
            print()
        else:
            print("\n❌ No active session\n")
            
    elif args.recap:
        recap = navigator.get_conversation_recap(args.recap)
        if recap:
            print()
            print(navigator.format_recap(recap))
            print()
        else:
            print("\n❌ No conversation history\n")
            
    elif args.timeline:
        timeline = navigator.get_timeline_view(args.timeline)
        print()
        print(navigator.format_timeline(timeline))
        print()
        
    elif args.bridge:
        active, prompt, eta = navigator.check_bridge_status()
        print()
        if active:
            print("🌉 MEMORY BRIDGE ACTIVE")
            print(f"   Pending: {prompt[:100]}...")
            print(f"   Expected recovery: {eta}")
        else:
            print("✅ No bridge active - session running normally")
        print()
        
    elif args.resume:
        print()
        print(navigator.get_quick_resume_info())
        print()
        
    else:
        # Default: show status
        state = navigator.get_current_state()
        if state:
            print()
            print(state.format_summary())
            print()
        else:
            print("\n❌ No active session. Use --help for options\n")


if __name__ == "__main__":
    main()
