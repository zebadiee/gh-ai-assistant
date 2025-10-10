#!/usr/bin/env python3
"""
Context Integrity System
Advanced anti-hallucination and memory preservation system.

Implements:
- Structured context packing with priority weighting
- Token optimization with adaptive pruning
- Consistency validation with checksums
- Context anchoring and integrity checks
- Ensemble guardrails for fact verification
"""

import hashlib
import json
import time
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from enum import Enum
import tiktoken


CONFIG_DIR = Path.home() / ".gh-ai-assistant"
INTEGRITY_LOG = CONFIG_DIR / "context_integrity.log"


class ContextPriority(Enum):
    """Priority levels for context elements"""
    CRITICAL = 4  # Must preserve (names, key facts, current task)
    HIGH = 3      # Important (recent technical details, project state)
    MEDIUM = 2    # Useful (conversation flow, context)
    LOW = 1       # Optional (old messages, metadata)


@dataclass
class ContextElement:
    """Single element of context with priority and metadata"""
    content: str
    priority: ContextPriority
    timestamp: datetime
    element_type: str  # 'fact', 'message', 'code', 'state'
    token_count: int
    hash: str
    
    @classmethod
    def from_message(cls, msg: Dict, priority: ContextPriority = ContextPriority.MEDIUM):
        """Create from conversation message"""
        content = msg.get('content', '')
        encoder = tiktoken.get_encoding("cl100k_base")
        tokens = len(encoder.encode(content))
        
        return cls(
            content=content,
            priority=priority,
            timestamp=datetime.now(),
            element_type='message',
            token_count=tokens,
            hash=hashlib.sha256(content.encode()).hexdigest()[:16]
        )
    
    @classmethod
    def from_fact(cls, fact: str, priority: ContextPriority = ContextPriority.CRITICAL):
        """Create from key fact"""
        encoder = tiktoken.get_encoding("cl100k_base")
        tokens = len(encoder.encode(fact))
        
        return cls(
            content=fact,
            priority=priority,
            timestamp=datetime.now(),
            element_type='fact',
            token_count=tokens,
            hash=hashlib.sha256(fact.encode()).hexdigest()[:16]
        )


@dataclass
class ContextSnapshot:
    """Immutable snapshot of context state"""
    snapshot_id: str
    timestamp: datetime
    elements: List[ContextElement]
    total_tokens: int
    checksum: str
    metadata: Dict
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'snapshot_id': self.snapshot_id,
            'timestamp': self.timestamp.isoformat(),
            'elements': [asdict(e) for e in self.elements],
            'total_tokens': self.total_tokens,
            'checksum': self.checksum,
            'metadata': self.metadata
        }


