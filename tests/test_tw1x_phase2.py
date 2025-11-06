#!/usr/bin/env python3
"""
Phase 2 tests for TW1X: Expression & Macro System

Tests for:
- Value parsing and type inference
- Expression evaluation
- <<set>> and <<print>> macros
- Conditionals (<<if>>/<<elseif>>/<<else>>/<<endif>>)
- Functions (either, random)
- Passage rendering

Run with: python3 test_tw1x_phase2.py
"""

import unittest
from tw1x import (
    TweeParser, parse_twee, parse_value,
    ExpressionEvaluator, MacroProcessor,
    VariableScope, ExecutionMode
)


class TestValueParsing(unittest.TestCase):
    """Test value parsing with type inference."""

    def test_parse_integer(self):
        """Test integer parsing."""
        self.assertEqual(parse_value("42"), 42)
        self.assertEqual(parse_value("0"), 0)
        self.assertEqual(parse_value("-10"), -10)

    def test_parse_float(self):
        """Test float parsing."""
        self.assertEqual(parse_value("3.14"), 3.14)
        self.assertEqual(parse_value("0.5"), 0.5)
        self.assertEqual(parse_value("-2.5"), -2.5)

    def test_parse_boolean(self):
        """Test boolean parsing."""
        self.assertEqual(parse_value("true"), True)
        self.assertEqual(parse_value("True"), True)
        self.assertEqual(parse_value("false"), False)
        self.assertEqual(parse_value("False"), False)

    def test_parse_string_quoted(self):
        """Test quoted string parsing."""
        self.assertEqual(parse_value('"hello"'), "hello")
        self.assertEqual(parse_value("'world'"), "world")
        self.assertEqual(parse_value('"hello world"'), "hello world")

    def test_parse_string_unquoted(self):
        """Test unquoted string parsing."""
        self.assertEqual(parse_value("hello"), "hello")
        self.assertEqual(parse_value("test"), "test")


class TestExpressionEvaluator(unittest.TestCase):
    """Test expression evaluation."""

    def setUp(self):
        """Create evaluator with test variables."""
        self.variables = {
            'HEALTH': 100,
            'DAMAGE': 25,
            'NAME': 'Thorgrim',
            'LEVEL': 5,
            'MULTIPLIER': 2.5
        }
        self.evaluator = ExpressionEvaluator(self.variables)

    def test_arithmetic_addition(self):
        """Test addition."""
        result = self.evaluator.evaluate('$HEALTH + $DAMAGE')
        self.assertEqual(result, 125)

    def test_arithmetic_subtraction(self):
        """Test subtraction."""
        result = self.evaluator.evaluate('$HEALTH - $DAMAGE')
        self.assertEqual(result, 75)

    def test_arithmetic_multiplication(self):
        """Test multiplication."""
        result = self.evaluator.evaluate('$DAMAGE * 2')
        self.assertEqual(result, 50)

    def test_arithmetic_division(self):
        """Test division."""
        result = self.evaluator.evaluate('$HEALTH / 2')
        self.assertEqual(result, 50.0)

    def test_arithmetic_complex(self):
        """Test complex expression."""
        result = self.evaluator.evaluate('($HEALTH + $DAMAGE) * 2')
        self.assertEqual(result, 250)

    def test_comparison_greater_than(self):
        """Test > operator."""
        result = self.evaluator.evaluate('$HEALTH > 50')
        self.assertEqual(result, True)

    def test_comparison_text_operators(self):
        """Test text operators (is, gt, lt, etc.)."""
        result = self.evaluator.evaluate('$HEALTH gt 50')
        self.assertEqual(result, True)

        result = self.evaluator.evaluate('$DAMAGE lt 30')
        self.assertEqual(result, True)

        result = self.evaluator.evaluate('$LEVEL is 5')
        self.assertEqual(result, True)

    def test_logical_and(self):
        """Test logical and."""
        result = self.evaluator.evaluate('$HEALTH > 50 and $LEVEL > 3')
        self.assertEqual(result, True)

    def test_logical_or(self):
        """Test logical or."""
        result = self.evaluator.evaluate('$HEALTH < 50 or $LEVEL > 3')
        self.assertEqual(result, True)

    def test_string_concatenation(self):
        """Test string concatenation."""
        result = self.evaluator.evaluate('"Hello " + $NAME')
        self.assertEqual(result, "Hello Thorgrim")

    def test_variable_case_insensitive(self):
        """Test case-insensitive variable lookup."""
        result = self.evaluator.evaluate('$health + 10')
        self.assertEqual(result, 110)

    def test_missing_variable(self):
        """Test missing variable returns empty string."""
        result = self.evaluator.evaluate('$MISSING_VAR + "test"')
        self.assertEqual(result, "test")


