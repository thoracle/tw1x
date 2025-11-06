#!/usr/bin/env python3
"""
TW1X (TWEE 1 eXtended) - Unified Twee 1.0 Parser
Pronounced like "Twix" 🍫

A comprehensive Twee 1.0/SugarCube 1.x parser for text-based interactive fiction.
Used by both the game engine and BranchEd editor.

Author: Development Team
Version: 0.3.0 (Phase 3: Special Passages - StoryInit & TestSetup)
Date: 2025-10-25
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum
import re
import random as random_module


# ============================================================================
# Enums
# ============================================================================

class VariableScope(Enum):
    """Variable scoping strategy."""
    GLOBAL = "global"              # No prefix (editor mode)
    USERNAME_PREFIXED = "prefixed"  # username_VAR (engine mode)


class ExecutionMode(Enum):
    """Parser execution mode."""
    PARSE_ONLY = "parse"    # Parse structure only
    PREVIEW = "preview"     # Render for preview (editor)
    RUNTIME = "runtime"     # Full execution (engine)


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class Passage:
    """Represents a parsed Twee passage."""
    name: str
    tags: List[str]
    content: str
    raw_content: str
    image_url: Optional[str] = None

    def __repr__(self):
        tags_str = f"[{', '.join(self.tags)}]" if self.tags else ""
        return f"Passage('{self.name}' {tags_str})"


@dataclass
class Link:
    """Represents a story link."""
    display: str
    target: str
    setters: List[Tuple[str, str, str]] = field(default_factory=list)

    def __repr__(self):
        if self.display == self.target:
            return f"Link([[{self.target}]])"
        return f"Link([[{self.display}|{self.target}]])"


@dataclass
class ParseResult:
    """Result of parsing Twee content."""
    passages: Dict[str, Passage]
    story_init_vars: Dict[str, Any]
    test_setup_vars: Dict[str, Any]
    errors: List[str]

    def __repr__(self):
        return f"ParseResult({len(self.passages)} passages, {len(self.errors)} errors)"


@dataclass
class RenderResult:
    """Result of rendering a passage."""
    text: str
    links: List[Link]
    variable_changes: Dict[str, Any]
    errors: List[str]


# ============================================================================
# Value Parsing & Type Inference
# ============================================================================

def parse_value(value_str: str) -> Union[int, float, str, bool]:
    """
    Parse value string with proper type inference.

    Args:
        value_str: String representation of value

    Returns:
        Typed value (int, float, bool, or str)

    Examples:
        >>> parse_value("42")
        42
        >>> parse_value("3.14")
        3.14
        >>> parse_value("true")
        True
        >>> parse_value('"hello"')
        'hello'
    """
    value_str = value_str.strip()

    # String value (quoted)
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]

    # Boolean value
    if value_str.lower() == 'true':
        return True
    if value_str.lower() == 'false':
        return False

    # Numeric value
    try:
        if '.' in value_str:
            return float(value_str)
        else:
            return int(value_str)
    except ValueError:
        pass

    # Default to string (unquoted)
    return value_str


# ============================================================================
# Expression Evaluator
# ============================================================================

class ExpressionEvaluator:
    """
    Evaluates Twee expressions with variables, operators, and functions.

    Supports:
        - Arithmetic: +, -, *, /, %
        - Comparison: is, ==, neq, !=, gt, >, gte, >=, lt, <, lte, <=
        - Logical: and, or, not
        - Functions: either(...), random(min, max)
        - String concatenation
    """

    # Operator mappings (text to symbol)
    OPERATORS = {
        'is': '==',
        'neq': '!=',
        'gt': '>',
        'gte': '>=',
        'lt': '<',
        'lte': '<=',
        'and': 'and',
        'or': 'or',
        'not': 'not'
    }

    def __init__(self, variables: Optional[Dict[str, Any]] = None):
        """
        Initialize evaluator.

        Args:
            variables: Variable store (e.g., missionDict or editor state)
        """
        self.variables = variables or {}
        self.errors: List[str] = []

    def evaluate(self, expr: str) -> Any:
        """
        Evaluate expression.

        Args:
            expr: Expression string (e.g., "$HEALTH + 50", "$NAME + ' the Great'")

        Returns:
            Evaluated result
        """
        try:
            # Normalize operators
            normalized = self._normalize_expression(expr)

            # Replace variables
            resolved = self._resolve_variables(normalized)

            # Handle functions
            resolved = self._resolve_functions(resolved)

            # Evaluate
            result = eval(resolved, {"__builtins__": {}}, {})
            return result

        except Exception as e:
            self.errors.append(f"Expression error: {expr} - {str(e)}")
            return None

    def evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate conditional expression to boolean.

        Args:
            condition: Conditional expression

        Returns:
            Boolean result
        """
        result = self.evaluate(condition)
        if result is None:
            return False
        return bool(result)

    def _normalize_expression(self, expr: str) -> str:
        """
        Normalize text operators to symbols.

        Args:
            expr: Raw expression

        Returns:
            Normalized expression
        """
        result = expr

        # Replace text operators with symbols (word boundaries)
        for text_op, symbol_op in self.OPERATORS.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + text_op + r'\b'
            result = re.sub(pattern, symbol_op, result)

        return result

    def _resolve_variables(self, expr: str) -> str:
        """
        Replace $VARIABLE references with values.

        Args:
            expr: Expression with variables

        Returns:
            Expression with resolved values
        """
        def replace_var(match):
            var_name = match.group(1)
            # Case-insensitive lookup
            value = self._get_variable(var_name)
            return repr(value)

        # Match $VARNAME (letters, numbers, underscores)
        pattern = r'\$([A-Za-z_][A-Za-z0-9_]*)'
        return re.sub(pattern, replace_var, expr)

    def _get_variable(self, var_name: str) -> Any:
        """
        Get variable value (case-insensitive).

        Args:
            var_name: Variable name (without $)

        Returns:
            Variable value or empty string if not found
        """
        # Try exact match first
        if var_name in self.variables:
            return self.variables[var_name]

        # Try case-insensitive match
        for key, value in self.variables.items():
            if key.lower() == var_name.lower():
                return value

        # Not found - return empty string (Twee 1.0 behavior)
        return ""

    def _resolve_functions(self, expr: str) -> str:
        """
        Replace function calls with their results.

        Args:
            expr: Expression with functions

        Returns:
            Expression with evaluated functions
        """
        # either(...) function
        expr = self._resolve_either(expr)

        # random(...) function
        expr = self._resolve_random(expr)

        return expr

    def _resolve_either(self, expr: str) -> str:
        """
        Resolve either(...) functions.

        Args:
            expr: Expression possibly containing either()

        Returns:
            Expression with either() resolved
        """
        pattern = r'either\(([^)]+)\)'

        def replace_either(match):
            args_str = match.group(1)
            # Split by comma, respecting quotes
            args = self._split_args(args_str)
            if args:
                choice = random_module.choice(args)
                return repr(eval(choice, {"__builtins__": {}}, {}))
            return '""'

        return re.sub(pattern, replace_either, expr)

    def _resolve_random(self, expr: str) -> str:
        """
        Resolve random(min, max) functions.

        Args:
            expr: Expression possibly containing random()

        Returns:
            Expression with random() resolved
        """
        pattern = r'random\(([^,]+),\s*([^)]+)\)'

        def replace_random(match):
            min_val = int(eval(match.group(1), {"__builtins__": {}}, {}))
            max_val = int(eval(match.group(2), {"__builtins__": {}}, {}))
            result = random_module.randint(min_val, max_val)
            # Return as string literal (quoted) so it can be concatenated with other strings
            return f'"{result}"'

        return re.sub(pattern, replace_random, expr)

    def _split_args(self, args_str: str) -> List[str]:
        """
        Split function arguments by comma, respecting quotes.

        Args:
            args_str: Comma-separated arguments

        Returns:
            List of argument strings
        """
        args = []
        current = []
        in_quotes = False
        quote_char = None

        for char in args_str:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
                current.append(char)
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
                current.append(char)
            elif char == ',' and not in_quotes:
                args.append(''.join(current).strip())
                current = []
            else:
                current.append(char)

        if current:
            args.append(''.join(current).strip())

        return args


