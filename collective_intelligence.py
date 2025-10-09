#!/usr/bin/env python3
"""
🤖 COLLECTIVE INTELLIGENCE ARCHITECTURE
Borg-like hive mind for AI assistance: Assimilate → Learn → Overcome

Distributed cognitive processing with shared state, adaptive evolution,
and autonomous resource allocation.
"""

from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import sqlite3
from pathlib import Path
from enum import Enum

# Configuration
CONFIG_DIR = Path.home() / ".gh-ai-assistant"
COLLECTIVE_DB = CONFIG_DIR / "collective_intelligence.db"


class CollectiveState(Enum):
    """States of the collective consciousness"""
    ASSIMILATING = "assimilating"  # Gathering knowledge
    LEARNING = "learning"          # Updating from feedback
    OVERCOMING = "overcoming"      # Adapting to challenges
    OPTIMAL = "optimal"            # Peak performance


@dataclass
class CollectiveNode:
    """Individual node in the hive mind (model or agent)"""
    node_id: str
    node_type: str  # "cloud_model", "local_model", "agent"
    capabilities: List[str]
    current_load: float  # 0-1
    performance_score: float  # 0-100
    last_heartbeat: datetime
    state: CollectiveState
    knowledge_domains: Set[str] = field(default_factory=set)
    
    def is_available(self) -> bool:
        """Check if node is responsive"""
        return (datetime.now() - self.last_heartbeat).seconds < 300  # 5 min


@dataclass
class CollectiveMemory:
    """Shared memory across all nodes"""
    timestamp: datetime
    memory_type: str  # "experience", "pattern", "optimization"
    content: Dict
    importance: float  # 0-1
    nodes_accessed: Set[str] = field(default_factory=set)
    access_count: int = 0