class TestMacroProcessor(unittest.TestCase):
    """Test macro processing."""

    def setUp(self):
        """Create processor with test variables."""
        self.variables = {}
        self.processor = MacroProcessor(self.variables)

    def test_set_macro_with_equals(self):
        """Test <<set $VAR = value>> syntax."""
        self.processor.process_set_macro('set $HEALTH = 100')
        self.assertEqual(self.variables['HEALTH'], 100)

    def test_set_macro_with_to(self):
        """Test <<set $VAR to value>> syntax."""
        self.processor.process_set_macro('set $NAME to "Thorgrim"')
        self.assertEqual(self.variables['NAME'], "Thorgrim")

    def test_set_macro_with_expression(self):
        """Test <<set>> with expression."""
        self.variables['HEALTH'] = 100
        self.processor = MacroProcessor(self.variables)
        self.processor.process_set_macro('set $NEW_HEALTH = $HEALTH + 50')
        self.assertEqual(self.variables['NEW_HEALTH'], 150)

    def test_print_macro(self):
        """Test <<print>> macro."""
        self.variables['NAME'] = "Thorgrim"
        self.processor = MacroProcessor(self.variables)
        result = self.processor.process_print_macro('print $NAME')
        self.assertEqual(result, "Thorgrim")

    def test_print_macro_with_expression(self):
        """Test <<print>> with expression."""
        self.variables['HEALTH'] = 100
        self.processor = MacroProcessor(self.variables)
        result = self.processor.process_print_macro('print $HEALTH + 50')
        self.assertEqual(result, "150")

    def test_evaluate_condition_true(self):
        """Test condition evaluation (true)."""
        self.variables['STRENGTH'] = 18
        self.processor = MacroProcessor(self.variables)
        result = self.processor.evaluate_condition('$STRENGTH > 15')
        self.assertTrue(result)

    def test_evaluate_condition_false(self):
        """Test condition evaluation (false)."""
        self.variables['STRENGTH'] = 10
        self.processor = MacroProcessor(self.variables)
        result = self.processor.evaluate_condition('$STRENGTH > 15')
        self.assertFalse(result)


class TestStoryInitParsing(unittest.TestCase):
    """Test StoryInit passage parsing."""

    def test_story_init_extracts_variables(self):
        """Test that StoryInit parses variables correctly."""
        content = """
:: StoryInit
<<set $PLAYER_NAME to "Thorgrim">>
<<set $STRENGTH = 18>>
<<set $RAGE to 0>>
<<set $HONOR = 10>>

:: Start
Game content.
"""
        result = parse_twee(content)

        # Check that variables were extracted
        self.assertIn('PLAYER_NAME', result.story_init_vars)
        self.assertEqual(result.story_init_vars['PLAYER_NAME'], "Thorgrim")
        self.assertEqual(result.story_init_vars['STRENGTH'], 18)
        self.assertEqual(result.story_init_vars['RAGE'], 0)
        self.assertEqual(result.story_init_vars['HONOR'], 10)


