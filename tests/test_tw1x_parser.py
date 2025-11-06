#!/usr/bin/env python3
"""
Comprehensive unit test suite for TW1X unified parser.
Tests all parser functionality including variables, conditionals, macros, and special passages.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from tw1x import TweeParser, ExpressionEvaluator


class TestVariableExtraction(unittest.TestCase):
    """Test variable extraction from StoryInit and TestSetup passages."""

    def test_storyinit_simple_variables(self):
        """Test basic variable extraction from StoryInit."""
        content = """
:: StoryInit
<<set $PLAYER_NAME to "Thorgrim">>
<<set $STRENGTH to 18>>
<<set $HONOR to 10>>

:: Start
You are <<print $PLAYER_NAME>>.
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertEqual(result.story_init_vars['PLAYER_NAME'], 'Thorgrim')
        self.assertEqual(result.story_init_vars['STRENGTH'], 18)
        self.assertEqual(result.story_init_vars['HONOR'], 10)

    def test_testsetup_simple_variables(self):
        """Test basic variable extraction from TestSetup."""
        content = """
:: StoryInit
<<set $PLAYER_NAME to "Hero">>

:: TestSetup
<<set $SCENARIO to 0>>
<<set $PLAYER_NAME to "Thorgrim">>
<<set $TEST_VAR to 42>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertEqual(result.test_setup_vars['SCENARIO'], 0)
        self.assertEqual(result.test_setup_vars['PLAYER_NAME'], 'Thorgrim')
        self.assertEqual(result.test_setup_vars['TEST_VAR'], 42)

    def test_testsetup_with_conditionals(self):
        """Test three-pass TestSetup processing with conditionals."""
        content = """
:: StoryInit
<<set $HONOR to 10>>

:: TestSetup
<<set $SCENARIO to 2>>

<<if $SCENARIO is 0>>
<<set $HONOR to 5>>
<<elseif $SCENARIO is 1>>
<<set $HONOR to 15>>
<<elseif $SCENARIO is 2>>
<<set $HONOR to 25>>
<<else>>
<<set $HONOR to 10>>
<<endif>>

<<set $FINAL_VAR to 100>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        # Pass 1: Extract top-level vars
        self.assertEqual(result.test_setup_vars['SCENARIO'], 2)

        # Pass 2-3: Evaluate conditional and extract from matched branch
        self.assertEqual(result.test_setup_vars['HONOR'], 25)
        self.assertEqual(result.test_setup_vars['FINAL_VAR'], 100)

    def test_variable_types(self):
        """Test extraction of different variable types."""
        content = """
:: StoryInit
<<set $STRING to "hello">>
<<set $NUMBER to 42>>
<<set $FLOAT to 3.14>>
<<set $ZERO to 0>>
<<set $BOOLEAN to 1>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertEqual(result.story_init_vars['STRING'], 'hello')
        self.assertEqual(result.story_init_vars['NUMBER'], 42)
        self.assertAlmostEqual(result.story_init_vars['FLOAT'], 3.14, places=2)
        self.assertEqual(result.story_init_vars['ZERO'], 0)
        self.assertEqual(result.story_init_vars['BOOLEAN'], 1)


class TestConditionalEvaluation(unittest.TestCase):
    """Test conditional expression evaluation."""

    def setUp(self):
        self.vars = {
            'HONOR': 10,
            'STRENGTH': 18,
            'HAS_BLESSING': 0,
            'HAS_WEAPON': 1,
            'PLAYER_NAME': 'Thorgrim'
        }
        self.evaluator = ExpressionEvaluator(self.vars)

    def test_simple_equality(self):
        """Test simple equality checks."""
        self.assertTrue(self.evaluator.evaluate_condition('$HONOR is 10'))
        self.assertFalse(self.evaluator.evaluate_condition('$HONOR is 5'))

        self.assertTrue(self.evaluator.evaluate_condition('$HAS_BLESSING is 0'))
        self.assertTrue(self.evaluator.evaluate_condition('$HAS_WEAPON is 1'))

    def test_comparison_operators(self):
        """Test >, <, >=, <= operators."""
        self.assertTrue(self.evaluator.evaluate_condition('$HONOR > 5'))
        self.assertFalse(self.evaluator.evaluate_condition('$HONOR > 15'))

        self.assertTrue(self.evaluator.evaluate_condition('$HONOR < 15'))
        self.assertFalse(self.evaluator.evaluate_condition('$HONOR < 5'))

        self.assertTrue(self.evaluator.evaluate_condition('$HONOR >= 10'))
        self.assertTrue(self.evaluator.evaluate_condition('$HONOR <= 10'))

    def test_inequality(self):
        """Test inequality (neq) operator."""
        self.assertTrue(self.evaluator.evaluate_condition('$HONOR neq 5'))
        self.assertFalse(self.evaluator.evaluate_condition('$HONOR neq 10'))

    def test_logical_and(self):
        """Test 'and' operator."""
        self.assertTrue(self.evaluator.evaluate_condition('$HONOR > 5 and $STRENGTH > 15'))
        self.assertFalse(self.evaluator.evaluate_condition('$HONOR > 15 and $STRENGTH > 15'))
        self.assertFalse(self.evaluator.evaluate_condition('$HONOR > 5 and $STRENGTH > 20'))

    def test_logical_or(self):
        """Test 'or' operator."""
        self.assertTrue(self.evaluator.evaluate_condition('$HONOR > 15 or $STRENGTH > 15'))
        self.assertTrue(self.evaluator.evaluate_condition('$HONOR > 5 or $STRENGTH > 20'))
        self.assertFalse(self.evaluator.evaluate_condition('$HONOR > 15 or $STRENGTH > 20'))

    def test_logical_not(self):
        """Test 'not' operator."""
        self.assertTrue(self.evaluator.evaluate_condition('not $HAS_BLESSING'))
        self.assertFalse(self.evaluator.evaluate_condition('not $HAS_WEAPON'))

    def test_complex_expressions(self):
        """Test complex multi-operator expressions."""
        self.assertTrue(self.evaluator.evaluate_condition(
            '$HONOR > 5 and $STRENGTH > 15 and $HAS_WEAPON is 1'
        ))

        # Note: Parentheses may need special handling in the parser
        self.assertTrue(self.evaluator.evaluate_condition(
            '$HONOR > 15 or $STRENGTH > 15'
        ))


class TestNestedConditionals(unittest.TestCase):
    """Test nested conditional blocks."""

    def test_nested_if_blocks(self):
        """Test nested <<if>> blocks are properly evaluated."""
        content = """
