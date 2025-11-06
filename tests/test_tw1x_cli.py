#!/usr/bin/env python3
"""
CLI integration tests for TW1X

Tests the tw1x_cli.py command-line interface.

Run with: python3 test_tw1x_cli.py
"""

import unittest
import subprocess
import json
import os
import shlex
from pathlib import Path


class TestCLICommands(unittest.TestCase):
    """Test CLI commands."""

    def setUp(self):
        """Set up test environment."""
        self.cli = 'python3 tw1x_cli.py'
        self.test_story = 'engine/games/barbarian/data/story.twee'

        if not os.path.exists(self.test_story):
            self.skipTest("Barbarian story file not found")

    def _run_cli(self, command: str, stdin_data: str = None) -> dict:
        """
        Run CLI command and return JSON output.

        Args:
            command: CLI command to run
            stdin_data: Optional data to pass to stdin

        Returns:
            Parsed JSON output
        """
        # Split command for subprocess to avoid shell expansion
        cmd_parts = ['python3', 'tw1x_cli.py'] + shlex.split(command)
        result = subprocess.run(
            cmd_parts,
            input=stdin_data,
            capture_output=True,
            text=True
        )

        # Parse JSON output
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(f"Invalid JSON output:\n{result.stdout}\nStderr:\n{result.stderr}")

    def test_info_command(self):
        """Test info command."""
        output = self._run_cli(f'info {self.test_story}')

        self.assertEqual(output['title'], 'Wrath of the Barbarian')
        self.assertEqual(output['passage_count'], 27)
        self.assertIn('PLAYER_NAME', output['story_init_vars'])
        self.assertIn('SCENARIO', output['test_setup_vars'])

    def test_parse_command(self):
        """Test parse command."""
        output = self._run_cli(f'parse {self.test_story}')

        self.assertIn('passages', output)
        self.assertIn('story_init_vars', output)
        self.assertIn('test_setup_vars', output)
        self.assertEqual(output['passage_count'], 27)

        # Check specific passages exist
        self.assertIn('Start', output['passages'])
        self.assertIn('LONGHOUSE', output['passages'])

    def test_render_command_basic(self):
        """Test render command with basic variables."""
        variables = {
            'PLAYER_NAME': 'Thorgrim',
            'STRENGTH': 18,
            'HONOR': 10,
            'RAGE': 0
        }

        output = self._run_cli(
            f'render {self.test_story} Start',
            stdin_data=json.dumps(variables)
        )

        self.assertIn('text', output)
        self.assertIn('links', output)
        self.assertIn('Thorgrim', output['text'])
        self.assertIn('18', output['text'])  # Strength value

        # Check link
        self.assertEqual(len(output['links']), 1)
        self.assertEqual(output['links'][0]['target'], 'LONGHOUSE')

    def test_render_command_with_conditionals(self):
        """Test render command with conditional passages."""
        # Test LONGHOUSE passage with high STRENGTH
        variables = {'STRENGTH': 18}

        output = self._run_cli(
            f'render {self.test_story} LONGHOUSE',
            stdin_data=json.dumps(variables)
        )

        self.assertIn('text', output)
        self.assertIn('links', output)
        self.assertEqual(len(output['errors']), 0)

    def test_evaluate_command_arithmetic(self):
        """Test evaluate command with arithmetic."""
        variables = {'HEALTH': 100, 'DAMAGE': 25}

        output = self._run_cli(
            'evaluate "$HEALTH - $DAMAGE"',
            stdin_data=json.dumps(variables)
        )

        self.assertEqual(output['result'], 75)
        self.assertEqual(output['expression'], '$HEALTH - $DAMAGE')
        self.assertEqual(len(output['errors']), 0)

    def test_evaluate_command_comparison(self):
        """Test evaluate command with comparison."""
        variables = {'STRENGTH': 18}

        output = self._run_cli(
            'evaluate "$STRENGTH > 15"',
            stdin_data=json.dumps(variables)
        )

        self.assertEqual(output['result'], True)

    def test_evaluate_command_string_concat(self):
        """Test evaluate command with string concatenation."""
        variables = {'NAME': 'Thorgrim'}

        output = self._run_cli(
            'evaluate \'"Hello " + $NAME\'',
            stdin_data=json.dumps(variables)
        )

        self.assertEqual(output['result'], 'Hello Thorgrim')

    def test_render_nonexistent_passage(self):
        """Test render with nonexistent passage."""
        variables = {}

        output = self._run_cli(
            f'render {self.test_story} NonExistent',
            stdin_data=json.dumps(variables)
        )

        self.assertIn('error', output)
        self.assertIn('Passage not found', output['error'])

    def test_parse_nonexistent_file(self):
        """Test parse with nonexistent file."""
        output = self._run_cli('parse /nonexistent/file.twee')

        self.assertIn('error', output)
        self.assertIn('File not found', output['error'])