class TestPassageRendering(unittest.TestCase):
    """Test passage rendering with macros."""

    def test_render_with_print(self):
        """Test rendering with <<print>> macro."""
        content = """
:: Test
Your name is <<print $NAME>>.
"""
        result = parse_twee(content)
        parser = TweeParser()
        passage = result.passages['Test']

        variables = {'NAME': 'Thorgrim'}
        render_result = parser.render_passage(passage, variables)

        self.assertIn('Your name is Thorgrim', render_result.text)

    def test_render_with_conditionals(self):
        """Test rendering with <<if>> conditionals."""
        content = """
:: Test
<<if $STRENGTH > 15>>
You are strong!
<<else>>
You are weak.
<<endif>>
"""
        result = parse_twee(content)
        parser = TweeParser()
        passage = result.passages['Test']

        # Strong character
        variables = {'STRENGTH': 18}
        render_result = parser.render_passage(passage, variables)
        self.assertIn('You are strong!', render_result.text)
        self.assertNotIn('You are weak', render_result.text)

        # Weak character
        variables = {'STRENGTH': 10}
        render_result = parser.render_passage(passage, variables)
        self.assertIn('You are weak', render_result.text)
        self.assertNotIn('You are strong!', render_result.text)

    def test_render_with_elseif(self):
        """Test rendering with <<elseif>>."""
        content = """
:: Test
<<if $HEALTH > 80>>
Healthy
<<elseif $HEALTH > 50>>
Wounded
<<else>>
Critical
<<endif>>
"""
        result = parse_twee(content)
        parser = TweeParser()
        passage = result.passages['Test']

        # Healthy
        render_result = parser.render_passage(passage, {'HEALTH': 90})
        self.assertIn('Healthy', render_result.text)

        # Wounded
        render_result = parser.render_passage(passage, {'HEALTH': 60})
        self.assertIn('Wounded', render_result.text)

        # Critical
        render_result = parser.render_passage(passage, {'HEALTH': 30})
        self.assertIn('Critical', render_result.text)

    def test_render_with_nobr(self):
        """Test <<nobr>> macro removes line breaks."""
        content = """
:: Test
<<nobr>>
Line one
Line two
Line three
<<endnobr>>
"""
        result = parse_twee(content)
        parser = TweeParser()
        passage = result.passages['Test']

        render_result = parser.render_passage(passage, {})
        # Should have spaces instead of newlines
        self.assertIn('Line one Line two Line three', render_result.text)


class TestBarbarianStoryWithVariables(unittest.TestCase):
    """Integration test with barbarian story and variable rendering."""

    def test_barbarian_story_init(self):
        """Test that barbarian StoryInit variables are parsed."""
        import os

        story_path = 'engine/games/barbarian/data/story.twee'
        if not os.path.exists(story_path):
            self.skipTest("Barbarian story file not found")

        with open(story_path, 'r') as f:
            content = f.read()

        result = parse_twee(content)

        # Verify StoryInit variables were extracted
        self.assertIn('PLAYER_NAME', result.story_init_vars)
        self.assertIn('STRENGTH', result.story_init_vars)
        self.assertIn('RAGE', result.story_init_vars)
        self.assertIn('HONOR', result.story_init_vars)

        # Verify values
        self.assertEqual(result.story_init_vars['PLAYER_NAME'], "Thorgrim")
        self.assertEqual(result.story_init_vars['STRENGTH'], 18)
        self.assertEqual(result.story_init_vars['RAGE'], 0)
        self.assertEqual(result.story_init_vars['HONOR'], 10)

    def test_render_start_passage(self):
        """Test rendering the Start passage with variables."""
        import os

        story_path = 'engine/games/barbarian/data/story.twee'
        if not os.path.exists(story_path):
            self.skipTest("Barbarian story file not found")

        with open(story_path, 'r') as f:
            content = f.read()

        result = parse_twee(content)
        parser = TweeParser()

        # Get Start passage
        start_passage = result.passages['Start']

        # Render with StoryInit variables
        variables = result.story_init_vars.copy()
        render_result = parser.render_passage(start_passage, variables)

        # Should contain rendered player name
        self.assertIn('Thorgrim', render_result.text)

        # Should contain stats
        self.assertIn('18', render_result.text)  # Strength
        self.assertIn('10', render_result.text)  # Honor
        self.assertIn('0', render_result.text)   # Rage

        # Should have link to LONGHOUSE
        self.assertEqual(len(render_result.links), 1)
        self.assertEqual(render_result.links[0].target, 'LONGHOUSE')


# ============================================================================
# Main - Run tests
# ============================================================================

if __name__ == '__main__':
    print("TW1X Phase 2 Tests: Expression & Macro System")
    print("=" * 60)
    unittest.main(verbosity=2)
