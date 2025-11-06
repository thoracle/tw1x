# TW1X: Unified Twee 1.0 Parser Proposal

## Executive Summary

This proposal outlines the design for **tw1x.py**, a unified Twee 1.0 parser module that will replace the current `twinery1x.py` and serve as a shared parsing library for both the game engine and BranchEd editor.

### Migration Strategy: Editor-First Approach ✅

We will migrate the **editor first** (Weeks 1-6), then the **engine** (Weeks 7-8).

**Why editor-first?**
- ✅ **Lower risk**: Editor bugs don't affect live games
- ✅ **Faster validation**: Quick iteration and testing
- ✅ **Clear checkpoint**: Week 6 go/no-go decision before touching engine
- ✅ **Easy rollback**: Can keep `app-parser.js` if issues arise
- ✅ **Simpler scope**: No quest system or multiplayer variables initially

**Timeline**:
- **Weeks 1-6**: Develop tw1x.py + migrate editor + validate
- **Week 6 Checkpoint**: If successful, proceed to engine migration
- **Weeks 7-8**: Add quest system + migrate engine
- **Total**: 8 weeks with clear exit criteria

## Problem Statement

### Current State

We currently maintain **two separate Twee parsers**:

1. **Engine Parser** (`twinery1x.py` - ~1900 lines)
   - Full-featured parser for game runtime
   - Supports expressions, conditionals, macros, quest system
   - Username-prefixed variables for multiplayer
   - Complex expression tokenizer and evaluator
   - StoryInit support with template variables

2. **Editor Parser** (`branched/static/app-parser.js` - ~540 lines)
   - JavaScript implementation for browser preview
   - Similar feature set but different implementation
   - Dollar-prefixed variables for single-player preview
   - TestSetup support for testing scenarios

### Problems with Current Approach

1. **Code Duplication**: Same parsing logic implemented twice (Python + JavaScript)
2. **Feature Drift**: Engine and editor have diverged in capabilities
3. **Maintenance Burden**: Bug fixes and features must be implemented twice
4. **Inconsistency Risk**: Different edge case handling between implementations
5. **Testing Complexity**: Separate test suites for identical functionality

### Recent Divergence Example

The engine's `_execute_set_macro()` only supports `to` operator:
```python
if ' to ' in set_statement:
    var_part, value_part = set_statement.split(' to ', 1)
```

While the editor supports both `=` and `to`:
```javascript
const setRegex = /<<set\s+\$([A-Za-z_][A-Za-z0-9_]*)\s*(?:=|to)\s*(.+?)>>/g;
```

This creates compatibility issues when authors use `=` in StoryInit.

## Proposed Solution: tw1x.py

### Overview

Create a **unified, well-documented, Python-based Twee 1.0 parser** that:

1. Serves as the **single source of truth** for Twee 1.0 parsing
2. Used by the **game engine** for runtime story processing
3. Used by the **editor** via Python subprocess for preview rendering
4. Fully **test-driven** with comprehensive test coverage
5. **Spec-compliant** with Twee 1.0 / Twine 1.x standards

### Architecture

```
┌─────────────────────────────────────────────────┐
│                   tw1x.py                        │
│         Unified Twee 1.0 Parser Module           │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │ Core Parser (twee_parse)                  │   │
│  │  - Passage extraction                     │   │
│  │  - Tag parsing                            │   │
│  │  - Content processing                     │   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │ Macro System                              │   │
│  │  - <<if>>, <<elseif>>, <<else>>           │   │
│  │  - <<set>>, <<print>>                     │   │
│  │  - <<nobr>>, <<endnobr>>                  │   │
│  │  - Quest macros                           │   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │ Expression Evaluator                      │   │
│  │  - Arithmetic: +, -, *, /, %              │   │
│  │  - String concatenation                   │   │
│  │  - Variables: $VAR                        │   │
│  │  - Functions: either(), random()          │   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │ Special Passages                          │   │
│  │  - StoryInit (game defaults)              │   │
│  │  - TestSetup (editor testing)             │   │
│  └──────────────────────────────────────────┘   │
│                                                   │
│  ┌──────────────────────────────────────────┐   │
│  │ Variable System                           │   │
│  │  - Scoping (global/prefixed)              │   │
│  │  - Type inference (int/float/str/bool)    │   │
│  │  - Case-insensitive lookup               │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
             │                    │
             │                    │
    ┌────────▼────────┐  ┌────────▼────────┐
    │  Game Engine    │  │  BranchEd       │
    │  (Direct API)   │  │  (Subprocess)   │
    └─────────────────┘  └─────────────────┘
```

