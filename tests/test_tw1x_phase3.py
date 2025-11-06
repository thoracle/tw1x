#!/usr/bin/env python3
"""
Phase 3 tests for TW1X: Special Passages (StoryInit & TestSetup)

Tests for:
- StoryInit variable extraction
- TestSetup three-pass processing
- Conditional evaluation in TestSetup
- All barbarian story scenarios

Run with: python3 test_tw1x_phase3.py
"""

import unittest
from tw1x import parse_twee


class TestStoryInitProcessing(unittest.TestCase):
    """Test StoryInit passage processing."""

    def test_story_init_basic(self):
        """Test basic StoryInit processing."""
        content = """
:: StoryInit
<<set $HEALTH to 100>>
<<set $GOLD = 50>>
<<set $NAME to "Hero">>

:: Start
Game starts.
"""
        result = parse_twee(content)

        self.assertEqual(result.story_init_vars['HEALTH'], 100)
        self.assertEqual(result.story_init_vars['GOLD'], 50)
        self.assertEqual(result.story_init_vars['NAME'], "Hero")

    def test_story_init_with_expressions(self):
        """Test StoryInit with expressions."""
        content = """
:: StoryInit
<<set $BASE to 10>>
<<set $DOUBLED = $BASE * 2>>
<<set $GREETING to "Hello " + "World">>

:: Start
Game starts.
"""
        result = parse_twee(content)

        self.assertEqual(result.story_init_vars['BASE'], 10)
        self.assertEqual(result.story_init_vars['DOUBLED'], 20)
        self.assertEqual(result.story_init_vars['GREETING'], "Hello World")

    def test_story_init_mixed_operators(self):
        """Test StoryInit with both = and to operators."""
        content = """
:: StoryInit
<<set $VAR1 = 100>>
<<set $VAR2 to 200>>
<<set $VAR3 = "test">>
<<set $VAR4 to "value">>

:: Start
Game starts.
"""
        result = parse_twee(content)

        self.assertEqual(result.story_init_vars['VAR1'], 100)
        self.assertEqual(result.story_init_vars['VAR2'], 200)
        self.assertEqual(result.story_init_vars['VAR3'], "test")
        self.assertEqual(result.story_init_vars['VAR4'], "value")


