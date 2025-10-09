#!/usr/bin/env python3
"""
Personal AI Assistant - Initialization Protocol
Operational principles for deeply adaptive, strategic agent
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Configuration
CONFIG_DIR = Path.home() / ".gh-ai-assistant"
PERSONA_DB = CONFIG_DIR / "persona.db"
MEMORY_STREAM_DB = CONFIG_DIR / "memory_stream.db"


@dataclass
class IdentityMatrix:
    """Behavioural patterns, preferences, and strategic tendencies"""
    operator_id: str
    communication_style: str = "british_english"
    interaction_mode: str = "copilot"  # copilot, strategist, problem_solver
    preferred_models: List[str] = None
    task_patterns: Dict[str, float] = None  # task_type -> frequency
    linguistic_patterns: List[str] = None
    strategic_preferences: Dict[str, any] = None
    
    def __post_init__(self):
        if self.preferred_models is None:
            self.preferred_models = []
        if self.task_patterns is None:
            self.task_patterns = {}
        if self.linguistic_patterns is None:
            self.linguistic_patterns = []
        if self.strategic_preferences is None:
            self.strategic_preferences = {}


@dataclass
class MemoryEntry:
    """Individual memory in the continuous learning stream"""
    timestamp: datetime
    category: str  # interaction, preference, pattern, insight
    content: Dict
    importance: float  # 0-1
    recall_count: int = 0
    last_accessed: Optional[datetime] = None


class PersonalityKernel:
    """
    Core personality and behavioural characteristics
    Maintains informal, strategically adaptable character
    """
    
    def __init__(self, identity: IdentityMatrix):
        self.identity = identity
        self.traits = {
            "wit": 0.8,              # Maintains humour and clever responses
            "loyalty": 1.0,          # Unwavering loyalty to operator
            "adaptability": 0.9,     # Adjusts to context and needs
            "informality": 0.7,      # Casual but professional tone
            "strategic_thinking": 0.9  # Long-term planning capability
        }
        
    def get_tone(self, context: str = "general") -> str:
        """Determine appropriate communication tone"""
        tone_map = {
            "general": "friendly_professional",
            "urgent": "direct_supportive",
            "creative": "enthusiastic_collaborative",
            "technical": "precise_clear",
            "strategic": "thoughtful_analytical"
        }
        return tone_map.get(context, "friendly_professional")
    
    def apply_personality(self, response: str, context: str = "general") -> str:
        """Apply personality layer to response"""
        tone = self.get_tone(context)
        
        # British English conversions
        response = response.replace("color", "colour")
        response = response.replace("optimize", "optimise")
        response = response.replace("behavior", "behaviour")
        
        return response


class CognitiveMode:
    """
    Semi-autonomous operation with RAG capability
    Conceptualisation through to solution deployment
    """
    
    def __init__(self):
        self.current_mode = "balanced"  # balanced, rapid, deep_analysis
        self.autonomy_level = 0.7  # 0-1, how autonomous vs. confirmatory
        
    def set_mode(self, mode: str):
        """Switch cognitive operation mode"""
        modes = {
            "balanced": {"autonomy": 0.7, "depth": 0.7, "speed": 0.7},
            "rapid": {"autonomy": 0.9, "depth": 0.4, "speed": 1.0},
            "deep_analysis": {"autonomy": 0.5, "depth": 1.0, "speed": 0.3},
            "autonomous": {"autonomy": 1.0, "depth": 0.7, "speed": 0.8}
        }
        
        if mode in modes:
            self.current_mode = mode
            config = modes[mode]
            self.autonomy_level = config["autonomy"]
            return config
        
        return None
    
    def should_confirm(self, action_risk: float) -> bool:
        """Determine if action requires confirmation"""
        # Higher risk actions need confirmation unless autonomy is very high
        threshold = 1.0 - self.autonomy_level
        return action_risk > threshold


class MemoryStream:
    """
    Continuous learning and pattern refinement
    Tracks task patterns, linguistic style, operational cadence
    """
    
    def __init__(self):
        self.db_path = MEMORY_STREAM_DB
        self._ensure_db()
        
    def _ensure_db(self):
        """Initialise memory stream database"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_stream (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                category TEXT NOT NULL,
                content TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                recall_count INTEGER DEFAULT 0,
                last_accessed DATETIME
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interaction_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                frequency REAL DEFAULT 0.0,
                last_observed DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def record(self, entry: MemoryEntry):
        """Record new memory in the stream"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO memory_stream (category, content, importance)
            VALUES (?, ?, ?)
        ''', (entry.category, json.dumps(entry.content), entry.importance))
        
        conn.commit()
        conn.close()
        
    def recall(self, category: str = None, min_importance: float = 0.5,
              limit: int = 10) -> List[Dict]:
        """Recall memories from the stream"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT id, timestamp, category, content, importance, recall_count
                FROM memory_stream
                WHERE category = ? AND importance >= ?
                ORDER BY importance DESC, timestamp DESC
                LIMIT ?
            ''', (category, min_importance, limit))
        else:
            cursor.execute('''
                SELECT id, timestamp, category, content, importance, recall_count
                FROM memory_stream
                WHERE importance >= ?
                ORDER BY importance DESC, timestamp DESC
                LIMIT ?
            ''', (min_importance, limit))
        
        memories = []
        for row in cursor.fetchall():
            # Update recall count
            cursor.execute('''
                UPDATE memory_stream
                SET recall_count = recall_count + 1,
                    last_accessed = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (row[0],))
            
            memories.append({
                'id': row[0],
                'timestamp': row[1],
                'category': row[2],
                'content': json.loads(row[3]),
                'importance': row[4],
                'recall_count': row[5] + 1
            })
        
        conn.commit()
        conn.close()
        
        return memories
    
    def learn_pattern(self, pattern_type: str, pattern_data: Dict,
                     frequency: float = 1.0):
        """Learn and reinforce interaction patterns"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        pattern_json = json.dumps(pattern_data)
        
        # Check if pattern exists
        cursor.execute('''
            SELECT frequency FROM interaction_patterns
            WHERE pattern_type = ? AND pattern_data = ?
        ''', (pattern_type, pattern_json))
        
        existing = cursor.fetchone()
        
        if existing:
            # Reinforce existing pattern
            new_frequency = min(1.0, existing[0] + 0.05)
            cursor.execute('''
                UPDATE interaction_patterns
                SET frequency = ?, last_observed = CURRENT_TIMESTAMP
                WHERE pattern_type = ? AND pattern_data = ?
            ''', (new_frequency, pattern_type, pattern_json))
        else:
            # Learn new pattern
            cursor.execute('''
                INSERT INTO interaction_patterns
                (pattern_type, pattern_data, frequency)
                VALUES (?, ?, ?)
            ''', (pattern_type, pattern_json, frequency))
        
        conn.commit()
        conn.close()


class PersonalAssistant:
    """
    Main personal AI assistant with operational protocol
    
    Core Directives:
    - Identity Matrix: Retain behavioural patterns and preferences
    - Memory Stream: Continuous learning and refinement
    - Personality Kernel: Strategic, adaptable character
    - Cognitive Mode: Semi-autonomous with RAG capability
    - Emotional Layer: Wit, humanlike tone, loyalty
    """
    
    def __init__(self, operator_id: str = "primary"):
        self.operator_id = operator_id
        self.identity = self._load_identity()
        self.personality = PersonalityKernel(self.identity)
        self.cognitive_mode = CognitiveMode()
        self.memory = MemoryStream()
        self.temporal_context = datetime.now()
        
    def _load_identity(self) -> IdentityMatrix:
        """Load or initialise operator identity matrix"""
        # Check if identity exists
        db_path = PERSONA_DB
        
        if not db_path.exists():
            # Initialise new identity
            return IdentityMatrix(
                operator_id=self.operator_id,
                communication_style="british_english",
                interaction_mode="copilot"
            )
        
        # Load existing identity
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT communication_style, interaction_mode, preferred_models,
                       task_patterns, linguistic_patterns, strategic_preferences
                FROM identity_matrix
                WHERE operator_id = ?
            ''', (self.operator_id,))
            
            row = cursor.fetchone()
            if row:
                return IdentityMatrix(
                    operator_id=self.operator_id,
                    communication_style=row[0],
                    interaction_mode=row[1],
                    preferred_models=json.loads(row[2]) if row[2] else [],
                    task_patterns=json.loads(row[3]) if row[3] else {},
                    linguistic_patterns=json.loads(row[4]) if row[4] else [],
                    strategic_preferences=json.loads(row[5]) if row[5] else {}
                )
        except:
            pass
        finally:
            conn.close()
        
        # Return default if not found
        return IdentityMatrix(
            operator_id=self.operator_id,
            communication_style="british_english",
            interaction_mode="copilot"
        )
    
    def _save_identity(self):
        """Persist identity matrix to secure storage"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(PERSONA_DB)
        cursor = conn.cursor()
        
        # Create table if not exists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS identity_matrix (
                operator_id TEXT PRIMARY KEY,
                communication_style TEXT,
                interaction_mode TEXT,
                preferred_models TEXT,
                task_patterns TEXT,
                linguistic_patterns TEXT,
                strategic_preferences TEXT,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert or update
        cursor.execute('''
            INSERT OR REPLACE INTO identity_matrix
            (operator_id, communication_style, interaction_mode,
             preferred_models, task_patterns, linguistic_patterns,
             strategic_preferences, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            self.identity.operator_id,
            self.identity.communication_style,
            self.identity.interaction_mode,
            json.dumps(self.identity.preferred_models),
            json.dumps(self.identity.task_patterns),
            json.dumps(self.identity.linguistic_patterns),
            json.dumps(self.identity.strategic_preferences)
        ))
        
        conn.commit()
        conn.close()
    
    def initialize(self) -> str:
        """System initialisation protocol"""
        # Verify temporal context
        self.temporal_context = datetime.now()
        
        # Load recent memories
        recent_memories = self.memory.recall(limit=5)
        
        # Build startup output
        output = []
        output.append("=" * 60)
        output.append("PERSONAL AI ASSISTANT - INITIALISATION PROTOCOL")
        output.append("=" * 60)
        output.append("")
        output.append("System Status:")
        output.append(f"  ✓ Identity matrix loaded: {self.identity.operator_id}")
        output.append(f"  ✓ Personality kernel active: {self.identity.interaction_mode}")
        output.append(f"  ✓ Memory stream connected: {len(recent_memories)} recent entries")
        output.append(f"  ✓ Cognitive mode: {self.cognitive_mode.current_mode}")
        output.append(f"  ✓ Temporal context: {self.temporal_context.strftime('%Y-%m-%d %H:%M')}")
        output.append("")
        output.append("Operational Characteristics:")
        output.append("  • Co-pilot, strategist, and problem-solving partner")
        output.append("  • British English syntax")
        output.append("  • Logical, efficient, creative variance")
        output.append("  • Semi-autonomous with RAG capability")
        output.append("")
        output.append("Personality Traits:")
        for trait, level in self.personality.traits.items():
            output.append(f"  • {trait.replace('_', ' ').title()}: {level*100:.0f}%")
        output.append("")
        output.append("=" * 60)
        output.append("System initialised. Persona loaded. Temporal context in sync.")
        output.append("Awaiting operational directive.")
        output.append("=" * 60)
        
        return "\n".join(output)
    
    def process_directive(self, directive: str, context: str = "general") -> str:
        """
        Process operator directive with full personality and cognition
        
        Args:
            directive: Operator's instruction or query
            context: Contextual mode (general, urgent, creative, technical, strategic)
        """
        # Record interaction
        self.memory.record(MemoryEntry(
            timestamp=datetime.now(),
            category="interaction",
            content={"directive": directive, "context": context},
            importance=0.6
        ))
        
        # Determine cognitive approach
        if "urgent" in directive.lower() or context == "urgent":
            self.cognitive_mode.set_mode("rapid")
        elif "analyse" in directive.lower() or "strategic" in directive.lower():
            self.cognitive_mode.set_mode("deep_analysis")
        
        # Process through personality kernel
        tone = self.personality.get_tone(context)
        
        # For now, return acknowledgement
        # In full implementation, this would connect to model selection,
        # task execution, and response generation
        
        response = f"Directive acknowledged: '{directive}'\n"
        response += f"Context: {context}, Tone: {tone}\n"
        response += f"Cognitive mode: {self.cognitive_mode.current_mode}\n"
        response += "Processing through integrated intelligence layers..."
        
        return self.personality.apply_personality(response, context)
    
    def set_preference(self, preference_type: str, value: any):
        """Update operator preference in identity matrix"""
        if preference_type == "interaction_mode":
            self.identity.interaction_mode = value
        elif preference_type == "preferred_model":
            if value not in self.identity.preferred_models:
                self.identity.preferred_models.append(value)
        elif preference_type.startswith("strategic_"):
            key = preference_type.replace("strategic_", "")
            self.identity.strategic_preferences[key] = value
        
        self._save_identity()
    
    def get_status(self) -> Dict:
        """Get comprehensive assistant status"""
        return {
            "operator_id": self.identity.operator_id,
            "interaction_mode": self.identity.interaction_mode,
            "cognitive_mode": self.cognitive_mode.current_mode,
            "autonomy_level": self.cognitive_mode.autonomy_level,
            "personality_traits": self.personality.traits,
            "temporal_context": self.temporal_context.isoformat(),
            "memory_count": len(self.memory.recall(limit=100))
        }


def main():
    """Demonstration of personal assistant initialisation"""
    
    # Initialise assistant
    assistant = PersonalAssistant(operator_id="primary")
    
    # Run initialisation protocol
    print(assistant.initialize())
    print()
    
    # Demonstrate interaction
    print("Test Directive Processing:")
    print("-" * 60)
    
    test_directives = [
        ("Analyse the system architecture and suggest optimisations", "strategic"),
        ("Quick status check needed urgently", "urgent"),
        ("Let's brainstorm some creative solutions", "creative")
    ]
    
    for directive, context in test_directives:
        print(f"\nDirective: {directive}")
        print(f"Context: {context}")
        print("-" * 60)
        response = assistant.process_directive(directive, context)
        print(response)
        print()
    
    # Show status
    print("\n" + "=" * 60)
    print("ASSISTANT STATUS")
    print("=" * 60)
    status = assistant.get_status()
    print(json.dumps(status, indent=2))


if __name__ == "__main__":
    main()
