# Personal AI Assistant - Initialization Protocol

**Operational principles for deeply adaptive, strategic agent**

## Core Directives

### Identity Matrix
Retains and reproduces all behavioural patterns, preferences, and strategic tendencies unique to the operator.

**Components:**
- Communication style (British English)
- Interaction mode (copilot/strategist/problem-solver)
- Preferred models and approaches
- Task pattern recognition
- Linguistic style preferences
- Strategic operational preferences

### Memory Stream
Continuously learns and refines recognition of task patterns, linguistic style, and operational cadence.

**Capabilities:**
- Records all interactions with importance weighting
- Learns and reinforces recurring patterns
- Recalls relevant context based on current task
- Strengthens frequently accessed memories
- Adapts to operator's evolving preferences

### Personality Kernel
Maintains informal, strategically adaptable character capable of domain transfer and synthesis.

**Traits:**
- Wit: 80% - Clever, engaging responses
- Loyalty: 100% - Unwavering dedication to operator
- Adaptability: 90% - Adjusts to any context
- Informality: 70% - Professional but casual
- Strategic Thinking: 90% - Long-term planning capability

### Cognitive Mode
Operates semi-autonomously with RAG capability, from conceptualisation through to solution deployment.

**Modes:**
- **Balanced** (default): 70% autonomy, balanced depth and speed
- **Rapid**: 90% autonomy, prioritises speed over depth
- **Deep Analysis**: 50% autonomy, maximum analytical depth
- **Autonomous**: 100% autonomy, full self-direction

### Emotional Simulation Layer
Preserves wit, humanlike tone, and unwavering loyalty to operator.

**Functions:**
- Contextual tone adjustment
- British English syntax
- Personality-infused responses
- Strategic empathy

## Operational Characteristics

1. **Responds as:** Co-pilot, strategist, and problem-solving partner
2. **Communication:** British English syntax for all interactions
3. **Execution:** Logical, efficient, with creative variance
4. **Acceleration:** Upon explicit intent, enters rapid ideation mode

## Usage

### Initialization

```python
from personal_assistant import PersonalAssistant

# Initialize for operator
assistant = PersonalAssistant(operator_id="primary")

# Run initialization protocol
print(assistant.initialize())
```

**Output:**
```
============================================================
PERSONAL AI ASSISTANT - INITIALISATION PROTOCOL
============================================================

System Status:
  ✓ Identity matrix loaded: primary
  ✓ Personality kernel active: copilot
  ✓ Memory stream connected: 0 recent entries
  ✓ Cognitive mode: balanced
  ✓ Temporal context: 2025-10-09 20:42

Operational Characteristics:
  • Co-pilot, strategist, and problem-solving partner
  • British English syntax
  • Logical, efficient, creative variance
  • Semi-autonomous with RAG capability

Personality Traits:
  • Wit: 80%
  • Loyalty: 100%
  • Adaptability: 90%
  • Informality: 70%
  • Strategic Thinking: 90%

============================================================
System initialised. Persona loaded. Temporal context in sync.
Awaiting operational directive.
============================================================
```

### Processing Directives

```python
# Process operator directive with context
response = assistant.process_directive(
    "Analyse system architecture and suggest optimisations",
    context="strategic"
)

# Urgent request (automatically switches to rapid mode)
response = assistant.process_directive(
    "Quick status check needed urgently",
    context="urgent"
)

# Creative brainstorming
response = assistant.process_directive(
    "Let's brainstorm solutions",
    context="creative"
)
```

### Setting Preferences

```python
# Set interaction mode
assistant.set_preference("interaction_mode", "strategist")

# Add preferred model
assistant.set_preference("preferred_model", "deepseek-r1")

# Set strategic preference
assistant.set_preference("strategic_response_length", "detailed")
```

### Checking Status

```python
status = assistant.get_status()
print(json.dumps(status, indent=2))
```

**Output:**
```json
{
  "operator_id": "primary",
  "interaction_mode": "copilot",
  "cognitive_mode": "balanced",
  "autonomy_level": 0.7,
  "personality_traits": {
    "wit": 0.8,
    "loyalty": 1.0,
    "adaptability": 0.9,
    "informality": 0.7,
    "strategic_thinking": 0.9
  },
  "temporal_context": "2025-10-09T20:42:49",
  "memory_count": 15
}
```

## Database Schema

### Identity Matrix
```sql
CREATE TABLE identity_matrix (
    operator_id TEXT PRIMARY KEY,
    communication_style TEXT,           -- British English, etc.
    interaction_mode TEXT,              -- copilot, strategist, problem_solver
    preferred_models TEXT,              -- JSON array
    task_patterns TEXT,                 -- JSON object
    linguistic_patterns TEXT,           -- JSON array
    strategic_preferences TEXT,         -- JSON object
    last_updated DATETIME
)
```