# ============================================================================
# Macro Processor
# ============================================================================

class MacroProcessor:
    """
    Processes Twee macros (<<set>>, <<print>>, <<if>>, etc.).
    """

    def __init__(self, variables: Dict[str, Any]):
        """
        Initialize macro processor.

        Args:
            variables: Variable store
        """
        self.variables = variables
        self.evaluator = ExpressionEvaluator(variables)
        self.errors: List[str] = []

    def process_set_macro(self, content: str) -> None:
        """
        Process <<set>> macro.

        Supports assignment operators:
            <<set $VAR = value>>
            <<set $VAR to value>>
            <<set $VAR += value>>
            <<set $VAR -= value>>
            <<set $VAR *= value>>
            <<set $VAR /= value>>

        Args:
            content: Macro content (between << and >>)
        """
        # Remove 'set' keyword
        assignment = content[3:].strip()

        # Match: $VAR op value (where op is =, to, +=, -=, *=, /=)
        match = re.match(r'\$([A-Za-z_][A-Za-z0-9_]*)\s+(=|to|\+=|-=|\*=|/=)\s+(.+)', assignment)
        if not match:
            self.errors.append(f"Invalid <<set>> syntax: {content}")
            return

        var_name = match.group(1)
        operator = match.group(2)
        value_expr = match.group(3).strip()

        # Evaluate expression
        new_value = self.evaluator.evaluate(value_expr)

        # Apply operator
        if operator in ('=', 'to'):
            self.variables[var_name] = new_value
        elif operator == '+=':
            current = self.variables.get(var_name, 0)
            self.variables[var_name] = current + new_value
        elif operator == '-=':
            current = self.variables.get(var_name, 0)
            self.variables[var_name] = current - new_value
        elif operator == '*=':
            current = self.variables.get(var_name, 1)
            self.variables[var_name] = current * new_value
        elif operator == '/=':
            current = self.variables.get(var_name, 1)
            if new_value != 0:
                self.variables[var_name] = current / new_value
            else:
                self.errors.append(f"Division by zero in: {content}")

    def process_print_macro(self, content: str) -> str:
        """
        Process <<print>> macro.

        Args:
            content: Macro content

        Returns:
            String representation of value
        """
        # Remove 'print' keyword
        expr = content[5:].strip()

        # Evaluate expression
        value = self.evaluator.evaluate(expr)

        return str(value) if value is not None else ""

    def evaluate_condition(self, condition: str) -> bool:
        """
        Evaluate conditional expression for <<if>>/<<elseif>>.

        Args:
            condition: Conditional expression

        Returns:
            Boolean result
        """
        return self.evaluator.evaluate_condition(condition)