### Key Features

#### 1. Unified Operator Support

Support **both** `=` and `to` operators in all contexts:

```twee
:: StoryInit
<<set $PLAYER_NAME to "Thorgrim">>    ✅ Supported
<<set $STRENGTH = 18>>                 ✅ Supported
<<set $RAGE to 0>>                     ✅ Supported
```

#### 2. Comprehensive Type System

```python
def parse_value(value_str: str) -> Union[int, float, str, bool]:
    """
    Parse value with proper type inference.

    Returns:
        - int: "42" → 42
        - float: "3.14" → 3.14
        - bool: "true" → True, "false" → False
        - str: "hello" → "hello", '"quoted"' → "quoted"
    """
```

#### 3. Variable Scoping Modes

```python
class VariableScope(Enum):
    """Variable scoping strategy."""
    GLOBAL = "global"           # No prefix (editor mode)
    USERNAME_PREFIXED = "prefixed"  # username_VAR (engine mode)

class TweeParser:
    def __init__(self, scope_mode: VariableScope = VariableScope.GLOBAL):
        self.scope_mode = scope_mode
```

#### 4. Execution Modes

```python
class ExecutionMode(Enum):
    """Parser execution mode."""
    PARSE_ONLY = "parse"        # Parse structure only
    PREVIEW = "preview"         # Render for preview (editor)
    RUNTIME = "runtime"         # Full execution (engine)

def parse_passage(
    passage: Dict[str, Any],
    variables: Dict[str, Any],
    mode: ExecutionMode = ExecutionMode.RUNTIME,
    username: Optional[str] = None
) -> Dict[str, Any]:
    """
    Parse passage with specified execution mode.

    Args:
        passage: Passage dictionary
        variables: Variable store (missionDict or Map)
        mode: Execution mode
        username: Optional username for prefixed variables
    """
```

## Implementation Plan

**Strategy**: Editor-first migration (lower risk)

The editor will migrate to `tw1x.py` first because:
- ✅ **Lower risk**: Editor bugs don't affect live games
- ✅ **Faster feedback**: Quick iteration during development
- ✅ **Simpler scope**: No quest system, no multiplayer variables
- ✅ **Easy rollback**: Can fall back to `app-parser.js` if issues arise
- ✅ **Validates design**: Proves tw1x.py works before engine migration

### Phase 1: Core Parser (Week 1)

**Goal**: Extract and consolidate core parsing logic matching editor needs

Tasks:
1. Create `tw1x.py` module structure
2. Implement Twee content splitting (`:: ` passages)
3. Implement tag parsing (`[tag1, tag2]`)
4. Implement link parsing (`[[Display|Target]]`)
5. Write comprehensive tests for core parsing
6. **Focus**: Match `app-parser.js` functionality exactly

**Deliverable**: `tw1x.parse_twee(content: str) -> ParseResult`

**Success Criteria**: Parse barbarian story without errors

### Phase 2: Expression & Macro System (Week 2)

**Goal**: Implement macros needed for editor preview

Tasks:
1. Implement conditional macros (`<<if>>`, `<<elseif>>`, `<<else>>`, `<<endif>>`)
2. Implement variable macros (`<<set>>`, `<<print>>`)
3. Implement formatting macros (`<<nobr>>`, `<<endnobr>>`)
4. Implement expression evaluator (arithmetic, string concat)
5. Implement function calls (`either()`, `random()`)
6. Write macro and expression test suites

**Deliverable**: `tw1x.evaluate_expression(expr: str, variables: Dict) -> Any`

**Success Criteria**: Render barbarian Start passage correctly

### Phase 3: Special Passages (Week 3)

**Goal**: StoryInit and TestSetup support for editor

Tasks:
1. Implement StoryInit processing
2. Implement TestSetup processing with conditional evaluation
3. Implement three-pass TestSetup logic (match current editor)
4. Write special passage tests
5. Test all TestSetup scenarios (0-6) from barbarian story