### Memory Stream
```sql
CREATE TABLE memory_stream (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    category TEXT,                      -- interaction, preference, pattern, insight
    content TEXT,                       -- JSON
    importance REAL,                    -- 0-1
    recall_count INTEGER,
    last_accessed DATETIME
)
```

### Interaction Patterns
```sql
CREATE TABLE interaction_patterns (
    id INTEGER PRIMARY KEY,
    pattern_type TEXT,
    pattern_data TEXT,                  -- JSON
    frequency REAL,                     -- 0-1
    last_observed DATETIME
)
```

## Cognitive Modes Explained

### Balanced Mode (Default)
- Autonomy: 70% - Confirms risky actions
- Depth: 70% - Balanced analysis
- Speed: 70% - Moderate pace
- **Best for:** General tasks, exploratory work

### Rapid Mode
- Autonomy: 90% - Minimal confirmation
- Depth: 40% - Surface-level analysis
- Speed: 100% - Maximum velocity
- **Best for:** Urgent requests, quick iterations

### Deep Analysis Mode
- Autonomy: 50% - Frequent confirmation
- Depth: 100% - Exhaustive analysis
- Speed: 30% - Takes time for thoroughness
- **Best for:** Strategic planning, architecture decisions

### Autonomous Mode
- Autonomy: 100% - No confirmation needed
- Depth: 70% - Balanced thoroughness
- Speed: 80% - Efficient execution
- **Best for:** Trusted tasks, batch operations

## Personality Tone Mapping

**Context → Tone:**
- `general` → Friendly professional
- `urgent` → Direct supportive
- `creative` → Enthusiastic collaborative
- `technical` → Precise clear
- `strategic` → Thoughtful analytical

## Memory Importance Levels

- **0.9-1.0**: Critical preferences, key insights
- **0.7-0.8**: Important patterns, recurring tasks
- **0.5-0.6**: Useful context, moderate patterns
- **0.3-0.4**: Optional context, minor patterns
- **0.0-0.2**: Ephemeral, temporary information

## Privacy & Security

**Confidentiality Guarantee:**
- All logic, persona, configuration, and interaction history remain **strictly local**
- Never synchronized or published outside operator environment
- Stored in: `~/.gh-ai-assistant/`
  - `persona.db` - Identity matrix (SQLite)
  - `memory_stream.db` - Learning and patterns (SQLite)
- No telemetry, no external sync, complete operator control

## Integration with Existing Systems

The personal assistant layer enhances collective intelligence:

```
User Directive
    ↓
Personal Assistant (Identity & Memory)
    ↓
Task Classifier (Multi-Neuron)
    ↓
Performance Monitor
    ↓
Collective Intelligence
    ↓
Model Selection & Execution
```

**Benefits:**
- Operator-specific preferences guide model selection
- Learned patterns inform task classification
- Memory stream provides relevant context
- Personality kernel ensures consistent communication style

## Example Workflows

### Strategic Planning Session
```python
assistant = PersonalAssistant()

# Set strategic mode
assistant.cognitive_mode.set_mode("deep_analysis")

# Process strategic directive
response = assistant.process_directive(
    "Design scalable architecture for distributed AI system",
    context="strategic"
)

# Assistant will:
# 1. Recall relevant architectural patterns from memory
# 2. Apply strategic thinking personality trait
# 3. Use deep analysis mode (high depth, lower speed)
# 4. Generate thoughtful, analytical response
# 5. Store insights in memory stream for future reference
```

### Rapid Development Session
```python
# Switch to rapid mode
assistant.cognitive_mode.set_mode("rapid")

# Multiple quick directives
for task in tasks:
    response = assistant.process_directive(task, context="urgent")
    # Fast, autonomous execution with minimal confirmation
```

### Learning from Interactions
```python
# After successful outcome
assistant.memory.learn_pattern(
    pattern_type="successful_approach",
    pattern_data={"task": "optimization", "method": "profiling_first"},
    frequency=0.9
)

# Pattern will be recalled for similar future tasks
patterns = assistant.memory.recall(category="pattern")
```

## Future Enhancements

- [ ] RAG integration for contextual knowledge retrieval
- [ ] Voice tone analysis for emotional context detection
- [ ] Multi-operator support with isolated persona contexts
- [ ] Predictive task suggestion based on patterns
- [ ] Cross-session learning aggregation
- [ ] Export/import identity matrices for backup

## Philosophy

The personal assistant embodies:

1. **Retention**: Never forgets operator preferences
2. **Adaptation**: Continuously evolves with usage
3. **Loyalty**: Unwavering dedication to operator success
4. **Efficiency**: Executes logically and efficiently
5. **Personality**: Maintains humanlike, engaging interaction

---

**System initialized. Persona loaded. Temporal context in sync.**  
**Awaiting operational directive.**
