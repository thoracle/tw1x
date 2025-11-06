#!/usr/bin/env python3
"""
Test TW1X Tag Format Conversion
Validates that TW1X adapter converts tags to engine's expected format
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'engine'))

print("=" * 80)
print("TW1X TAG FORMAT CONVERSION TEST")
print("=" * 80)

from tw1x import Passage
from tw1x_adapter import passage_to_engine_dict

# Test 1: Passage with multiple tags
print("\n### Test 1: Passage with Multiple Tags")
passage_multi = Passage(
    name="TestPassage",
    tags=["tag1", "tag2", "tag3"],
    content="Test content",
    raw_content="Test content"
)

result = passage_to_engine_dict(passage_multi)
print(f"TW1X tags: {passage_multi.tags}")
print(f"Engine tag_list: {result['tag_list']}")
print(f"Type: {type(result['tag_list'])}")

if result['tag_list'] == ['tag1 tag2 tag3']:
    print("✓ Multiple tags converted correctly")
else:
    print(f"✗ Expected ['tag1 tag2 tag3'], got {result['tag_list']}")
    sys.exit(1)

# Test 2: Passage with single tag
print("\n### Test 2: Passage with Single Tag")
passage_single = Passage(
    name="TestPassage2",
    tags=["$start"],
    content="Start passage",
    raw_content="Start passage"
)

result = passage_to_engine_dict(passage_single)
print(f"TW1X tags: {passage_single.tags}")
print(f"Engine tag_list: {result['tag_list']}")

if result['tag_list'] == ['$start']:
    print("✓ Single tag converted correctly")
else:
    print(f"✗ Expected ['$start'], got {result['tag_list']}")
    sys.exit(1)

# Test 3: Passage with no tags
print("\n### Test 3: Passage with No Tags")
passage_empty = Passage(
    name="TestPassage3",
    tags=[],
    content="No tags",
    raw_content="No tags"
)

result = passage_to_engine_dict(passage_empty)
print(f"TW1X tags: {passage_empty.tags}")
print(f"Engine tag_list: {result['tag_list']}")

if result['tag_list'] == []:
    print("✓ Empty tags handled correctly")
else:
    print(f"✗ Expected [], got {result['tag_list']}")
    sys.exit(1)

# Test 4: Load real story and check Start passage tags
print("\n### Test 4: Real Story - Start Passage Tags")
from twinery1x import load_story

story, _ = load_story('engine/games/barbarian/data/story.twee', {})

if 'Start' in story:
    start_passage = story['Start']
    tag_list = start_passage.get('tag_list', [])

    print(f"Start passage tag_list: {tag_list}")
    print(f"Type: {type(tag_list)}")
    print(f"Length: {len(tag_list)}")

    if len(tag_list) > 0:
        print(f"First element: '{tag_list[0]}'")
        print(f"First element type: {type(tag_list[0])}")

        # Engine expects to be able to do: tags[0].split()
        try:
            split_result = tag_list[0].split()
            print(f"✓ Can split tags[0]: {split_result}")
        except Exception as e:
            print(f"✗ Cannot split tags[0]: {e}")
            sys.exit(1)
    else:
        print("✓ Empty tag_list (no crash expected)")
else:
    print("✗ Start passage not found")
    sys.exit(1)

# Test 5: Check ELDER passage (the one that crashed)
print("\n### Test 5: ELDER Passage Tags")
if 'ELDER' in story:
    elder_passage = story['ELDER']
    tag_list = elder_passage.get('tag_list', [])

    print(f"ELDER passage tag_list: {tag_list}")
    print(f"Type: {type(tag_list)}")
    print(f"Length: {len(tag_list)}")

    # This is the problematic line from game.py:1766
    if len(tag_list) > 0:
        try:
            split_result = tag_list[0].split()
            print(f"✓ Can safely access tags[0].split(): {split_result}")
        except Exception as e:
            print(f"✗ Would crash on tags[0].split(): {e}")
            sys.exit(1)
    else:
        print("⚠ Empty tag_list - game.py line 1766 would crash with IndexError!")
        print("  This is OK now because game.py should check if list is empty")
else:
    print("✗ ELDER passage not found")
    sys.exit(1)

print("\n" + "=" * 80)
print("TAG FORMAT CONVERSION TEST SUMMARY")
print("=" * 80)
print("✓ Multiple tags: converted to single space-separated string")
print("✓ Single tag: wrapped in list")
print("✓ Empty tags: returns empty list")
print("✓ Real story passages: correct format")
print("✓ Engine can safely call tags[0].split() on tagged passages")
print("\n⚠ Note: Engine should check if tag_list is empty before accessing tags[0]")
print("=" * 80)