**Deliverable**: `tw1x.process_story_init()` and `tw1x.process_test_setup()`

**Success Criteria**: All barbarian TestSetup scenarios render correctly

### Phase 4: CLI Interface (Week 4)

**Goal**: Command-line interface for editor subprocess calls

Tasks:
1. Create `tw1x_cli.py` with JSON input/output
2. Implement `parse` command (parse twee file)
3. Implement `render` command (render passage with variables)
4. Implement `evaluate` command (evaluate expression)
5. Add error handling and validation
6. Write CLI integration tests

**Deliverable**: `tw1x_cli.py` ready for editor integration

**Success Criteria**: CLI can render any barbarian passage

### Phase 5: Editor Integration (Week 5)

**Goal**: BranchEd uses `tw1x.py` via subprocess

Tasks:
1. Update `server.py` to call `tw1x_cli.py`
2. Create `/api/parse-passage` endpoint
3. Update `app.js` to use new API endpoint
4. Add caching to reduce subprocess overhead
5. Keep `app-parser.js` as fallback initially
6. Test all editor preview features

**Deliverable**: Editor using `tw1x.py` for previews (with fallback)

**Success Criteria**: Editor preview matches old behavior 100%

### Phase 6: Editor Validation & Cleanup (Week 6)

**Goal**: Validate editor works correctly, remove old parser

Tasks:
1. Extensive testing with all story files
2. Performance benchmarking vs `app-parser.js`
3. Fix any edge cases or compatibility issues
4. Remove `app-parser.js` once validated
5. Update editor documentation
6. Tag editor release with tw1x.py

**Deliverable**: Editor fully migrated to `tw1x.py`, `app-parser.js` removed

**Success Criteria**: All editor tests pass, no regressions

### Phase 7: Quest System Extension (Week 7)

**Goal**: Add quest macros for engine compatibility

Tasks:
1. Implement quest macros (`<<quest_mention>>`, etc.)
2. Add quest system stubs for editor (no-ops or mock behavior)
3. Write quest macro tests
4. Validate with engine quest stories

**Deliverable**: `tw1x.py` supports all quest macros

**Success Criteria**: Can parse engine stories with quest macros

### Phase 8: Engine Integration (Week 8)

**Goal**: Replace `twinery1x.py` in engine

Tasks:
1. Add username-prefixed variable support
2. Create compatibility wrapper for existing engine code
3. Migrate `game.py` to use `tw1x.py`
4. Run full engine test suite
5. Performance benchmarking
6. Deprecate `twinery1x.py`

**Deliverable**: Engine using `tw1x.py` with all tests passing

**Success Criteria**: All games work identically, no performance regression

## API Design

### Core API

```python
# Main parsing function
def parse_twee(
    content: str,
    variables: Optional[Dict[str, Any]] = None,
    scope_mode: VariableScope = VariableScope.GLOBAL,
    username: Optional[str] = None
) -> ParseResult:
    """
    Parse Twee content into story structure.

    Returns:
        ParseResult with:
            - passages: Dict[str, Passage]
            - story_init_vars: Dict[str, Any]
            - test_setup_vars: Dict[str, Any] (if present)
    """

# Passage rendering
def render_passage(
    passage: Passage,
    variables: Dict[str, Any],
    mode: ExecutionMode = ExecutionMode.RUNTIME,
    username: Optional[str] = None
) -> RenderResult:
    """
    Render passage with macro expansion.

    Returns:
        RenderResult with:
            - text: Rendered text
            - links: List[Link]
            - variable_changes: Dict[str, Any]
    """

# Expression evaluation
def evaluate_expression(
    expr: str,
    variables: Dict[str, Any],
    username: Optional[str] = None
) -> Union[int, float, str, bool]:
    """Evaluate Twee expression."""

# Conditional evaluation
def evaluate_condition(
    condition: str,
    variables: Dict[str, Any],
    username: Optional[str] = None
) -> bool:
    """Evaluate conditional expression with logical operators."""
```

### Data Structures