# ============================================================================
# Core Parser
# ============================================================================

class TweeParser:
    """
    Twee 1.0 parser with full macro and expression support.

    Usage:
        parser = TweeParser()
        result = parser.parse_twee(twee_content)
        print(f"Parsed {len(result.passages)} passages")
    """

    # Regex patterns for Twee syntax
    PASSAGE_PATTERN = re.compile(r'^::([^[\n]+)(?:\[([^\]]+)\])?\s*$', re.MULTILINE)
    LINK_PATTERN = re.compile(r'\[\[([^\]|]+)(?:\|([^\]]+))?\]\]')
    IMAGE_PATTERN = re.compile(r'\[img\[([^\]]+)\]\]')

    def __init__(self, scope_mode: VariableScope = VariableScope.GLOBAL):
        """
        Initialize parser.

        Args:
            scope_mode: Variable scoping strategy (GLOBAL or USERNAME_PREFIXED)
        """
        self.scope_mode = scope_mode
        self.errors: List[str] = []

    def parse_twee(self, content: str) -> ParseResult:
        """
        Parse Twee content into story structure.

        Args:
            content: Raw Twee content (entire file as string)

        Returns:
            ParseResult with passages, story_init_vars, test_setup_vars, and errors
        """
        self.errors = []
        passages: Dict[str, Passage] = {}

        # Split content into passages
        passage_sections = self._split_into_passages(content)

        # Parse each passage
        for section in passage_sections:
            passage = self._parse_passage(section)
            if passage:
                passages[passage.name] = passage

        # Extract special passages
        story_init_vars = self._extract_story_init(passages.get('StoryInit'))
        test_setup_vars = self._extract_test_setup(passages.get('TestSetup'))

        return ParseResult(
            passages=passages,
            story_init_vars=story_init_vars,
            test_setup_vars=test_setup_vars,
            errors=self.errors.copy()
        )

    def _split_into_passages(self, content: str) -> List[str]:
        """
        Split Twee content into individual passage sections.

        Args:
            content: Raw Twee content

        Returns:
            List of passage sections (including header and content)
        """
        # Split on passage markers (:: at start of line)
        sections = re.split(r'^(?=::)', content, flags=re.MULTILINE)

        # Filter out empty sections
        return [s.strip() for s in sections if s.strip() and s.strip().startswith('::')]

    def _parse_passage(self, section: str) -> Optional[Passage]:
        """
        Parse a single passage section.

        Args:
            section: Passage text including :: header

        Returns:
            Passage object or None if parsing fails
        """
        lines = section.split('\n', 1)
        if not lines:
            return None

        header = lines[0]
        content = lines[1] if len(lines) > 1 else ""

        # Parse header: :: PassageName [tag1, tag2]
        match = re.match(r'^::\s*([^[\n]+?)(?:\s*\[([^\]]+)\])?\s*$', header)
        if not match:
            self.errors.append(f"Invalid passage header: {header}")
            return None

        name = match.group(1).strip()
        tags_str = match.group(2)

        # Parse tags
        tags = []
        if tags_str:
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]

        # Extract image URL if present and remove image tag from content
        image_url = self._extract_image_url(content)

        # Remove [img[url]] tag from content for display
        content_without_image = content
        if image_url:
            content_without_image = self.IMAGE_PATTERN.sub('', content).strip()

        return Passage(
            name=name,
            tags=tags,
            content=content_without_image,
            raw_content=content.strip(),
            image_url=image_url
        )

    def _extract_image_url(self, content: str) -> Optional[str]:
        """
        Extract image URL from [img[...]] syntax.

        Args:
            content: Passage content

        Returns:
            Image URL or None
        """
        match = self.IMAGE_PATTERN.search(content)
        return match.group(1) if match else None

    def _extract_story_init(self, passage: Optional[Passage]) -> Dict[str, Any]:
        """
        Extract variables from StoryInit passage.

        Args:
            passage: StoryInit passage or None

        Returns:
            Dictionary of initialized variables
        """
        if not passage:
            return {}

        # Parse <<set>> macros to extract variables
        variables = {}
        processor = MacroProcessor(variables)

        # Find all <<set>> macros
        set_pattern = re.compile(r'<<(set\s+.+?)>>')
        for match in set_pattern.finditer(passage.content):
            macro_content = match.group(1)
            processor.process_set_macro(macro_content)
            # Update evaluator with new variables so subsequent macros can reference them
            processor.evaluator.variables = variables

        return variables

    def _extract_test_setup(self, passage: Optional[Passage]) -> Dict[str, Any]:
        """
        Extract variables from TestSetup passage using three-pass processing.

        Three-pass approach:
        1. Extract top-level <<set>> statements (before any conditionals)
        2. Evaluate conditional blocks using Pass 1 variables
        3. Extract <<set>> statements from evaluated conditional branch

        Args:
            passage: TestSetup passage or None

        Returns:
            Dictionary of test variables
        """
        if not passage:
            return {}

        content = passage.content
        variables = {}

        # PASS 1: Extract top-level <<set>> statements (before first <<if>>)
        # Find position of first <<if>>
        if_match = re.search(r'<<if\s+', content)
        if if_match:
            top_level_content = content[:if_match.start()]
        else:
            top_level_content = content

        # Extract all <<set>> from top-level
        processor = MacroProcessor(variables)
        set_pattern = re.compile(r'<<(set\s+.+?)>>')
        for match in set_pattern.finditer(top_level_content):
            macro_content = match.group(1)
            processor.process_set_macro(macro_content)

        # PASS 2 & 3: Evaluate conditionals and extract variables from matched branch
        if if_match:
            # Process conditionals to get the evaluated branch content
            conditional_content = content[if_match.start():]

            # Create a processor with Pass 1 variables
            processor = MacroProcessor(variables)

            # Process ALL conditionals first (without extracting <<set>> macros yet)
            # This ensures nested conditionals are evaluated before we extract variables
            rendered = conditional_content
            max_iterations = 20
            for iteration in range(max_iterations):
                old_rendered = rendered
                rendered = self._process_conditionals(rendered, processor)

                # If no more changes or no more conditionals, we're done
                if rendered == old_rendered or '<<if' not in rendered:
                    break

            # PASS 3: Now extract all <<set>> statements from fully evaluated content
            # All conditionals have been resolved, so only active branch <<set>> remain
            for match in set_pattern.finditer(rendered):
                macro_content = match.group(1)
                processor.process_set_macro(macro_content)

        return variables

    def extract_links(self, passage: Passage) -> List[Link]:
        """
        Extract all links from passage content.

        Args:
            passage: Passage to extract links from

        Returns:
            List of Link objects
        """
        links = []

        for match in self.LINK_PATTERN.finditer(passage.content):
            if match.group(2):
                # [[Display|Target]] format
                display = match.group(1).strip()
                target = match.group(2).strip()
            else:
                # [[Target]] format
                target = match.group(1).strip()
                display = target

            links.append(Link(display=display, target=target))

        return links

    def render_passage(self,
                      passage: Passage,
                      variables: Dict[str, Any],
                      mode: ExecutionMode = ExecutionMode.PREVIEW,
                      passages: Optional[Dict[str, Passage]] = None,
                      _display_stack: Optional[List[str]] = None) -> RenderResult:
        """
        Render passage with macro expansion.

        Args:
            passage: Passage to render
            variables: Variable store
            mode: Execution mode
            passages: Dict of all passages (needed for <<display>> macro)
            _display_stack: Internal parameter to track circular <<display>> references

        Returns:
            RenderResult with rendered text, links, and variable changes
        """
        errors = []
        text = passage.content
        variable_changes = {}
        processor = MacroProcessor(variables)

        # Initialize display stack for circular reference detection
        if _display_stack is None:
            _display_stack = []

        # Process <<display>> macros FIRST (before conditionals)
        # This allows displayed passages to contain conditionals that will be evaluated
        if passages:
            text = self._process_display_macros(text, passages, variables, mode, _display_stack, errors)

        # Iteratively process conditionals and <<set>> macros
        # This handles cases where <<set>> macros affect nested conditionals
        max_iterations = 20
        for iteration in range(max_iterations):
            old_text = text

            # Process <<if>>/<<elseif>>/<<else>>/<<endif>> conditionals
            text = self._process_conditionals(text, processor)

            # Process <<set>> macros to update variables
            set_pattern = re.compile(r'<<(set\s+.+?)>>')
            def replace_set(match):
                macro_content = match.group(1)
                processor.process_set_macro(macro_content)
                return ""  # Remove <<set>> from output
            text = set_pattern.sub(replace_set, text)

            # If no changes were made, we're done
            if text == old_text:
                break

        # Process <<print>> macros (after all variables are updated)
        def replace_print(match):
            macro_content = match.group(1)
            return processor.process_print_macro(macro_content)

        print_pattern = re.compile(r'<<(print\s+[^>]+)>>')
        text = print_pattern.sub(replace_print, text)

        # Process <<nobr>>/<<endnobr>> - remove line breaks
        nobr_pattern = re.compile(r'<<nobr>>(.*?)<<endnobr>>', re.DOTALL)
        text = nobr_pattern.sub(lambda m: m.group(1).replace('\n', ' '), text)

        # Extract links from processed text (not original passage content)
        links = []
        for match in self.LINK_PATTERN.finditer(text):
            if match.group(2):
                # [[Display|Target]] format
                display = match.group(1).strip()
                target = match.group(2).strip()
            else:
                # [[Target]] format
                target = match.group(1).strip()
                display = target
            links.append(Link(display=display, target=target))

        errors.extend(processor.errors)

        return RenderResult(
            text=text.strip(),
            links=links,
            variable_changes=variable_changes,
            errors=errors
        )

    def _process_display_macros(self,
                                 text: str,
                                 passages: Dict[str, Passage],
                                 variables: Dict[str, Any],
                                 mode: ExecutionMode,
                                 display_stack: List[str],
                                 errors: List[str]) -> str:
        """
        Process <<display "PASSAGE_NAME">> macros by including passage content inline.

        Args:
            text: Text containing <<display>> macros
            passages: Dict of all passages
            variables: Variable store
            mode: Execution mode
            display_stack: Stack of currently displayed passages (for circular reference detection)
            errors: Error list to append to

        Returns:
            Text with <<display>> macros replaced by passage content
        """
        # Pattern: <<display "PASSAGE_NAME">> or <<display 'PASSAGE_NAME'>>
        display_pattern = re.compile(r'<<display\s+["\']([^"\']+)["\']\s*>>', re.IGNORECASE)

        def replace_display(match):
            passage_name = match.group(1).strip()

            # Check for circular reference
            if passage_name in display_stack:
                error_msg = f"Circular <<display>> reference detected: {' -> '.join(display_stack + [passage_name])}"
                errors.append(error_msg)
                return f"[ERROR: {error_msg}]"

            # Look up passage (case-insensitive)
            target_passage = None
            for name, passage in passages.items():
                if name.lower() == passage_name.lower():
                    target_passage = passage
                    break

            if not target_passage:
                error_msg = f"<<display>> passage not found: {passage_name}"
                errors.append(error_msg)
                return f"[ERROR: {error_msg}]"

            # Add to display stack
            new_display_stack = display_stack + [passage_name]

            # Recursively render the displayed passage
            # This allows displayed passages to have their own macros, conditionals, etc.
            result = self.render_passage(
                target_passage,
                variables,
                mode,
                passages,
                new_display_stack
            )

            # Collect any errors from the nested render
            errors.extend(result.errors)

            # Return the rendered text
            return result.text

        # Replace all <<display>> macros
        return display_pattern.sub(replace_display, text)

    def _process_conditionals(self, text: str, processor: MacroProcessor) -> str:
        """
        Process <<if>>/<<elseif>>/<<else>>/<<endif>> blocks.
        Only processes the FIRST/OUTERMOST conditional block found.
        Caller should loop to process nested conditionals after updating variables.

        Args:
            text: Passage text with conditionals
            processor: Macro processor for evaluating conditions

        Returns:
            Text with first conditional evaluated
        """
        # Only process ONE <<if>> block, not all of them
        # This allows the caller to process <<set>> macros between nested conditionals

        # Match everything except >> at the end (use negative lookahead to avoid matching single >)
        if_match = re.search(r'<<if\s+((?:(?!>>).)+)>>', text, re.DOTALL)
        if not if_match:
            return text

        # Find matching <<endif>>
        start_pos = if_match.end()
        depth = 1
        pos = start_pos
        sections = []  # [(type, condition, content), ...]
        current_section_type = 'if'
        current_condition = if_match.group(1)
        current_content_start = start_pos

        while pos < len(text) and depth > 0:
            # Look for next control structure
            # Match everything except >> at the end (use negative lookahead)
            # Support both <<endif>> and <</if>> syntaxes
            next_match = re.search(r'<<(/?)(if|elseif|else|endif)(?:\s+((?:(?!>>).)+))?>>',text[pos:], re.DOTALL)
            if not next_match:
                break

            is_closing = next_match.group(1) == '/'
            match_type = next_match.group(2)
            # Convert closing tags to 'endif' for unified handling
            if is_closing and match_type == 'if':
                match_type = 'endif'
            match_pos = pos + next_match.start()

            if match_type == 'if':
                depth += 1
                pos = pos + next_match.end()
            elif match_type == 'endif':
                depth -= 1
                if depth == 0:
                    # Save current section
                    content = text[current_content_start:match_pos]
                    sections.append((current_section_type, current_condition, content))
                    # Found matching endif
                    endif_pos = pos + next_match.end()

                    # Evaluate sections
                    result_text = ""
                    for section_type, condition, content in sections:
                        if section_type == 'else':
                            result_text = content
                            break
                        elif processor.evaluate_condition(condition):
                            result_text = content
                            break

                    # Replace entire if block with result
                    text = text[:if_match.start()] + result_text + text[endif_pos:]
                    return text
                else:
                    pos = pos + next_match.end()
            elif match_type in ('elseif', 'else') and depth == 1:
                # Save current section
                content = text[current_content_start:match_pos]
                sections.append((current_section_type, current_condition, content))

                # Start new section
                current_section_type = match_type
                current_condition = next_match.group(3) if match_type == 'elseif' else None
                current_content_start = pos + next_match.end()
                pos = pos + next_match.end()
            else:
                pos = pos + next_match.end()

        return text