class TestCLIVariableHandling(unittest.TestCase):
    """Test CLI variable handling via stdin."""

    def setUp(self):
        """Set up test environment."""
        self.cli = 'python3 tw1x_cli.py'

    def _run_cli(self, command: str, stdin_data: str = None) -> dict:
        """Run CLI command and return JSON output."""
        cmd_parts = ['python3', 'tw1x_cli.py'] + shlex.split(command)
        result = subprocess.run(
            cmd_parts,
            input=stdin_data,
            capture_output=True,
            text=True
        )

        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(f"Invalid JSON output:\n{result.stdout}\nStderr:\n{result.stderr}")

    def test_evaluate_empty_stdin(self):
        """Test evaluate with no stdin (empty variables)."""
        output = self._run_cli('evaluate "42"')

        self.assertEqual(output['result'], 42)

    def test_evaluate_with_variables(self):
        """Test evaluate with variables from stdin."""
        variables = {'A': 10, 'B': 20}

        output = self._run_cli(
            'evaluate "$A + $B"',
            stdin_data=json.dumps(variables)
        )

        self.assertEqual(output['result'], 30)

    def test_evaluate_missing_variable(self):
        """Test evaluate with missing variable (should return empty string)."""
        variables = {'A': 10}

        output = self._run_cli(
            'evaluate "$MISSING + 5"',
            stdin_data=json.dumps(variables)
        )

        # Missing variable treated as empty string, which fails arithmetic
        # Result should be None or error
        self.assertIn('errors', output)


class TestCLIJSONOutput(unittest.TestCase):
    """Test JSON output formatting."""

    def setUp(self):
        """Set up test environment."""
        self.cli = 'python3 tw1x_cli.py'
        self.test_story = 'engine/games/barbarian/data/story.twee'

        if not os.path.exists(self.test_story):
            self.skipTest("Barbarian story file not found")

    def _run_cli(self, command: str, stdin_data: str = None) -> str:
        """Run CLI and return raw output."""
        cmd_parts = ['python3', 'tw1x_cli.py'] + shlex.split(command)
        result = subprocess.run(
            cmd_parts,
            input=stdin_data,
            capture_output=True,
            text=True
        )
        return result.stdout

    def test_output_is_valid_json(self):
        """Test that all outputs are valid JSON."""
        commands = [
            f'info {self.test_story}',
            f'parse {self.test_story}',
        ]

        for cmd in commands:
            output = self._run_cli(cmd)
            try:
                json.loads(output)
            except json.JSONDecodeError:
                self.fail(f"Invalid JSON for command: {cmd}")

    def test_render_output_structure(self):
        """Test render output has expected structure."""
        variables = {'PLAYER_NAME': 'Test'}
        output = self._run_cli(
            f'render {self.test_story} Start',
            stdin_data=json.dumps(variables)
        )

        data = json.loads(output)

        # Required fields
        self.assertIn('text', data)
        self.assertIn('links', data)
        self.assertIn('variable_changes', data)
        self.assertIn('errors', data)

        # Check types
        self.assertIsInstance(data['text'], str)
        self.assertIsInstance(data['links'], list)
        self.assertIsInstance(data['variable_changes'], dict)
        self.assertIsInstance(data['errors'], list)


# ============================================================================
# Main - Run tests
# ============================================================================

if __name__ == '__main__':
    print("TW1X CLI Integration Tests")
    print("=" * 60)
    unittest.main(verbosity=2)