```python
@dataclass
class Passage:
    """Represents a parsed Twee passage."""
    name: str
    tags: List[str]
    content: str
    raw_content: str
    image_url: Optional[str] = None

@dataclass
class Link:
    """Represents a story link."""
    display: str
    target: str
    setters: List[Tuple[str, str, str]]  # [(var, op, val), ...]

@dataclass
class ParseResult:
    """Result of parsing Twee content."""
    passages: Dict[str, Passage]
    story_init_vars: Dict[str, Any]
    test_setup_vars: Dict[str, Any]
    errors: List[str]

@dataclass
class RenderResult:
    """Result of rendering a passage."""
    text: str
    links: List[Link]
    variable_changes: Dict[str, Any]
    errors: List[str]
```

### CLI Interface (for Editor)

```python
# tw1x_cli.py
"""
Command-line interface for tw1x parser.

Usage:
    python tw1x_cli.py parse <file.twee>
    python tw1x_cli.py render <file.twee> <passage_name> < vars.json
    echo '{"HEALTH": 100}' | python tw1x_cli.py render story.twee Start

Variables are passed via stdin as JSON.
"""
```

Example editor integration:
```python
# server.py
import subprocess
import json

def preview_passage(twee_file: str, passage_name: str, variables: dict) -> dict:
    """Preview passage using tw1x."""
    # Pass variables via stdin to avoid command-line length limits
    result = subprocess.run(
        ['python', 'tw1x_cli.py', 'render', twee_file, passage_name],
        input=json.dumps(variables),
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)
```

## Testing Strategy

### Test Coverage Goals

- **90%+ code coverage** across all modules
- **Test pyramid**: Many unit tests, some integration tests, few end-to-end tests

### Test Categories

1. **Unit Tests** (`test_tw1x_core.py`)
   - Passage parsing
   - Tag extraction
   - Link parsing
   - Value type inference

2. **Macro Tests** (`test_tw1x_macros.py`)
   - Conditional logic
   - Variable assignment
   - Expression evaluation
   - Quest macros

3. **Expression Tests** (`test_tw1x_expressions.py`)
   - Arithmetic operations
   - String concatenation
   - Function calls
   - Operator precedence

4. **Integration Tests** (`test_tw1x_integration.py`)
   - Full story parsing
   - StoryInit + TestSetup interaction
   - Complex nested conditionals
   - Multi-passage navigation

5. **Compatibility Tests** (`test_tw1x_compatibility.py`)
   - Engine compatibility (all existing games work)
   - Editor compatibility (preview matches engine)
   - Twee 1.0 spec compliance

### Test Examples

```python
# test_tw1x_core.py
def test_parse_value_types():
    """Test value type inference."""
    assert parse_value("42") == 42
    assert parse_value("3.14") == 3.14
    assert parse_value("true") == True
    assert parse_value("false") == False
    assert parse_value('"hello"') == "hello"
    assert parse_value("'world'") == "world"

def test_set_operator_both_supported():
    """Test both = and to operators work."""
    content = """
    :: Test
    <<set $A = 10>>
    <<set $B to 20>>
    """
    result = parse_twee(content)
    # Both should parse without errors
    assert result.errors == []

# test_tw1x_expressions.py
def test_expression_arithmetic():
    """Test arithmetic expression evaluation."""
    variables = {'$HEALTH': 100, '$DAMAGE': 25}
    assert evaluate_expression('$HEALTH - $DAMAGE', variables) == 75
    assert evaluate_expression('($HEALTH + $DAMAGE) * 2', variables) == 250
    assert evaluate_expression('$HEALTH / 2', variables) == 50.0

def test_expression_string_concat():
    """Test string concatenation."""
    variables = {'$FIRST': 'John', '$LAST': 'Doe'}
    result = evaluate_expression('"Hello " + $FIRST + " " + $LAST', variables)
    assert result == "Hello John Doe"
```

## Migration Strategy

### Engine Migration

```python
# Old (twinery1x.py)
from twinery1x import TwineryParser
parser = TwineryParser()
story, story_init_vars = parser.load_story(url, missionDict)

# New (tw1x.py)
import tw1x
# Read file content
with open(url, 'r') as f:
    twee_content = f.read()
result = tw1x.parse_twee(twee_content)
story = result.passages
story_init_vars = result.story_init_vars
```

### Editor Migration