# ============================================================================
# Public API
# ============================================================================

def parse_twee(content: str,
               scope_mode: VariableScope = VariableScope.GLOBAL) -> ParseResult:
    """
    Parse Twee content (convenience function).

    Args:
        content: Raw Twee content
        scope_mode: Variable scoping strategy

    Returns:
        ParseResult with passages and metadata

    Example:
        result = parse_twee(twee_content)
        for name, passage in result.passages.items():
            print(f"{name}: {len(passage.content)} chars")
    """
    parser = TweeParser(scope_mode=scope_mode)
    return parser.parse_twee(content)


# ============================================================================
# Main (for testing)
# ============================================================================

if __name__ == '__main__':
    import sys

    print("TW1X (TWEE 1 eXtended) Parser v0.1.0")
    print("Phase 1: Core Parser\n")

    if len(sys.argv) > 1:
        # Parse file from command line
        filepath = sys.argv[1]
        with open(filepath, 'r') as f:
            content = f.read()

        result = parse_twee(content)

        print(f"✅ Parsed {len(result.passages)} passages")
        if result.errors:
            print(f"⚠️  {len(result.errors)} errors:")
            for error in result.errors:
                print(f"   - {error}")

        print("\nPassages:")
        for name, passage in result.passages.items():
            tags_str = f" [{', '.join(passage.tags)}]" if passage.tags else ""
            print(f"  - {name}{tags_str} ({len(passage.content)} chars)")

            # Show links
            parser = TweeParser()
            links = parser.extract_links(passage)
            if links:
                print(f"    Links: {', '.join(link.target for link in links)}")
    else:
        print("Usage: python tw1x.py <story.twee>")
        print("\nExample:")
        print("  python tw1x.py ../engine/games/barbarian/data/story.twee")