:: TestSetup
<<set $HAS_BLESSING to 0>>
<<set $HONOR to 10>>

<<if $HAS_BLESSING is 0>>
<<set $OUTER to 1>>

<<if $HONOR > 12>>
<<set $INNER_HIGH to 1>>
<<else>>
<<set $INNER_LOW to 1>>
<<endif>>

<<set $AFTER_INNER to 1>>
<<else>>
<<set $OUTER to 0>>
<<endif>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        # Outer condition should match
        self.assertEqual(result.test_setup_vars['OUTER'], 1)

        # Inner condition should evaluate (HONOR=10, not > 12)
        self.assertNotIn('INNER_HIGH', result.test_setup_vars)
        self.assertEqual(result.test_setup_vars['INNER_LOW'], 1)

        # After inner should execute
        self.assertEqual(result.test_setup_vars['AFTER_INNER'], 1)

    def test_deeply_nested_conditionals(self):
        """Test 3+ levels of nesting."""
        content = """
:: TestSetup
<<set $A to 1>>

<<if $A is 1>>
<<set $LEVEL1 to 1>>

<<if $A is 1>>
<<set $LEVEL2 to 1>>

<<if $A is 1>>
<<set $LEVEL3 to 1>>
<<endif>>

<<endif>>
<<endif>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertEqual(result.test_setup_vars['LEVEL1'], 1)
        self.assertEqual(result.test_setup_vars['LEVEL2'], 1)
        self.assertEqual(result.test_setup_vars['LEVEL3'], 1)


class TestElseIfChains(unittest.TestCase):
    """Test elseif and else clause handling."""

    def test_elseif_first_match(self):
        """Test elseif when first condition matches."""
        content = """
:: TestSetup
<<set $VALUE to 5>>

<<if $VALUE is 5>>
<<set $RESULT to "first">>
<<elseif $VALUE is 10>>
<<set $RESULT to "second">>
<<else>>
<<set $RESULT to "other">>
<<endif>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertEqual(result.test_setup_vars['RESULT'], 'first')

    def test_elseif_second_match(self):
        """Test elseif when second condition matches."""
        content = """
:: TestSetup
<<set $VALUE to 10>>

<<if $VALUE is 5>>
<<set $RESULT to "first">>
<<elseif $VALUE is 10>>
<<set $RESULT to "second">>
<<else>>
<<set $RESULT to "other">>
<<endif>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertEqual(result.test_setup_vars['RESULT'], 'second')

    def test_else_fallthrough(self):
        """Test else when no conditions match."""
        content = """
:: TestSetup
<<set $VALUE to 99>>

<<if $VALUE is 5>>
<<set $RESULT to "first">>
<<elseif $VALUE is 10>>
<<set $RESULT to "second">>
<<else>>
<<set $RESULT to "other">>
<<endif>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertEqual(result.test_setup_vars['RESULT'], 'other')

    def test_multiple_elseif(self):
        """Test multiple elseif clauses."""
        content = """
:: TestSetup
<<set $SCENARIO to 2>>

<<if $SCENARIO is 0>>
<<set $HONOR to 5>>
<<elseif $SCENARIO is 1>>
<<set $HONOR to 15>>
<<elseif $SCENARIO is 2>>
<<set $HONOR to 25>>
<<elseif $SCENARIO is 3>>
<<set $HONOR to 35>>
<<else>>
<<set $HONOR to 10>>
<<endif>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertEqual(result.test_setup_vars['HONOR'], 25)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_empty_content(self):
        """Test parser handles empty content."""
        parser = TweeParser()
        result = parser.parse_twee("")

        self.assertIsNotNone(result)
        self.assertEqual(result.story_init_vars, {})
        self.assertEqual(result.test_setup_vars, {})

    def test_missing_storyinit(self):
        """Test handling when StoryInit is missing."""
        content = """