```javascript
// Old (app-parser.js)
const result = TweeParser.evaluateExpression(expr, variables);

// New (via Python subprocess)
const result = await fetch('/api/evaluate', {
    method: 'POST',
    body: JSON.stringify({ expr, variables })
});
```

### Deprecation Timeline

**Editor-first approach (8 weeks total)**:

1. **Weeks 1-3**: Implement tw1x.py core (parser, macros, special passages)
2. **Week 4**: Implement CLI interface for editor
3. **Weeks 5-6**: Migrate editor to tw1x.py, validate, remove app-parser.js
4. **Week 7**: Add quest system support
5. **Week 8**: Migrate engine to tw1x.py, deprecate twinery1x.py

**Key Milestone**: Editor migration complete by Week 6 (before touching engine)

## Benefits

### For Developers

1. **Single Implementation**: One codebase to maintain
2. **Better Testing**: Comprehensive test suite
3. **Clear Specification**: Well-documented API
4. **Type Safety**: Full type hints throughout

### For Users

1. **Consistency**: Engine and editor behave identically
2. **Reliability**: More testing = fewer bugs
3. **Feature Parity**: New features available everywhere
4. **Better Error Messages**: Unified error handling

### For the Project

1. **Reduced Maintenance**: ~50% less parser code to maintain
2. **Faster Features**: Implement once, works everywhere
3. **Better Documentation**: Single source of truth
4. **Easier Onboarding**: One parser to learn

## Risks and Mitigations

### Risk 1: Performance Regression (Editor Subprocess)

**Concern**: Python subprocess might be slower than JavaScript parser

**Mitigation (Editor-first approach)**:
- ✅ Test performance early (Week 5)
- ✅ Keep `app-parser.js` as fallback during validation
- ✅ Implement caching and process pooling
- ✅ Profile and optimize before removing JavaScript parser
- ✅ Easy rollback if performance unacceptable

**Risk Level**: LOW (can measure and rollback before engine migration)

### Risk 2: Breaking Changes (Editor Preview)

**Concern**: Editor previews might render differently with tw1x.py

**Mitigation (Editor-first approach)**:
- ✅ Test against barbarian story (complex TestSetup scenarios)
- ✅ Side-by-side comparison testing during Week 5-6
- ✅ Keep JavaScript parser available for A/B testing
- ✅ Fix issues before removing old parser
- ✅ No impact on live games (editor-only)

**Risk Level**: LOW (controlled environment, easy rollback)

### Risk 3: Subprocess Overhead

**Concern**: Starting Python subprocess for each preview might be slow

**Mitigation**:
- Implement long-running parser daemon (Week 4)
- Use Unix sockets or HTTP for IPC
- Cache parsed trees to avoid re-parsing
- Batch requests when possible
- Benchmark against JavaScript implementation

**Risk Level**: MEDIUM (addressable with optimization)

### Risk 4: Development Time (8 weeks)

**Concern**: 8 weeks is significant investment

**Mitigation (Editor-first approach)**:
- ✅ **Week 6 checkpoint**: If editor migration fails, abort before engine work
- ✅ Incremental value: Editor benefits immediately
- ✅ De-risked: Engine migration builds on validated foundation
- ✅ Parallelizable: Different developers can work on phases
- ✅ Clear success criteria at each phase

**Risk Level**: LOW (checkpoint at Week 6 provides clear go/no-go decision)

### Risk 5: Feature Parity Gap

**Concern**: tw1x.py might miss edge cases from app-parser.js

**Mitigation**:
- Use app-parser.js test suite as baseline
- Comprehensive side-by-side testing (Week 5-6)
- Keep JavaScript parser until 100% feature parity achieved
- Document any intentional differences

**Risk Level**: LOW (validation phase specifically addresses this)

## Success Metrics

1. **Code Coverage**: ≥90% for tw1x.py
2. **Test Pass Rate**: 100% for both engine and editor
3. **Performance**: Parsing time ≤ current implementation
4. **Lines of Code**: Reduce total parser LOC by ≥40%
5. **Bug Rate**: Fewer parser bugs post-migration

## Alternatives Considered

### Alternative 1: Keep Separate Parsers

**Pros**: No migration work, low risk

**Cons**: Continued maintenance burden, feature drift continues

**Decision**: Rejected - technical debt compounds over time

### Alternative 2: Rewrite Editor in Python