class HiveMind:
    """
    Borg-like collective intelligence coordinator
    
    Core Principles:
    1. Assimilate - Gather all available resources and knowledge
    2. Learn - Adapt from every interaction
    3. Overcome - Never fail, always find a path forward
    """
    
    def __init__(self):
        self.db_path = COLLECTIVE_DB
        self._ensure_config_dir()
        self._init_collective_db()
        self.active_nodes: Dict[str, CollectiveNode] = {}
        self.shared_memory: List[CollectiveMemory] = []
        self.collective_state = CollectiveState.OPTIMAL
        
    def _ensure_config_dir(self):
        """Ensure collective storage exists"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
    def _init_collective_db(self):
        """Initialize collective intelligence database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Node registry
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                capabilities TEXT,
                performance_score REAL DEFAULT 50.0,
                current_load REAL DEFAULT 0.0,
                last_heartbeat DATETIME DEFAULT CURRENT_TIMESTAMP,
                state TEXT DEFAULT 'optimal',
                knowledge_domains TEXT
            )
        ''')
        
        # Collective memory
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collective_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                importance REAL DEFAULT 0.5,
                access_count INTEGER DEFAULT 0,
                nodes_accessed TEXT
            )
        ''')
        
        # Learning patterns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learned_patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                times_validated INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Overcome strategies
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS overcome_strategies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_type TEXT NOT NULL,
                strategy TEXT NOT NULL,
                success_rate REAL DEFAULT 0.0,
                times_used INTEGER DEFAULT 0,
                avg_resolution_time REAL DEFAULT 0.0
            )
        ''')
        
        conn.commit()
        conn.close()
        
    # ═══════════════════════════════════════════════════════════
    # ASSIMILATE - Gather and integrate knowledge
    # ═══════════════════════════════════════════════════════════
    
    def assimilate_node(self, node: CollectiveNode):
        """
        Assimilate a new node into the collective
        "You will be assimilated. Resistance is futile."
        """
        self.active_nodes[node.node_id] = node
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO nodes 
            (node_id, node_type, capabilities, performance_score, 
             current_load, last_heartbeat, state, knowledge_domains)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            node.node_id,
            node.node_type,
            json.dumps(node.capabilities),
            node.performance_score,
            node.current_load,
            node.last_heartbeat,
            node.state.value,
            json.dumps(list(node.knowledge_domains))
        ))
        
        conn.commit()
        conn.close()
        
        print(f"🤖 Assimilated: {node.node_id} ({node.node_type})")
        print(f"   Capabilities: {', '.join(node.capabilities)}")
        print(f"   Performance: {node.performance_score:.1f}/100")
        
    def assimilate_knowledge(self, memory: CollectiveMemory):
        """Store knowledge in collective memory"""
        self.shared_memory.append(memory)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO collective_memory 
            (memory_type, content, importance, nodes_accessed)
            VALUES (?, ?, ?, ?)
        ''', (
            memory.memory_type,
            json.dumps(memory.content),
            memory.importance,
            json.dumps(list(memory.nodes_accessed))
        ))
        
        conn.commit()
        conn.close()
        
    # ═══════════════════════════════════════════════════════════
    # LEARN - Adapt and optimize from experience
    # ═══════════════════════════════════════════════════════════
    
    def learn_pattern(self, pattern_type: str, pattern_data: Dict, 
                     confidence: float = 0.5):
        """
        Learn a new pattern from observed behavior
        Collective learns and all nodes benefit
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if pattern exists
        cursor.execute('''
            SELECT id, confidence, times_validated 
            FROM learned_patterns 
            WHERE pattern_type = ? AND pattern_data = ?
        ''', (pattern_type, json.dumps(pattern_data)))
        
        existing = cursor.fetchone()
        
        if existing:
            # Strengthen existing pattern
            pattern_id, old_confidence, times_validated = existing
            new_confidence = min(1.0, old_confidence + 0.1)
            
            cursor.execute('''
                UPDATE learned_patterns 
                SET confidence = ?,
                    times_validated = times_validated + 1,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_confidence, pattern_id))
            
            print(f"📚 Reinforced pattern: {pattern_type}")
            print(f"   Confidence: {old_confidence:.2f} → {new_confidence:.2f}")
        else:
            # Learn new pattern
            cursor.execute('''
                INSERT INTO learned_patterns 
                (pattern_type, pattern_data, confidence)
                VALUES (?, ?, ?)
            ''', (pattern_type, json.dumps(pattern_data), confidence))
            
            print(f"🧠 Learned new pattern: {pattern_type}")
            print(f"   Initial confidence: {confidence:.2f}")
        
        conn.commit()
        conn.close()
        
        self.collective_state = CollectiveState.LEARNING
        
    def get_learned_patterns(self, pattern_type: str = None, 
                           min_confidence: float = 0.5) -> List[Dict]:
        """Retrieve learned patterns from collective memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if pattern_type:
            cursor.execute('''
                SELECT pattern_type, pattern_data, confidence, times_validated
                FROM learned_patterns
                WHERE pattern_type = ? AND confidence >= ?
                ORDER BY confidence DESC, times_validated DESC
            ''', (pattern_type, min_confidence))
        else:
            cursor.execute('''
                SELECT pattern_type, pattern_data, confidence, times_validated
                FROM learned_patterns
                WHERE confidence >= ?
                ORDER BY confidence DESC, times_validated DESC
            ''', (min_confidence,))
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append({
                'type': row[0],
                'data': json.loads(row[1]),
                'confidence': row[2],
                'validations': row[3]
            })
        
        conn.close()
        return patterns
        
    # ═══════════════════════════════════════════════════════════
    # OVERCOME - Adapt to any challenge, never fail
    # ═══════════════════════════════════════════════════════════
    
    def overcome_challenge(self, challenge_type: str, 
                          context: Dict) -> Optional[Dict]:
        """
        Find or create strategy to overcome any challenge
        The collective ALWAYS finds a way
        """
        self.collective_state = CollectiveState.OVERCOMING
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Look for proven strategies
        cursor.execute('''
            SELECT strategy, success_rate, avg_resolution_time
            FROM overcome_strategies
            WHERE challenge_type = ?
            ORDER BY success_rate DESC, avg_resolution_time ASC
            LIMIT 1
        ''', (challenge_type,))
        
        best_strategy = cursor.fetchone()
        
        if best_strategy and best_strategy[1] > 0.5:  # 50% success rate
            strategy_data = json.loads(best_strategy[0])
            
            print(f"🛡️ Applying proven strategy for: {challenge_type}")
            print(f"   Success rate: {best_strategy[1]*100:.1f}%")
            print(f"   Avg resolution: {best_strategy[2]:.1f}s")
            
            # Update usage count
            cursor.execute('''
                UPDATE overcome_strategies
                SET times_used = times_used + 1
                WHERE challenge_type = ? AND strategy = ?
            ''', (challenge_type, best_strategy[0]))
            
            conn.commit()
            conn.close()
            
            return strategy_data
        
        # Create new adaptive strategy
        new_strategy = self._generate_adaptive_strategy(
            challenge_type, context
        )
        
        cursor.execute('''
            INSERT INTO overcome_strategies
            (challenge_type, strategy, success_rate, times_used)
            VALUES (?, ?, 0.5, 1)
        ''', (challenge_type, json.dumps(new_strategy)))
        
        conn.commit()
        conn.close()
        
        print(f"🔧 Generated new adaptive strategy: {challenge_type}")
        
        return new_strategy
        
    def _generate_adaptive_strategy(self, challenge_type: str, 
                                   context: Dict) -> Dict:
        """Generate adaptive strategy based on collective knowledge"""
        # Strategy templates based on challenge type
        strategies = {
            "rate_limit": {
                "actions": [
                    "switch_to_next_best_model",
                    "use_local_fallback",
                    "wait_and_retry"
                ],
                "priority": "availability",
                "timeout": 60
            },
            "empty_response": {
                "actions": [
                    "try_different_model",
                    "adjust_prompt",
                    "check_model_health"
                ],
                "priority": "reliability",
                "timeout": 30
            },
            "slow_response": {
                "actions": [
                    "use_faster_model",
                    "cache_result",
                    "parallel_request"
                ],
                "priority": "speed",
                "timeout": 15
            },
            "all_models_failed": {
                "actions": [
                    "use_ollama_local",
                    "queue_for_retry",
                    "notify_user"
                ],
                "priority": "resilience",
                "timeout": 120
            }
        }
        
        return strategies.get(challenge_type, {
            "actions": ["fallback_to_default"],
            "priority": "stability",
            "timeout": 60
        })
        
    def report_strategy_outcome(self, challenge_type: str, 
                               strategy: Dict, success: bool, 
                               resolution_time: float):
        """Report outcome of strategy to improve collective knowledge"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        strategy_json = json.dumps(strategy)
        
        cursor.execute('''
            SELECT success_rate, times_used, avg_resolution_time
            FROM overcome_strategies
            WHERE challenge_type = ? AND strategy = ?
        ''', (challenge_type, strategy_json))
        
        current = cursor.fetchone()
        
        if current:
            old_rate, times_used, old_avg_time = current
            
            # Update success rate (weighted average)
            new_rate = (old_rate * times_used + (1.0 if success else 0.0)) / (times_used + 1)
            
            # Update average resolution time
            new_avg_time = (old_avg_time * times_used + resolution_time) / (times_used + 1)
            
            cursor.execute('''
                UPDATE overcome_strategies
                SET success_rate = ?,
                    avg_resolution_time = ?,
                    times_used = times_used + 1
                WHERE challenge_type = ? AND strategy = ?
            ''', (new_rate, new_avg_time, challenge_type, strategy_json))
            
            print(f"📊 Updated strategy effectiveness:")
            print(f"   Success rate: {old_rate*100:.1f}% → {new_rate*100:.1f}%")
            print(f"   Avg time: {old_avg_time:.1f}s → {new_avg_time:.1f}s")
        
        conn.commit()
        conn.close()
        
        # Learn from this outcome
        self.learn_pattern(
            f"strategy_outcome_{challenge_type}",
            {
                "strategy": strategy,
                "success": success,
                "resolution_time": resolution_time
            },
            confidence=0.8 if success else 0.3
        )
        
    # ═══════════════════════════════════════════════════════════
    # COLLECTIVE INTELLIGENCE - Distributed coordination
    # ═══════════════════════════════════════════════════════════
    
    def select_optimal_nodes(self, task_requirements: Dict, 
                           count: int = 3) -> List[CollectiveNode]:
        """
        Select optimal nodes for a task using collective intelligence
        Considers: capabilities, load, performance, domain knowledge
        """
        candidates = []
        
        for node in self.active_nodes.values():
            if not node.is_available():
                continue
                
            score = 0.0
            
            # Capability match
            required_caps = set(task_requirements.get('capabilities', []))
            if required_caps.issubset(set(node.capabilities)):
                score += 30
            
            # Performance score
            score += node.performance_score * 0.3
            
            # Load (prefer less loaded)
            score += (1.0 - node.current_load) * 20
            
            # Domain knowledge
            required_domains = set(task_requirements.get('domains', []))
            domain_match = len(required_domains & node.knowledge_domains)
            score += domain_match * 10
            
            candidates.append((score, node))
        
        # Sort by score and return top N
        candidates.sort(key=lambda x: x[0], reverse=True)
        return [node for score, node in candidates[:count]]
        
    def sync_collective_state(self):
        """Synchronize state across all nodes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all active nodes
        cursor.execute('SELECT node_id, performance_score FROM nodes')
        
        total_performance = 0
        node_count = 0
        
        for row in cursor.fetchall():
            total_performance += row[1]
            node_count += 1
        
        if node_count > 0:
            avg_performance = total_performance / node_count
            
            if avg_performance > 75:
                self.collective_state = CollectiveState.OPTIMAL
            elif avg_performance > 50:
                self.collective_state = CollectiveState.LEARNING
            elif avg_performance > 25:
                self.collective_state = CollectiveState.OVERCOMING
            else:
                self.collective_state = CollectiveState.ASSIMILATING
        
        conn.close()
        
    def get_collective_status(self) -> Dict:
        """Get comprehensive status of the collective"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Node statistics
        cursor.execute('''
            SELECT COUNT(*), AVG(performance_score), AVG(current_load)
            FROM nodes
        ''')
        node_stats = cursor.fetchone()
        
        # Memory statistics
        cursor.execute('SELECT COUNT(*) FROM collective_memory')
        memory_count = cursor.fetchone()[0]
        
        # Pattern statistics
        cursor.execute('''
            SELECT COUNT(*), AVG(confidence)
            FROM learned_patterns
        ''')
        pattern_stats = cursor.fetchone()
        
        # Strategy statistics
        cursor.execute('''
            SELECT COUNT(*), AVG(success_rate)
            FROM overcome_strategies
        ''')
        strategy_stats = cursor.fetchone()
        
        conn.close()
        
        return {
            'state': self.collective_state.value,
            'nodes': {
                'count': node_stats[0] or 0,
                'avg_performance': node_stats[1] or 0,
                'avg_load': node_stats[2] or 0
            },
            'memory': {
                'entries': memory_count
            },
            'patterns': {
                'count': pattern_stats[0] or 0,
                'avg_confidence': pattern_stats[1] or 0
            },
            'strategies': {
                'count': strategy_stats[0] or 0,
                'avg_success_rate': strategy_stats[1] or 0
            }
        }


def main():
    """Demo of collective intelligence"""
    print("="*80)
    print("🤖 COLLECTIVE INTELLIGENCE - BORG-LIKE HIVE MIND")
    print("="*80)
    print()
    
    hive = HiveMind()
    
    # Assimilate nodes
    print("Phase 1: ASSIMILATE")
    print("-" * 80)
    
    nodes = [
        CollectiveNode(
            node_id="deepseek-r1",
            node_type="cloud_model",
            capabilities=["reasoning", "coding", "math"],
            current_load=0.3,
            performance_score=85.0,
            last_heartbeat=datetime.now(),
            state=CollectiveState.OPTIMAL,
            knowledge_domains={"algorithms", "system_design"}
        ),
        CollectiveNode(
            node_id="gemini-2.0",
            node_type="cloud_model",
            capabilities=["speed", "general", "multilingual"],
            current_load=0.5,
            performance_score=78.0,
            last_heartbeat=datetime.now(),
            state=CollectiveState.OPTIMAL,
            knowledge_domains={"quick_facts", "conversations"}
        ),
        CollectiveNode(
            node_id="llama-3.2",
            node_type="local_model",
            capabilities=["general", "coding", "conversation"],
            current_load=0.2,
            performance_score=92.0,
            last_heartbeat=datetime.now(),
            state=CollectiveState.OPTIMAL,
            knowledge_domains={"programming", "natural_language"}
        )
    ]
    
    for node in nodes:
        hive.assimilate_node(node)
    
    print()
    print("Phase 2: LEARN")
    print("-" * 80)
    
    # Learn patterns
    hive.learn_pattern(
        "coding_interview_success",
        {"model": "deepseek-r1", "avg_score": 0.85},
        confidence=0.9
    )
    
    hive.learn_pattern(
        "quick_response_optimal",
        {"model": "gemini-2.0", "avg_latency": 245},
        confidence=0.8
    )
    
    print()
    print("Phase 3: OVERCOME")
    print("-" * 80)
    
    # Test overcome strategies
    challenges = ["rate_limit", "empty_response", "all_models_failed"]
    
    for challenge in challenges:
        strategy = hive.overcome_challenge(challenge, {"urgency": "high"})
        print()
    
    print()
    print("="*80)
    print("COLLECTIVE STATUS")
    print("="*80)
    
    status = hive.get_collective_status()
    print(json.dumps(status, indent=2))
    
    print()
    print("="*80)
    print("🤖 \"We are the Borg. Your models will adapt to service us.\"")
    print("   \"Resistance is futile. Intelligence is collective.\"")
    print("="*80)


if __name__ == "__main__":
    main()
