#!/usr/bin/env python3
"""
TW1X Basic Usage Example

Demonstrates core functionality of the TW1X parser.
"""

from tw1x import parse_twee, TweeParser, ExecutionMode

# Sample Twee content
SAMPLE_STORY = """
:: StoryTitle
My Adventure

:: StoryInit
<<set $HEALTH to 100>>
<<set $GOLD to 50>>
<<set $NAME to "Hero">>

:: Start [$start]
You wake up in a mysterious forest.

Your stats:
- Health: <<print $HEALTH>>
- Gold: <<print $GOLD>>

[[Explore the forest|forest]]
[[Rest by the campfire|rest]]

:: forest
You venture deeper into the forest.

<<set $GOLD += 10>>

You found 10 gold coins!

Current gold: <<print $GOLD>>

[[Continue|cave_entrance]]

:: rest
You rest by the warm fire.

<<set $HEALTH to 100>>

Your health is restored!

[[Get up|Start]]

:: cave_entrance
You discover a dark cave.

<<if $GOLD > 50>>
You have enough gold to buy supplies.
[[Enter the cave|cave_interior]]
<<else>>
You need more gold before entering.
[[Go back|forest]]
<<endif>>

:: cave_interior
Deep inside the cave, you find treasure!

<<set $GOLD += 100>>

You now have <<print $GOLD>> gold!

THE END
"""


def example_parse():
    """Example: Parse a Twee story."""
    print("=" * 70)
    print("EXAMPLE 1: PARSING")
    print("=" * 70)

    result = parse_twee(SAMPLE_STORY)

    print(f"\n✅ Parsed {len(result.passages)} passages")
    print(f"\nPassages:")
    for name in result.passages.keys():
        print(f"  - {name}")

    print(f"\nStoryInit Variables: {result.story_init_vars}")

    if result.errors:
        print(f"\n⚠️  Errors: {result.errors}")
    else:
        print("\n✅ No parse errors")


def example_render():
    """Example: Render a passage with variables."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: RENDERING")
    print("=" * 70)

    # Parse story
    result = parse_twee(SAMPLE_STORY)

    # Initialize variables from StoryInit
    variables = result.story_init_vars.copy()

    # Get Start passage
    start_passage = result.passages['Start']

    # Render it
    parser = TweeParser()
    render_result = parser.render_passage(
        start_passage,
        variables,
        mode=ExecutionMode.PREVIEW,
        passages=result.passages
    )

    print(f"\nRendered Text:")
    print("-" * 70)
    print(render_result.text)
    print("-" * 70)

    print(f"\nLinks:")
    for link in render_result.links:
        print(f"  - [{link.display}] → {link.target}")


def example_gameplay_simulation():
    """Example: Simulate gameplay with variable updates."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: GAMEPLAY SIMULATION")
    print("=" * 70)

    # Parse story
    result = parse_twee(SAMPLE_STORY)
    parser = TweeParser()

    # Initialize game state
    game_state = result.story_init_vars.copy()
    current_passage_name = 'Start'

    print(f"\nStarting game with state: {game_state}\n")

    # Simulate player path: Start → forest → cave_entrance
    path = ['Start', 'forest', 'cave_entrance']

    for passage_name in path:
        print(f"\n{'='*70}")
        print(f"PASSAGE: {passage_name}")
        print('='*70)

        passage = result.passages[passage_name]
        render_result = parser.render_passage(
            passage,
            game_state,
            mode=ExecutionMode.RUNTIME,
            passages=result.passages
        )

        print(render_result.text)

        print(f"\nUpdated game state: {game_state}")

        if render_result.links:
            print(f"\nAvailable choices:")
            for link in render_result.links:
                print(f"  - {link.display}")


def example_conditionals():
    """Example: Demonstrate conditional processing."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: CONDITIONAL PROCESSING")
    print("=" * 70)

    # Parse story
    result = parse_twee(SAMPLE_STORY)
    parser = TweeParser()

    # Test with LOW gold (should see "need more gold" message)
    print("\n--- Test 1: Low Gold (40) ---")
    game_state = {'HEALTH': 100, 'GOLD': 40, 'NAME': 'Hero'}

    passage = result.passages['cave_entrance']
    render_result = parser.render_passage(
        passage,
        game_state,
        mode=ExecutionMode.PREVIEW,
        passages=result.passages
    )

    print(render_result.text)

    # Test with HIGH gold (should see "enter the cave" option)
    print("\n--- Test 2: High Gold (60) ---")
    game_state = {'HEALTH': 100, 'GOLD': 60, 'NAME': 'Hero'}

    render_result = parser.render_passage(
        passage,
        game_state,
        mode=ExecutionMode.PREVIEW,
        passages=result.passages
    )

    print(render_result.text)


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("TW1X BASIC USAGE EXAMPLES")
    print("=" * 70)

    example_parse()
    example_render()
    example_gameplay_simulation()
    example_conditionals()

    print("\n" + "=" * 70)
    print("EXAMPLES COMPLETE")
    print("=" * 70)
    print("\nFor more examples, see:")
    print("  - tests/validate_tw1x.py")
    print("  - tests/test_tw1x.py")
    print("\nDocumentation:")
    print("  - docs/API.md")
    print("  - docs/TW1X_UNIFIED_PARSER_PROPOSAL.md")


if __name__ == '__main__':
    main()