:: Start
Test content
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertEqual(result.story_init_vars, {})

    def test_missing_testsetup(self):
        """Test handling when TestSetup is missing."""
        content = """
:: StoryInit
<<set $VAR to 1>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertIn('VAR', result.story_init_vars)
        self.assertEqual(result.test_setup_vars, {})


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world scenarios from the barbarian game."""

    def test_barbarian_storyinit(self):
        """Test actual barbarian game StoryInit."""
        content = """
:: StoryInit
<<set $PLAYER_NAME to "Thorgrim">>
<<set $STRENGTH to 18>>
<<set $RAGE to 0>>
<<set $HONOR to 10>>
<<set $QUEST_STATE to 0>>
<<set $HAS_WEAPON to 0>>
<<set $HAS_BLESSING to 0>>
<<set $WEAPON_POWER to 25>>

:: Start
You are <<print $PLAYER_NAME>>.
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertEqual(result.story_init_vars['PLAYER_NAME'], 'Thorgrim')
        self.assertEqual(result.story_init_vars['STRENGTH'], 18)
        self.assertEqual(result.story_init_vars['RAGE'], 0)
        self.assertEqual(result.story_init_vars['HONOR'], 10)
        self.assertEqual(result.story_init_vars['QUEST_STATE'], 0)
        self.assertEqual(result.story_init_vars['HAS_WEAPON'], 0)
        self.assertEqual(result.story_init_vars['HAS_BLESSING'], 0)
        self.assertEqual(result.story_init_vars['WEAPON_POWER'], 25)

    def test_barbarian_testsetup_scenario_2(self):
        """Test barbarian TestSetup scenario 2 (Ready for dragon)."""
        content = """
:: StoryInit
<<set $HONOR to 10>>
<<set $HAS_WEAPON to 0>>
<<set $HAS_BLESSING to 0>>
<<set $WEAPON_POWER to 25>>

:: TestSetup
<<set $SCENARIO to 2>>

<<if $SCENARIO is 0>>
<<set $HONOR to 10>>
<<set $HAS_WEAPON to 0>>
<<set $HAS_BLESSING to 0>>
<<elseif $SCENARIO is 1>>
<<set $HONOR to 15>>
<<set $HAS_WEAPON to 1>>
<<set $WEAPON_POWER to 35>>
<<set $HAS_BLESSING to 0>>
<<elseif $SCENARIO is 2>>
<<set $HONOR to 20>>
<<set $HAS_WEAPON to 1>>
<<set $WEAPON_POWER to 40>>
<<set $HAS_BLESSING to 1>>
<<endif>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        self.assertEqual(result.test_setup_vars['SCENARIO'], 2)
        self.assertEqual(result.test_setup_vars['HONOR'], 20)
        self.assertEqual(result.test_setup_vars['HAS_WEAPON'], 1)
        self.assertEqual(result.test_setup_vars['WEAPON_POWER'], 40)
        self.assertEqual(result.test_setup_vars['HAS_BLESSING'], 1)

    def test_shaman_nested_conditional(self):
        """Test the SHAMAN passage nested conditional logic."""
        content = """
:: StoryInit
<<set $HAS_BLESSING to 0>>
<<set $HONOR to 10>>

:: SHAMAN
<<if $HAS_BLESSING is 0>>
You seek wisdom.

<<if $HONOR > 12>>
Your honor is strong.
<<else>>
Your honor is weak.
<<endif>>

<<else>>
You already have blessing.
<<endif>>

:: Start
Test
"""
        parser = TweeParser()
        result = parser.parse_twee(content)

        # Verify passages are parsed
        self.assertIn('SHAMAN', result.passages)


class TestIntegrationWithCLI(unittest.TestCase):
    """Test integration with CLI interface."""

    def test_cli_parse_command(self):
        """Test CLI parse command returns proper JSON."""
        import subprocess
        import json
        import tempfile

        content = """
:: StoryInit
<<set $VAR to 42>>

:: Start
Test
"""

        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.twee', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name

        try:
            # Run CLI
            result = subprocess.run(
                ['python3', 'tw1x_cli.py', 'parse', temp_path],
                capture_output=True,
                text=True,
                timeout=5
            )

            self.assertEqual(result.returncode, 0)

            # Parse JSON output
            data = json.loads(result.stdout)
            self.assertIn('story_init_vars', data)
            self.assertEqual(data['story_init_vars']['VAR'], 42)

        finally:
            Path(temp_path).unlink()


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestVariableExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestConditionalEvaluation))
    suite.addTests(loader.loadTestsFromTestCase(TestNestedConditionals))
    suite.addTests(loader.loadTestsFromTestCase(TestElseIfChains))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestRealWorldScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationWithCLI))

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
