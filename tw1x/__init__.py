"""
TW1X (Twee 1 eXtended) - Unified Twee 1.0 Parser
Pronounced like "Twix" 🍫

A comprehensive Twee 1.0/SugarCube 1.x parser for text-based interactive fiction.
"""

from .tw1x import (
    # Core parser
    TweeParser,
    parse_twee,

    # Data structures
    Passage,
    Link,
    ParseResult,
    RenderResult,

    # Enums
    VariableScope,
    ExecutionMode,

    # Expression evaluator
    ExpressionEvaluator,

    # Macro processor
    MacroProcessor,

    # Utilities
    parse_value,
)

__version__ = "0.3.0"
__author__ = "Development Team"
__all__ = [
    # Parser
    "TweeParser",
    "parse_twee",

    # Data structures
    "Passage",
    "Link",
    "ParseResult",
    "RenderResult",

    # Enums
    "VariableScope",
    "ExecutionMode",

    # Expression evaluator
    "ExpressionEvaluator",

    # Macro processor
    "MacroProcessor",

    # Utilities
    "parse_value",
]