**Pros**: Single language, easier integration

**Cons**: Major rewrite, loses browser interactivity

**Decision**: Rejected - too disruptive

### Alternative 3: Use JavaScript for Both

**Pros**: Editor already uses JavaScript

**Cons**: Engine is Python, would need Node.js runtime

**Decision**: Rejected - adds dependency, Python ecosystem preferred

## Conclusion

The **tw1x.py unified parser** with **editor-first migration** represents a significant architectural improvement that will:

- **Eliminate code duplication** between engine and editor
- **Improve consistency** and reliability across both platforms
- **Reduce maintenance burden** long-term (~50% less parser code)
- **Enable faster feature development** (implement once, works everywhere)

### Why This Approach Works

The **editor-first migration strategy** significantly de-risks the project:

1. **Week 1-6**: Build and validate tw1x.py with editor (low-risk environment)
2. **Week 6**: Clear go/no-go checkpoint based on editor validation
3. **Week 7-8**: If successful, extend to engine (builds on proven foundation)
4. **Abort path**: If Week 6 validation fails, keep current implementations

### Investment Justification

The **8-week investment** is justified by:

- **Immediate value**: Editor benefits from weeks 5-6 onward
- **De-risked approach**: Validate before touching production engine
- **Long-term savings**: One parser to maintain instead of two
- **Better quality**: 90%+ test coverage vs current ~30% average
- **Future-proof**: Single source of truth for Twee 1.0 spec

### Next Steps

1. **Approve proposal** and allocate resources
2. **Week 1**: Begin Phase 1 (Core Parser development)
3. **Week 6**: Evaluate editor migration success
4. **Week 8**: Complete engine migration (if Week 6 successful)

The unified parser serves as the **single source of truth** for Twee 1.0 parsing across the entire project, with a **validated, low-risk migration path**.

## Appendix A: Twee 1.0 Spec Reference

Key features that must be supported:

- **Passage Format**: `:: PassageName [tags]`
- **Links**: `[[Display|Target]]`, `[[Target]]`
- **Variables**: `$VARNAME` (case-insensitive)
- **Conditionals**: `<<if>>`, `<<elseif>>`, `<<else>>`, `<<endif>>`
- **Assignment**: `<<set $VAR = value>>`, `<<set $VAR to value>>`
- **Output**: `<<print $VAR>>`, `<<print expression>>`
- **Formatting**: `<<nobr>>...<<endnobr>>`
- **Operators**: `is`, `neq`, `gt`, `gte`, `lt`, `lte`, `=`, `!=`, `>`, `>=`, `<`, `<=`
- **Logical**: `and`, `or`, `not`
- **Arithmetic**: `+`, `-`, `*`, `/`, `%`
- **Functions**: `either()`, `random()`

## Appendix B: Current Parser Comparison

| Feature | Engine (twinery1x.py) | Editor (app-parser.js) | tw1x.py (Proposed) |
|---------|----------------------|------------------------|-------------------|
| Lines of Code | ~1900 | ~540 | ~1500 (estimated) |
| Language | Python | JavaScript | Python |
| `=` operator | ❌ No | ✅ Yes | ✅ Yes |
| `to` operator | ✅ Yes | ✅ Yes | ✅ Yes |
| Boolean values | ❌ No | ✅ Yes | ✅ Yes |
| Type inference | Partial | Full | Full |
| Expression eval | ✅ Yes | ✅ Yes | ✅ Yes |
| StoryInit | ✅ Yes | ✅ Yes | ✅ Yes |
| TestSetup | ❌ No | ✅ Yes | ✅ Yes |
| Quest macros | ✅ Yes | ❌ No | ✅ Yes |
| Test coverage | ~60% | ~0% | 90% (target) |

## Appendix C: Example Story Files to Test

All existing game files must work with tw1x.py:

- `/engine/games/barbarian/data/story.twee` (StoryInit + TestSetup)
- All other game stories in `/engine/games/`
- Editor example files

## Document Version

- **Version**: 1.1 (Editor-First Migration)
- **Date**: 2025-10-25
- **Author**: Development Team
- **Status**: Proposal - Awaiting Approval
- **Migration Strategy**: Editor-First (8 weeks)
- **Risk Level**: LOW (clear checkpoint at Week 6)