class TestTestSetupThreePass(unittest.TestCase):
    """Test TestSetup three-pass processing."""

    def test_testsetup_pass1_only(self):
        """Test TestSetup with only top-level variables (no conditionals)."""
        content = """
:: TestSetup [$metadata]
<<set $VAR1 to 10>>
<<set $VAR2 to 20>>

:: Start
Game starts.
"""
        result = parse_twee(content)

        self.assertEqual(result.test_setup_vars['VAR1'], 10)
        self.assertEqual(result.test_setup_vars['VAR2'], 20)

    def test_testsetup_three_pass_if(self):
        """Test TestSetup with if/else conditional."""
        content = """
:: TestSetup [$metadata]
<<set $SCENARIO to 1>>

<<if $SCENARIO is 1>>
  <<set $NAME to "Alice">>
  <<set $LEVEL to 5>>
<<else>>
  <<set $NAME to "Bob">>
  <<set $LEVEL to 10>>
<<endif>>

:: Start
Game starts.
"""
        result = parse_twee(content)

        # Pass 1: SCENARIO
        self.assertEqual(result.test_setup_vars['SCENARIO'], 1)

        # Pass 3: Variables from matched branch
        self.assertEqual(result.test_setup_vars['NAME'], "Alice")
        self.assertEqual(result.test_setup_vars['LEVEL'], 5)

    def test_testsetup_three_pass_elseif(self):
        """Test TestSetup with elseif branches."""
        content = """
:: TestSetup [$metadata]
<<set $SCENARIO to 2>>

<<if $SCENARIO is 1>>
  <<set $RESULT to "First">>
<<elseif $SCENARIO is 2>>
  <<set $RESULT to "Second">>
<<elseif $SCENARIO is 3>>
  <<set $RESULT to "Third">>
<<else>>
  <<set $RESULT to "Default">>
<<endif>>

:: Start
Game starts.
"""
        result = parse_twee(content)

        self.assertEqual(result.test_setup_vars['SCENARIO'], 2)
        self.assertEqual(result.test_setup_vars['RESULT'], "Second")

    def test_testsetup_else_branch(self):
        """Test TestSetup else branch execution."""
        content = """
:: TestSetup [$metadata]
<<set $SCENARIO to 99>>

<<if $SCENARIO is 1>>
  <<set $RESULT to "One">>
<<elseif $SCENARIO is 2>>
  <<set $RESULT to "Two">>
<<else>>
  <<set $RESULT to "Other">>
<<endif>>

:: Start
Game starts.
"""
        result = parse_twee(content)

        self.assertEqual(result.test_setup_vars['SCENARIO'], 99)
        self.assertEqual(result.test_setup_vars['RESULT'], "Other")

    def test_testsetup_multiple_variables_per_branch(self):
        """Test multiple <<set>> in each branch."""
        content = """
:: TestSetup [$metadata]
<<set $MODE to "test">>

<<if $MODE is "test">>
  <<set $VAR1 to 1>>
  <<set $VAR2 to 2>>
  <<set $VAR3 to 3>>
<<else>>
  <<set $VAR1 to 10>>
  <<set $VAR2 to 20>>
<<endif>>

:: Start
Game starts.
"""
        result = parse_twee(content)

        self.assertEqual(result.test_setup_vars['MODE'], "test")
        self.assertEqual(result.test_setup_vars['VAR1'], 1)
        self.assertEqual(result.test_setup_vars['VAR2'], 2)
        self.assertEqual(result.test_setup_vars['VAR3'], 3)


