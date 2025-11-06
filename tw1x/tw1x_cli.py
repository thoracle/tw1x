#!/usr/bin/env python3
"""
TW1X CLI - Command-line interface for TW1X parser

Provides JSON-based interface for editor integration via subprocess.

Usage:
    # Parse a twee file
    python3 tw1x_cli.py parse story.twee

    # Render a passage with variables (from stdin)
    echo '{"HEALTH": 100}' | python3 tw1x_cli.py render story.twee Start

    # Evaluate an expression
    echo '{"HEALTH": 100}' | python3 tw1x_cli.py evaluate '$HEALTH + 50'

Author: Development Team
Version: 0.4.0 (Phase 4: CLI Interface)
Date: 2025-10-25
"""

import sys
import json
import argparse
from typing import Dict, Any, Optional
from pathlib import Path

from tw1x import (
    parse_twee, TweeParser, ExpressionEvaluator,
    VariableScope, ExecutionMode
)


def read_stdin_json() -> Dict[str, Any]:
    """
    Read JSON from stdin.

    Returns:
        Dictionary of variables or empty dict if no input
    """
    if not sys.stdin.isatty():
        try:
            data = sys.stdin.read().strip()
            if data:
                return json.loads(data)
        except json.JSONDecodeError as e:
            print(json.dumps({
                "error": f"Invalid JSON on stdin: {str(e)}"
            }), file=sys.stderr)
            sys.exit(1)
    return {}


def cmd_parse(args: argparse.Namespace) -> None:
    """
    Parse a twee file and output story structure as JSON.

    Args:
        args: Command arguments with 'file' attribute
    """
    try:
        # Read file
        file_path = Path(args.file)
        if not file_path.exists():
            print(json.dumps({
                "error": f"File not found: {args.file}"
            }))
            sys.exit(1)

        with open(file_path, 'r') as f:
            content = f.read()

        # Parse
        result = parse_twee(content)

        # Convert to JSON-serializable format
        output = {
            "passages": {
                name: {
                    "name": p.name,
                    "tags": p.tags,
                    "content": p.content,
                    "image_url": p.image_url
                }
                for name, p in result.passages.items()
            },
            "story_init_vars": result.story_init_vars,
            "test_setup_vars": result.test_setup_vars,
            "errors": result.errors,
            "passage_count": len(result.passages)
        }

        print(json.dumps(output, indent=2))

    except Exception as e:
        print(json.dumps({
            "error": f"Parse error: {str(e)}"
        }))
        sys.exit(1)


def cmd_render(args: argparse.Namespace) -> None:
    """
    Render a passage with variables from stdin.

    Args:
        args: Command arguments with 'file' and 'passage' attributes
    """
    try:
        # Read variables from stdin
        variables = read_stdin_json()

        # Read file
        file_path = Path(args.file)
        if not file_path.exists():
            print(json.dumps({
                "error": f"File not found: {args.file}"
            }))
            sys.exit(1)

        with open(file_path, 'r') as f:
            content = f.read()

        # Parse
        result = parse_twee(content)

        # Find passage
        if args.passage not in result.passages:
            print(json.dumps({
                "error": f"Passage not found: {args.passage}",
                "available_passages": list(result.passages.keys())
            }))
            sys.exit(1)

        passage = result.passages[args.passage]

        # Render with variables and all passages (for <<display>> macro support)
        parser = TweeParser()
        render_result = parser.render_passage(passage, variables, passages=result.passages)

        # Convert to JSON
        output = {
            "text": render_result.text,
            "links": [
                {
                    "display": link.display,
                    "target": link.target,
                    "setters": link.setters
                }
                for link in render_result.links
            ],
            "variable_changes": render_result.variable_changes,
            "errors": render_result.errors
        }

        print(json.dumps(output, indent=2))

    except Exception as e:
        print(json.dumps({
            "error": f"Render error: {str(e)}"
        }))
        sys.exit(1)


def cmd_evaluate(args: argparse.Namespace) -> None:
    """
    Evaluate an expression with variables from stdin.

    Args:
        args: Command arguments with 'expression' attribute
    """
    try:
        # Read variables from stdin
        variables = read_stdin_json()

        # Evaluate expression
        evaluator = ExpressionEvaluator(variables)
        result = evaluator.evaluate(args.expression)

        # Output result
        output = {
            "result": result,
            "expression": args.expression,
            "errors": evaluator.errors
        }

        print(json.dumps(output, indent=2))

    except Exception as e:
        print(json.dumps({
            "error": f"Evaluation error: {str(e)}"
        }))
        sys.exit(1)


def cmd_info(args: argparse.Namespace) -> None:
    """
    Get story metadata (title, init vars, test vars).

    Args:
        args: Command arguments with 'file' attribute
    """
    try:
        # Read file
        file_path = Path(args.file)
        if not file_path.exists():
            print(json.dumps({
                "error": f"File not found: {args.file}"
            }))
            sys.exit(1)

        with open(file_path, 'r') as f:
            content = f.read()

        # Parse
        result = parse_twee(content)

        # Get title
        title = result.passages.get('StoryTitle')
        title_text = title.content.strip() if title else None

        # Output metadata
        output = {
            "title": title_text,
            "passage_count": len(result.passages),
            "story_init_vars": result.story_init_vars,
            "test_setup_vars": result.test_setup_vars,
            "passages": list(result.passages.keys()),
            "errors": result.errors
        }

        print(json.dumps(output, indent=2))

    except Exception as e:
        print(json.dumps({
            "error": f"Info error: {str(e)}"
        }))
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='TW1X - Twee 1.0 Parser CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Parse a story file
  python3 tw1x_cli.py parse story.twee

  # Get story metadata
  python3 tw1x_cli.py info story.twee

  # Render a passage with variables
  echo '{"HEALTH": 100, "NAME": "Hero"}' | python3 tw1x_cli.py render story.twee Start

  # Evaluate an expression
  echo '{"HEALTH": 100}' | python3 tw1x_cli.py evaluate '$HEALTH + 50'

Variables are passed via stdin as JSON.
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse a twee file')
    parse_parser.add_argument('file', help='Twee file to parse')

    # Render command
    render_parser = subparsers.add_parser('render', help='Render a passage')
    render_parser.add_argument('file', help='Twee file')
    render_parser.add_argument('passage', help='Passage name to render')

    # Evaluate command
    eval_parser = subparsers.add_parser('evaluate', help='Evaluate an expression')
    eval_parser.add_argument('expression', help='Expression to evaluate')

    # Info command
    info_parser = subparsers.add_parser('info', help='Get story metadata')
    info_parser.add_argument('file', help='Twee file')

    args = parser.parse_args()

    # Execute command
    if args.command == 'parse':
        cmd_parse(args)
    elif args.command == 'render':
        cmd_render(args)
    elif args.command == 'evaluate':
        cmd_evaluate(args)
    elif args.command == 'info':
        cmd_info(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
