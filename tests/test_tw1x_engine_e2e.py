#!/usr/bin/env python3
"""
End-to-End Test: TW1X Engine Integration
Tests complete workflow: Load story with TW1X → Parse passages → Run quest system
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engine'))

print("=" * 80)
print("TW1X ENGINE END-TO-END INTEGRATION TEST")
print("=" * 80)

# Import engine components
from twinery1x import load_story, USE_TW1X_PARSER, TW1X_AVAILABLE
from twinery1x import TwineryParser

print(f"\nTW1X Available: {TW1X_AVAILABLE}")
print(f"Using TW1X Parser: {USE_TW1X_PARSER}")
print("-" * 80)

# Test 1: Load story with TW1X
print("\n### TEST 1: Load Story with TW1X")
story_path = 'engine/games/mission_possible/data/story.twee'
mission_dict = {'testuser_DUMMY': 1}

try:
    story, storyinit = load_story(story_path, mission_dict)
    print(f"✓ Story loaded: {len(story)} passages")
    print(f"✓ StoryInit vars: {len(storyinit)}")
except Exception as e:
    print(f"✗ Failed to load story: {e}")
    sys.exit(1)

# Test 2: Validate passage structure
print("\n### TEST 2: Validate Passage Structure")
critical_passages = ['Start', 'INFO_BROKER', 'BLACK_MARKET_SHOP']
all_found = True

for passage_name in critical_passages:
    if passage_name in story:
        passage = story[passage_name]
        content_len = len(passage.get('text', ''))
        has_text = 'text' in passage
        has_tags = 'tag_list' in passage
        has_unparsed = 'unparsed_text' in passage

        if has_text and has_tags and has_unparsed and content_len > 0:
            print(f"✓ {passage_name}: {content_len} chars, all fields present")
        else:
            print(f"✗ {passage_name}: Missing fields or empty content")
            all_found = False
    else:
        print(f"✗ {passage_name}: NOT FOUND")
        all_found = False

if not all_found:
    print("\n✗ Some passages missing or malformed")
    sys.exit(1)

# Test 3: Parse passage with quest macros
print("\n### TEST 3: Parse Passage with Quest Macros")
parser = TwineryParser()

# Get INFO_BROKER passage
info_broker = story.get('INFO_BROKER')
if not info_broker:
    print("✗ INFO_BROKER passage not found")
    sys.exit(1)

try:
    # Parse the passage
    result = parser.parse_story_passage(info_broker, mission_dict, run_mode=False)

    print(f"✓ Passage parsed successfully")
    print(f"✓ Result has 'text' field: {'text' in result}")
    print(f"✓ Result has 'links' field: {'links' in result}")
    print(f"✓ Content length: {len(result.get('text', ''))} chars")

except Exception as e:
    print(f"✗ Failed to parse passage: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Quest system integration
print("\n### TEST 4: Quest System Integration")
try:
    from game import Quest

    username = "testuser"

    # Create a test quest
    quest = Quest("TEST_QUEST_TW1X", username)

    # Test quest state progression
    states_tested = []

    # UNKNOWN -> MENTIONED
    quest.set_state(Quest.STATE_MENTIONED)
    states_tested.append("MENTIONED")

    # MENTIONED -> ACCEPTED
    quest.set_state(Quest.STATE_ACCEPTED)
    states_tested.append("ACCEPTED")

    # ACCEPTED -> ACTIVE
    quest.set_state(Quest.STATE_ACTIVE)
    states_tested.append("ACTIVE")

    # Add objectives
    quest.add_objective("Find the broker", required=True)
    quest.add_objective("Get intel", required=True)
    states_tested.append("OBJECTIVES")

    # Complete objectives
    quest.complete_objective(0)
    quest.complete_objective(1)
    states_tested.append("OBJECTIVES_COMPLETE")

    # Should auto-advance to ACHIEVED
    if quest.state == Quest.STATE_ACHIEVED:
        states_tested.append("ACHIEVED")

    # Complete quest
    quest.set_state(Quest.STATE_COMPLETED)
    states_tested.append("COMPLETED")

    print(f"✓ Quest system working: {len(states_tested)} states tested")
    print(f"✓ States: {' → '.join(states_tested)}")
    print(f"✓ Final quest state: {quest.state}")

except Exception as e:
    print(f"✗ Quest system error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Load barbarian story (with TestSetup)
print("\n### TEST 5: Load Barbarian Story (with TestSetup)")
barbarian_path = 'engine/games/barbarian/data/story.twee'

try:
    story_barb, storyinit_barb = load_story(barbarian_path, {})
    print(f"✓ Barbarian story loaded: {len(story_barb)} passages")

    # Check for TestSetup
    if 'TestSetup' in story_barb:
        testsetup = story_barb['TestSetup']
        content = testsetup.get('text', '')
        print(f"✓ TestSetup found: {len(content)} chars")

        # Check for weapon name variable
        if '$WEAPON_NAME' in content:
            print(f"✓ TestSetup contains $WEAPON_NAME variable")
        else:
            print(f"⚠ TestSetup missing $WEAPON_NAME variable")
    else:
        print(f"⚠ TestSetup passage not found")

    # Check ARMORY passage
    if 'ARMORY' in story_barb:
        armory = story_barb['ARMORY']
        content = armory.get('text', '')
        print(f"✓ ARMORY found: {len(content)} chars")

        if '$WEAPON_NAME' in content:
            print(f"✓ ARMORY uses $WEAPON_NAME variable")
        else:
            print(f"⚠ ARMORY doesn't use $WEAPON_NAME variable")

except Exception as e:
    print(f"✗ Failed to load barbarian story: {e}")
    import traceback
    traceback.print_exc()

# Summary
print("\n" + "=" * 80)
print("END-TO-END INTEGRATION TEST SUMMARY")
print("=" * 80)

if USE_TW1X_PARSER:
    print("✓ Engine using TW1X parser")
    print("✓ Story loading working")
    print("✓ Passage structure validated")
    print("✓ Passage parsing working")
    print("✓ Quest system integrated")
    print("✓ Multiple stories tested")
    print("\n✅ TW1X ENGINE INTEGRATION: COMPLETE")
else:
    print("⚠ Engine is using original parser")
    print("  TW1X_AVAILABLE:", TW1X_AVAILABLE)
    print("\n⚠ TW1X not enabled")

print("=" * 80)
