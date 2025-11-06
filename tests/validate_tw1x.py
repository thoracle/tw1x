#!/usr/bin/env python3
"""
TW1X Parser Validation Script
Validates all parser features using the test_story.twee file
"""

from tw1x import TweeParser, ExpressionEvaluator
import sys

def validate_parsing():
    """Validate basic parsing functionality."""
    print("=" * 70)
    print("TEST 1: BASIC PARSING")
    print("=" * 70)

    parser = TweeParser()
    with open('test_story.twee', 'r') as f:
        content = f.read()

    result = parser.parse_twee(content)

    print(f"✓ Parsed {len(result.passages)} passages")
    print(f"✓ Found {len(result.story_init_vars)} StoryInit variables")
    print(f"✓ Found {len(result.test_setup_vars)} TestSetup variables")
    print(f"✓ Errors: {len(result.errors)}")

    assert len(result.passages) == 15, f"Expected 15 passages, got {len(result.passages)}"
    assert len(result.errors) == 0, f"Parser errors: {result.errors}"

    print("\n✓ PASS: Basic parsing works\n")
    return True

def validate_storyinit():
    """Validate StoryInit variable extraction."""
    print("=" * 70)
    print("TEST 2: STORYINIT VARIABLES")
    print("=" * 70)

    parser = TweeParser()
    with open('test_story.twee', 'r') as f:
        content = f.read()

    result = parser.parse_twee(content)
    vars = result.story_init_vars

    expected = {
        'PLAYER_NAME': 'Hero',
        'HEALTH': 100,
        'MAX_HEALTH': 100,
        'GOLD': 50,
        'STRENGTH': 10,
        'WISDOM': 8,
        'HAS_SWORD': 0,
        'HAS_SHIELD': 0,
        'HAS_MAGIC_RING': 0,
        'QUEST_STAGE': 0,
        'REPUTATION': 0,
        'COMPANION': ''
    }

    for key, expected_val in expected.items():
        actual_val = vars.get(key)
        status = "✓" if actual_val == expected_val else "✗"
        print(f"{status} {key}: {actual_val} (expected: {expected_val})")
        assert actual_val == expected_val, f"{key} mismatch"

    print("\n✓ PASS: StoryInit extraction works\n")
    return True

def validate_testsetup_scenarios():
    """Validate TestSetup conditional processing."""
    print("=" * 70)
    print("TEST 3: TESTSETUP CONDITIONAL PROCESSING")
    print("=" * 70)

    with open('test_story.twee', 'r') as f:
        content = f.read()

    scenarios = [
        (0, 'Tester', 100, 50, 0, True),  # has_sword expected, check_sword
        (1, 'Warrior', 150, 100, 1, True),
        (2, 'Wizard', 80, 200, 0, False),  # Wizard branch doesn't set HAS_SWORD
        (3, 'Champion', 200, 500, 1, True),
    ]

    for scenario_num, expected_name, expected_health, expected_gold, expected_sword, check_sword in scenarios:
        test_content = content.replace(
            '<<set $SCENARIO to 0>>',
            f'<<set $SCENARIO to {scenario_num}>>'
        )

        parser = TweeParser()
        result = parser.parse_twee(test_content)
        vars = result.test_setup_vars

        print(f"\nScenario {scenario_num}:")
        print(f"  Name: {vars.get('PLAYER_NAME')} (expected: {expected_name})")
        print(f"  Health: {vars.get('HEALTH')} (expected: {expected_health})")
        print(f"  Gold: {vars.get('GOLD')} (expected: {expected_gold})")
        if check_sword:
            print(f"  Has Sword: {vars.get('HAS_SWORD')} (expected: {expected_sword})")

        assert vars.get('SCENARIO') == scenario_num
        assert vars.get('PLAYER_NAME') == expected_name
        assert vars.get('HEALTH') == expected_health
        assert vars.get('GOLD') == expected_gold
        if check_sword:
            assert vars.get('HAS_SWORD') == expected_sword
        assert vars.get('TEST_VAR') == 42  # Should always be set

        print(f"  ✓ Scenario {scenario_num} correct")

    print("\n✓ PASS: TestSetup conditional processing works\n")
    return True