class TestBarbarianStoryScenarios(unittest.TestCase):
    """Test all barbarian story TestSetup scenarios."""

    def _load_barbarian_story_with_scenario(self, scenario_num):
        """Helper to load barbarian story and modify SCENARIO."""
        import os

        story_path = 'engine/games/barbarian/data/story.twee'
        if not os.path.exists(story_path):
            self.skipTest("Barbarian story file not found")

        with open(story_path, 'r') as f:
            content = f.read()

        # Replace SCENARIO value
        content = content.replace(
            '<<set $SCENARIO to 9>>',
            f'<<set $SCENARIO to {scenario_num}>>'
        )

        return parse_twee(content)

    def test_scenario_0_default(self):
        """Test SCENARIO=0 (default settings)."""
        result = self._load_barbarian_story_with_scenario(0)
        vars = result.test_setup_vars

        self.assertEqual(vars['SCENARIO'], 0)
        self.assertEqual(vars['PLAYER_NAME'], "Thorgrim")
        self.assertEqual(vars['STRENGTH'], 18)
        self.assertEqual(vars['RAGE'], 0)
        self.assertEqual(vars['HONOR'], 10)
        self.assertEqual(vars['QUEST_STATE'], 0)
        self.assertEqual(vars['HAS_WEAPON'], 0)
        self.assertEqual(vars['HAS_BLESSING'], 0)
        self.assertEqual(vars['WEAPON_POWER'], 0)

    def test_scenario_1_furious(self):
        """Test SCENARIO=1 (Thorgrim the Furious)."""
        result = self._load_barbarian_story_with_scenario(1)
        vars = result.test_setup_vars

        self.assertEqual(vars['SCENARIO'], 1)
        self.assertEqual(vars['PLAYER_NAME'], "Thorgrim the Furious")
        self.assertEqual(vars['STRENGTH'], 18)
        self.assertEqual(vars['RAGE'], 25)
        self.assertEqual(vars['HONOR'], 15)
        self.assertEqual(vars['QUEST_STATE'], 4)
        self.assertEqual(vars['HAS_WEAPON'], 1)
        self.assertEqual(vars['HAS_BLESSING'], 0)
        self.assertEqual(vars['WEAPON_POWER'], 40)

    def test_scenario_2_honorable(self):
        """Test SCENARIO=2 (Thorgrim the Honorable)."""
        result = self._load_barbarian_story_with_scenario(2)
        vars = result.test_setup_vars

        self.assertEqual(vars['SCENARIO'], 2)
        self.assertEqual(vars['PLAYER_NAME'], "Thorgrim the Honorable")
        self.assertEqual(vars['RAGE'], 5)
        self.assertEqual(vars['HONOR'], 20)
        self.assertEqual(vars['HAS_BLESSING'], 1)
        self.assertEqual(vars['WEAPON_POWER'], 25)

    def test_scenario_3_champion(self):
        """Test SCENARIO=3 (Thorgrim the Champion)."""
        result = self._load_barbarian_story_with_scenario(3)
        vars = result.test_setup_vars

        self.assertEqual(vars['SCENARIO'], 3)
        self.assertEqual(vars['PLAYER_NAME'], "Thorgrim the Champion")
        self.assertEqual(vars['RAGE'], 15)
        self.assertEqual(vars['HONOR'], 20)
        self.assertEqual(vars['HAS_BLESSING'], 1)
        self.assertEqual(vars['WEAPON_POWER'], 40)

    def test_scenario_4_mid_quest(self):
        """Test SCENARIO=4 (mid-quest state)."""
        result = self._load_barbarian_story_with_scenario(4)
        vars = result.test_setup_vars

        self.assertEqual(vars['SCENARIO'], 4)
        self.assertEqual(vars['HONOR'], 15)
        self.assertEqual(vars['QUEST_STATE'], 2)
        self.assertEqual(vars['WEAPON_POWER'], 40)

    def test_scenario_5_specific_state(self):
        """Test SCENARIO=5 (specific test state)."""
        result = self._load_barbarian_story_with_scenario(5)
        vars = result.test_setup_vars

        self.assertEqual(vars['SCENARIO'], 5)
        self.assertEqual(vars['RAGE'], 15)
        self.assertEqual(vars['HONOR'], 16)
        self.assertEqual(vars['WEAPON_POWER'], 26)

    def test_scenario_6_weak_warrior(self):
        """Test SCENARIO=6 (weak warrior)."""
        result = self._load_barbarian_story_with_scenario(6)
        vars = result.test_setup_vars

        self.assertEqual(vars['SCENARIO'], 6)
        self.assertEqual(vars['PLAYER_NAME'], "Weak Warrior")
        self.assertEqual(vars['STRENGTH'], 15)
        self.assertEqual(vars['RAGE'], 5)
        self.assertEqual(vars['HONOR'], 10)
        self.assertEqual(vars['WEAPON_POWER'], 20)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""

    def test_testsetup_without_conditionals(self):
        """Test TestSetup with no conditional blocks."""
        content = """
:: TestSetup [$metadata]
<<set $VAR1 to 100>>
<<set $VAR2 to 200>>

:: Start
Content.
"""
        result = parse_twee(content)

        self.assertEqual(result.test_setup_vars['VAR1'], 100)
        self.assertEqual(result.test_setup_vars['VAR2'], 200)

    def test_empty_testsetup(self):
        """Test empty TestSetup passage."""
        content = """
:: TestSetup [$metadata]

:: Start
Content.
"""
        result = parse_twee(content)

        self.assertEqual(len(result.test_setup_vars), 0)

    def test_no_testsetup(self):
        """Test story without TestSetup passage."""
        content = """
:: Start
Content.
"""
        result = parse_twee(content)

        self.assertEqual(len(result.test_setup_vars), 0)


# ============================================================================
# Main - Run tests
# ============================================================================

if __name__ == '__main__':
    print("TW1X Phase 3 Tests: Special Passages (StoryInit & TestSetup)")
    print("=" * 60)
    unittest.main(verbosity=2)