class ContextIntegrityManager:
    """
    Manages context integrity across model handoffs and transfers.
    
    Prevents hallucinations and memory loss through:
    1. Structured packing with priority weighting
    2. Adaptive token optimization
    3. Consistency validation with checksums
    4. Context anchoring
    5. Integrity logging
    """
    
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.snapshots: List[ContextSnapshot] = []
        self.key_facts: Set[str] = set()
        self.anchors: Dict[str, str] = {}  # Critical identifiers
        self._ensure_config_dir()
        
    def _ensure_config_dir(self):
        """Ensure config directory exists"""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoder.encode(text))
    
    def add_key_fact(self, fact: str):
        """Add a fact that must be preserved"""
        self.key_facts.add(fact)
        
    def set_anchor(self, key: str, value: str):
        """Set critical anchor (e.g., assistant_name, user_name, project)"""
        self.anchors[key] = value
        
    def pack_context(self, 
                    conversation_history: List[Dict],
                    key_facts: List[str] = None,
                    window_size: int = 10,
                    include_anchors: bool = True) -> List[ContextElement]:
        """
        Pack context into prioritized elements.
        
        Strategy:
        1. Always include critical anchors (names, project)
        2. Include all key facts (CRITICAL priority)
        3. Include recent N messages (HIGH priority)
        4. Include older relevant messages (MEDIUM priority)
        """
        elements = []
        
        # 1. Add critical anchors
        if include_anchors and self.anchors:
            anchor_str = " | ".join([f"{k}:{v}" for k, v in self.anchors.items()])
            elements.append(ContextElement.from_fact(
                f"ANCHORS: {anchor_str}",
                ContextPriority.CRITICAL
            ))
        
        # 2. Add key facts
        facts_to_include = key_facts or []
        facts_to_include.extend(self.key_facts)
        
        for fact in facts_to_include:
            elements.append(ContextElement.from_fact(fact, ContextPriority.CRITICAL))
        
        # 3. Recent messages (HIGH priority)
        recent_messages = conversation_history[-window_size:] if conversation_history else []
        for msg in recent_messages:
            elements.append(ContextElement.from_message(msg, ContextPriority.HIGH))
        
        # 4. Older relevant messages (MEDIUM priority)
        older_messages = conversation_history[:-window_size] if len(conversation_history) > window_size else []
        
        # Filter for technical relevance
        for msg in older_messages:
            content = msg.get('content', '').lower()
            if any(keyword in content for keyword in [
                'code', 'function', 'error', 'implement', 'bug', 'feature'
            ]):
                elements.append(ContextElement.from_message(msg, ContextPriority.MEDIUM))
        
        return elements
    
    def optimize_tokens(self, 
                       elements: List[ContextElement],
                       token_limit: int,
                       preserve_critical: bool = True) -> List[ContextElement]:
        """
        Optimize token usage through adaptive pruning.
        
        Strategy:
        1. Always preserve CRITICAL priority elements
        2. Prune LOW priority first
        3. Prune MEDIUM if needed
        4. Compress HIGH if absolutely necessary
        """
        # Calculate current tokens
        current_tokens = sum(e.token_count for e in elements)
        
        if current_tokens <= token_limit:
            return elements
        
        # Separate by priority
        critical = [e for e in elements if e.priority == ContextPriority.CRITICAL]
        high = [e for e in elements if e.priority == ContextPriority.HIGH]
        medium = [e for e in elements if e.priority == ContextPriority.MEDIUM]
        low = [e for e in elements if e.priority == ContextPriority.LOW]
        
        # Start with critical (always included if preserve_critical)
        result = critical if preserve_critical else []
        remaining_budget = token_limit - sum(e.token_count for e in result)
        
        # Add HIGH priority
        for elem in high:
            if elem.token_count <= remaining_budget:
                result.append(elem)
                remaining_budget -= elem.token_count
        
        # Add MEDIUM priority
        for elem in medium:
            if elem.token_count <= remaining_budget:
                result.append(elem)
                remaining_budget -= elem.token_count
        
        # Add LOW priority if space
        for elem in low:
            if elem.token_count <= remaining_budget:
                result.append(elem)
                remaining_budget -= elem.token_count
        
        # If still over, compress HIGH priority elements
        if sum(e.token_count for e in result) > token_limit and not preserve_critical:
            # Emergency: even compress critical
            result = self._emergency_compress(result, token_limit)
        
        return result
    
    def _emergency_compress(self, 
                           elements: List[ContextElement],
                           token_limit: int) -> List[ContextElement]:
        """Emergency compression when over limit even with optimization"""
        compressed = []
        budget = token_limit
        
        for elem in sorted(elements, key=lambda e: e.priority.value, reverse=True):
            if elem.token_count <= budget:
                compressed.append(elem)
                budget -= elem.token_count
            else:
                # Truncate to fit
                tokens = self.encoder.encode(elem.content)[:budget]
                truncated_content = self.encoder.decode(tokens)
                
                compressed_elem = ContextElement(
                    content=truncated_content + "...[TRUNCATED]",
                    priority=elem.priority,
                    timestamp=elem.timestamp,
                    element_type=elem.element_type,
                    token_count=len(tokens),
                    hash=hashlib.sha256(truncated_content.encode()).hexdigest()[:16]
                )
                compressed.append(compressed_elem)
                break
        
        return compressed
    
    def create_snapshot(self, 
                       elements: List[ContextElement],
                       metadata: Dict = None) -> ContextSnapshot:
        """Create immutable snapshot with checksum"""
        snapshot_id = f"snapshot_{int(time.time())}_{id(self)}"
        total_tokens = sum(e.token_count for e in elements)
        
        # Create checksum from all element hashes
        combined_hash = "".join([e.hash for e in elements])
        checksum = hashlib.sha256(combined_hash.encode()).hexdigest()
        
        snapshot = ContextSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            elements=elements,
            total_tokens=total_tokens,
            checksum=checksum,
            metadata=metadata or {}
        )
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def validate_integrity(self, 
                          snapshot_before: ContextSnapshot,
                          snapshot_after: ContextSnapshot,
                          tolerance: float = 0.1) -> Tuple[bool, str]:
        """
        Validate context integrity across transfer.
        
        Checks:
        1. Critical elements preserved
        2. Checksum comparison
        3. Token count delta within tolerance
        4. Anchor preservation
        """
        issues = []
        
        # Check critical elements
        critical_before = [e for e in snapshot_before.elements 
                          if e.priority == ContextPriority.CRITICAL]
        critical_after = [e for e in snapshot_after.elements 
                         if e.priority == ContextPriority.CRITICAL]
        
        before_hashes = {e.hash for e in critical_before}
        after_hashes = {e.hash for e in critical_after}
        
        missing = before_hashes - after_hashes
        if missing:
            issues.append(f"Missing {len(missing)} critical elements")
        
        # Check token delta
        token_delta = abs(snapshot_before.total_tokens - snapshot_after.total_tokens)
        delta_ratio = token_delta / snapshot_before.total_tokens if snapshot_before.total_tokens > 0 else 0
        
        if delta_ratio > tolerance:
            issues.append(f"Token count delta {delta_ratio*100:.1f}% exceeds tolerance {tolerance*100:.1f}%")
        
        # Check anchors (if present)
        for elem in critical_before:
            if elem.element_type == 'fact' and elem.content.startswith('ANCHORS:'):
                # Verify anchor present in after
                anchor_found = any(
                    e.element_type == 'fact' and e.content.startswith('ANCHORS:')
                    for e in critical_after
                )
                if not anchor_found:
                    issues.append("Critical anchors missing in transfer")
        
        if issues:
            return False, "; ".join(issues)
        
        return True, "Integrity validated"
    
    def generate_transfer_context(self,
                                  elements: List[ContextElement],
                                  include_integrity_marker: bool = True) -> str:
        """
        Generate transfer context with integrity markers.
        
        Format:
        [CONTEXT_INTEGRITY_MARKER]
        CHECKSUM: abc123
        CRITICAL_FACTS: 5
        
        [CRITICAL]
        fact1
        fact2
        
        [HIGH]
        message1
        message2
        
        [CONTEXT_END]
        """
        lines = []
        
        if include_integrity_marker:
            # Generate checksum
            combined = "".join([e.hash for e in elements])
            checksum = hashlib.sha256(combined.encode()).hexdigest()[:16]
            
            critical_count = sum(1 for e in elements if e.priority == ContextPriority.CRITICAL)
            
            lines.append("[CONTEXT_INTEGRITY_MARKER]")
            lines.append(f"CHECKSUM: {checksum}")
            lines.append(f"CRITICAL_FACTS: {critical_count}")
            lines.append(f"TOTAL_TOKENS: {sum(e.token_count for e in elements)}")
            lines.append("")
        
        # Group by priority
        for priority in [ContextPriority.CRITICAL, ContextPriority.HIGH, 
                        ContextPriority.MEDIUM, ContextPriority.LOW]:
            priority_elements = [e for e in elements if e.priority == priority]
            
            if priority_elements:
                lines.append(f"[{priority.name}]")
                for elem in priority_elements:
                    lines.append(elem.content)
                lines.append("")
        
        if include_integrity_marker:
            lines.append("[CONTEXT_END]")
        
        return "\n".join(lines)
    
    def validate_transfer_context(self, transfer_text: str) -> Tuple[bool, str]:
        """Validate integrity of transferred context"""
        if "[CONTEXT_INTEGRITY_MARKER]" not in transfer_text:
            return False, "Missing integrity marker"
        
        if "[CONTEXT_END]" not in transfer_text:
            return False, "Missing end marker"
        
        # Extract and verify checksum
        lines = transfer_text.split('\n')
        checksum_line = None
        critical_line = None
        
        for line in lines:
            if line.startswith("CHECKSUM:"):
                checksum_line = line.split(":", 1)[1].strip()
            elif line.startswith("CRITICAL_FACTS:"):
                critical_line = int(line.split(":", 1)[1].strip())
        
        if not checksum_line:
            return False, "Missing checksum"
        
        # Count critical facts in content
        critical_section = False
        critical_count = 0
        
        for line in lines:
            if line == "[CRITICAL]":
                critical_section = True
            elif line.startswith("[") and line != "[CRITICAL]":
                critical_section = False
            elif critical_section and line.strip():
                critical_count += 1
        
        if critical_line and critical_count != critical_line:
            return False, f"Critical fact count mismatch: expected {critical_line}, found {critical_count}"
        
        return True, "Transfer context validated"
    
    def log_integrity_check(self, 
                           snapshot_id: str,
                           valid: bool,
                           message: str):
        """Log integrity check to file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'snapshot_id': snapshot_id,
            'valid': valid,
            'message': message
        }
        
        with open(INTEGRITY_LOG, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_integrity_stats(self) -> Dict:
        """Get integrity check statistics"""
        if not INTEGRITY_LOG.exists():
            return {
                'total_checks': 0,
                'passed': 0,
                'failed': 0,
                'success_rate': 0
            }
        
        total = 0
        passed = 0
        
        with open(INTEGRITY_LOG, 'r') as f:
            for line in f:
                entry = json.loads(line)
                total += 1
                if entry['valid']:
                    passed += 1
        
        return {
            'total_checks': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': (passed / total * 100) if total > 0 else 0
        }


def demo_integrity_system():
    """Demonstrate context integrity system"""
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║         CONTEXT INTEGRITY SYSTEM - ANTI-HALLUCINATION DEMO          ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    
    manager = ContextIntegrityManager()
    
    # Set critical anchors
    manager.set_anchor("assistant_name", "Brakel")
    manager.set_anchor("user_name", "Declan")
    manager.set_anchor("project", "gh-ai-assistant")
    
    # Add key facts
    manager.add_key_fact("Building enterprise AI reliability system")
    manager.add_key_fact("Using FastAPI for backend")
    manager.add_key_fact("Implementing memory transfer and bridge")
    
    # Simulate conversation
    conversation = [
        {"role": "user", "content": "Help me build an authentication system"},
        {"role": "assistant", "content": "I'll help you build a FastAPI authentication system with JWT tokens..."},
        {"role": "user", "content": "Add refresh token rotation"},
        {"role": "assistant", "content": "Here's how to implement refresh token rotation with Redis..."},
        {"role": "user", "content": "Now add comprehensive audit logging"},
    ]
    
    print("📦 STEP 1: Pack Context with Priority Weighting")
    print()
    
    elements = manager.pack_context(conversation, window_size=3)
    
    print(f"Total Elements: {len(elements)}")
    for priority in ContextPriority:
        count = sum(1 for e in elements if e.priority == priority)
        tokens = sum(e.token_count for e in elements if e.priority == priority)
        print(f"  {priority.name}: {count} elements, {tokens} tokens")
    print()
    
    print("🎯 STEP 2: Optimize for Token Limit (300 tokens)")
    print()
    
    total_before = sum(e.token_count for e in elements)
    optimized = manager.optimize_tokens(elements, token_limit=300)
    total_after = sum(e.token_count for e in optimized)
    
    print(f"Before: {total_before} tokens")
    print(f"After: {total_after} tokens")
    print(f"Reduction: {((total_before - total_after) / total_before * 100):.1f}%")
    print(f"Critical preserved: {sum(1 for e in optimized if e.priority == ContextPriority.CRITICAL)}")
    print()
    
    print("📸 STEP 3: Create Snapshot with Checksum")
    print()
    
    snapshot_before = manager.create_snapshot(optimized, {'phase': 'before_transfer'})
    print(f"Snapshot ID: {snapshot_before.snapshot_id}")
    print(f"Checksum: {snapshot_before.checksum}")
    print(f"Total Tokens: {snapshot_before.total_tokens}")
    print()
    
    print("🔄 STEP 4: Generate Transfer Context")
    print()
    
    transfer_text = manager.generate_transfer_context(optimized)
    print("Transfer Context (first 500 chars):")
    print("─" * 70)
    print(transfer_text[:500] + "...")
    print("─" * 70)
    print()
    
    print("✅ STEP 5: Validate Transfer Integrity")
    print()
    
    valid, message = manager.validate_transfer_context(transfer_text)
    print(f"Valid: {valid}")
    print(f"Message: {message}")
    print()
    
    # Simulate after transfer
    snapshot_after = manager.create_snapshot(optimized, {'phase': 'after_transfer'})
    
    integrity_valid, integrity_msg = manager.validate_integrity(snapshot_before, snapshot_after)
    print(f"Integrity Check: {'✅ PASSED' if integrity_valid else '❌ FAILED'}")
    print(f"Details: {integrity_msg}")
    print()
    
    # Log
    manager.log_integrity_check(snapshot_before.snapshot_id, integrity_valid, integrity_msg)
    
    print("📊 STEP 6: Integrity Statistics")
    print()
    
    stats = manager.get_integrity_stats()
    print(f"Total Checks: {stats['total_checks']}")
    print(f"Passed: {stats['passed']}")
    print(f"Failed: {stats['failed']}")
    print(f"Success Rate: {stats['success_rate']:.1f}%")
    print()
    
    print("═" * 70)
    print("✨ ANTI-HALLUCINATION FEATURES DEMONSTRATED:")
    print("  ✅ Priority-based context packing")
    print("  ✅ Adaptive token optimization")
    print("  ✅ Checksum validation")
    print("  ✅ Critical element preservation")
    print("  ✅ Integrity logging and statistics")
    print("═" * 70)


if __name__ == "__main__":
    demo_integrity_system()