def validate_expression_evaluator():
    """Validate expression evaluation."""
    print("=" * 70)
    print("TEST 4: EXPRESSION EVALUATION")
    print("=" * 70)

    vars = {
        'HEALTH': 100,
        'STRENGTH': 15,
        'WISDOM': 8,
        'HAS_SWORD': 1,
        'HAS_SHIELD': 0,
        'GOLD': 50
    }

    evaluator = ExpressionEvaluator(vars)

    tests = [
        # (expression, expected_result, description)
        ('$HEALTH is 100', True, 'Simple equality'),
        ('$HEALTH > 50', True, 'Greater than'),
        ('$HEALTH < 150', True, 'Less than'),
        ('$HEALTH >= 100', True, 'Greater or equal'),
        ('$HEALTH <= 100', True, 'Less or equal'),
        ('$HEALTH neq 50', True, 'Not equal'),
        ('$STRENGTH > 10 and $HEALTH > 50', True, 'AND operator'),
        ('$STRENGTH > 20 or $WISDOM > 5', True, 'OR operator'),
        ('not $HAS_SHIELD', True, 'NOT operator'),
        ('$HAS_SWORD is 1 and $HAS_SHIELD is 0', True, 'Complex AND'),
        ('$GOLD > 40 and $GOLD < 60', True, 'Range check'),
    ]

    for expr, expected, desc in tests:
        result = evaluator.evaluate_condition(expr)
        status = "✓" if result == expected else "✗"
        print(f"{status} {desc}: {expr} => {result}")
        assert result == expected, f"Failed: {expr}"

    print("\n✓ PASS: Expression evaluation works\n")
    return True

def validate_passage_structure():
    """Validate passage structure and tags."""
    print("=" * 70)
    print("TEST 5: PASSAGE STRUCTURE")
    print("=" * 70)

    parser = TweeParser()
    with open('test_story.twee', 'r') as f:
        content = f.read()

    result = parser.parse_twee(content)
    passages = result.passages

    # Check Start passage has $start tag
    start = passages.get('Start')
    assert start is not None, "Start passage not found"
    assert '$start' in start.tags, "Start passage missing $start tag"
    print("✓ Start passage has $start tag")

    # Check all expected passages exist
    expected_passages = [
        'StoryTitle', 'StoryInit', 'TestSetup', 'Start',
        'TEST_SIMPLE_CONDITIONALS', 'TEST_NESTED_CONDITIONALS',
        'TEST_COMPARISON_OPS', 'TEST_LOGICAL_OPS', 'TEST_VARIABLE_OPS',
        'TEST_COMPLEX_SCENARIOS', 'TEST_PRINT_DISPLAY',
        'BUY_SWORD', 'QUEST_START', 'QUEST_CONTINUE', 'QUEST_CHALLENGE'
    ]

    for passage_name in expected_passages:
        assert passage_name in passages, f"Missing passage: {passage_name}"
        print(f"✓ Found passage: {passage_name}")

    print("\n✓ PASS: Passage structure correct\n")
    return True

def validate_nested_conditionals():
    """Validate nested conditional extraction from TestSetup."""
    print("=" * 70)
    print("TEST 6: NESTED CONDITIONAL EXTRACTION")
    print("=" * 70)

    # Test that nested conditionals in TestSetup are properly evaluated
    with open('test_story.twee', 'r') as f:
        content = f.read()

    # Scenario 0 should execute the first if branch
    parser = TweeParser()
    result = parser.parse_twee(content)

    # Variables inside the first if should be set
    assert result.test_setup_vars.get('PLAYER_NAME') == 'Tester'
    assert result.test_setup_vars.get('QUEST_STAGE') == 0

    # Variables from other branches should NOT be set
    assert result.test_setup_vars.get('PLAYER_NAME') != 'Warrior'
    assert result.test_setup_vars.get('PLAYER_NAME') != 'Wizard'

    print("✓ First branch executed correctly")
    print("✓ Other branches correctly skipped")

    print("\n✓ PASS: Nested conditional extraction works\n")
    return True

def main():
    """Run all validation tests."""
    print("\n" + "=" * 70)
    print("TW1X PARSER VALIDATION SUITE")
    print("=" * 70 + "\n")

    tests = [
        ("Basic Parsing", validate_parsing),
        ("StoryInit Variables", validate_storyinit),
        ("TestSetup Scenarios", validate_testsetup_scenarios),
        ("Expression Evaluator", validate_expression_evaluator),
        ("Passage Structure", validate_passage_structure),
        ("Nested Conditionals", validate_nested_conditionals),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n✗ FAIL: {test_name}")
            print(f"  Error: {e}\n")
            failed += 1
        except Exception as e:
            print(f"\n✗ ERROR: {test_name}")
            print(f"  Exception: {e}\n")
            failed += 1

    print("=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed == 0:
        print("\n🎉 ALL VALIDATION TESTS PASSED!")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
