# TW1X (Twee 1 eXtended) 🍫

**Pronounced like "Twix"**

A comprehensive Twee 1.0/SugarCube 1.x parser for text-based interactive fiction written in Python.

## Features

- ✅ **Full Twee 1.0 Syntax Support**
  - Passages with tags: `:: PassageName [tag1, tag2]`
  - Links: `[[Target]]` and `[[Display Text|Target]]`
  - Images: `[img[url]]`

- ✅ **Macro System**
  - Variable assignment: `<<set $VAR = value>>`
  - Conditionals: `<<if>>`/`<<elseif>>`/`<<else>>`/`<<endif>>`
  - Output: `<<print $EXPRESSION>>`
  - Include passages: `<<display "PassageName">>`
  - Formatting: `<<nobr>>`/`<<endnobr>>`

- ✅ **Expression Evaluation**
  - Arithmetic: `+`, `-`, `*`, `/`, `%`
  - Comparison: `is`, `==`, `neq`, `!=`, `gt`, `>`, `gte`, `>=`, `lt`, `<`, `lte`, `<=`
  - Logical: `and`, `or`, `not`
  - Functions: `either(...)`, `random(min, max)`
  - String concatenation

- ✅ **Special Passages**
  - `StoryInit`: Initialize story variables
  - `TestSetup`: Configure test scenarios with conditionals
  - `StoryTitle`: Story metadata

- ✅ **CLI Interface**
  - Parse Twee files to JSON
  - Render passages with variables
  - Evaluate expressions
  - Get story metadata

## Installation

### From Source
```bash
git clone https://github.com/yourusername/tw1x.git
cd tw1x
pip install -e .
```

### As a Dependency
```bash
pip install tw1x
```

Or add to your `requirements.txt`:
```
tw1x>=0.3.0
```

## Quick Start

### Python API

```python
from tw1x import parse_twee, TweeParser, ExecutionMode

# Parse a Twee file
with open('story.twee', 'r') as f:
    content = f.read()

result = parse_twee(content)

print(f"Parsed {len(result.passages)} passages")
print(f"StoryInit variables: {result.story_init_vars}")
print(f"TestSetup variables: {result.test_setup_vars}")

# Render a passage
parser = TweeParser()
passage = result.passages['Start']
variables = {'HEALTH': 100, 'NAME': 'Hero'}

render_result = parser.render_passage(
    passage,
    variables,
    mode=ExecutionMode.PREVIEW,
    passages=result.passages  # For <<display>> macro support
)

print(f"Rendered text: {render_result.text}")
print(f"Links: {[link.target for link in render_result.links]}")
```

### CLI Usage

```bash
# Parse a story file
python -m tw1x parse story.twee

# Get story metadata
python -m tw1x info story.twee

# Render a passage with variables
echo '{"HEALTH": 100, "NAME": "Hero"}' | python -m tw1x render story.twee Start

# Evaluate an expression
echo '{"HEALTH": 100}' | python -m tw1x evaluate '$HEALTH + 50'
```

## Use Cases

### Game Engine Integration
TW1X was designed to be used by game engines to parse and execute Twee stories at runtime:

```python
from tw1x import TweeParser, ExecutionMode

# Load story
parser = TweeParser()
result = parser.parse_twee(twee_content)

# Initialize variables from StoryInit
game_state = result.story_init_vars.copy()

# Render current passage
current_passage = result.passages['Start']
render_result = parser.render_passage(
    current_passage,
    game_state,
    mode=ExecutionMode.RUNTIME,
    passages=result.passages
)

# Display to player
print(render_result.text)

# Handle player choice
for link in render_result.links:
    print(f"  [{link.display}]")
```

### Editor/IDE Integration
TW1X can be used by story editors for preview and validation:

```python
from tw1x import TweeParser, ExecutionMode

# Preview mode for editors
parser = TweeParser()
result = parser.parse_twee(content)

# Use TestSetup variables for testing different scenarios
test_vars = result.test_setup_vars.copy()

# Render for preview
render_result = parser.render_passage(
    passage,
    test_vars,
    mode=ExecutionMode.PREVIEW,
    passages=result.passages
)
```

## Architecture

### Variable Scoping
TW1X supports two variable scoping modes:

- **GLOBAL**: Variables are stored without prefix (for editors)
  - Example: `$HEALTH` → `{'HEALTH': 100}`

- **USERNAME_PREFIXED**: Variables are prefixed with username (for multiplayer games)
  - Example: `$HEALTH` → `{'alice_HEALTH': 100}`

### Execution Modes

- **PARSE_ONLY**: Parse structure only, no macro execution
- **PREVIEW**: Render for preview (editor mode)
- **RUNTIME**: Full execution (game engine mode)

## Documentation

- [API Reference](docs/API.md)
- [Unified Parser Proposal](docs/TW1X_UNIFIED_PARSER_PROPOSAL.md)
- [Twee 1.0 Gap Analysis](docs/TW1X_TWEE10_GAP_ANALYSIS.md)

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tw1x.py

# Run validation suite
python tests/validate_tw1x.py
```

## Projects Using TW1X

- **1drpg Engine**: Multiplayer text-based RPG game engine
- **BranchEd**: Visual story editor for Twee files

## Version History

### v0.3.0 (Phase 3: Special Passages)
- ✅ StoryInit variable extraction
- ✅ TestSetup conditional processing with nested support
- ✅ Three-pass TestSetup algorithm
- ✅ <<display>> macro with circular reference detection

### v0.2.0 (Phase 2: Macros)
- ✅ <<set>> macro with compound operators (+=, -=, *=, /=)
- ✅ <<print>> macro
- ✅ <<if>>/<<elseif>>/<<else>>/<<endif>> conditionals
- ✅ <<nobr>>/<<endnobr>> formatting
- ✅ Expression evaluator with operators and functions

### v0.1.0 (Phase 1: Core Parser)
- ✅ Passage parsing with tags
- ✅ Link extraction
- ✅ Image URL extraction
- ✅ Basic structure parsing

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Authors

Development Team

---

**TW1X** - Making Twee parsing consistent across the ecosystem 🍫

---

## Full License Text

MIT License

Copyright (c) 2025 Thor Alexander

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
