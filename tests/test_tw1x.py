#!/usr/bin/env python3
"""
Unit tests for TW1X (TWEE 1 eXtended) parser.

Run with: python3 -m pytest test_tw1x.py -v
Or: python3 test_tw1x.py
"""

import unittest
from tw1x import (
    TweeParser, parse_twee, Passage, Link, ParseResult,
    VariableScope, ExecutionMode
)


class TestCoreParser(unittest.TestCase):
    """Test core passage parsing functionality."""

    def setUp(self):
        """Create parser instance for tests."""
        self.parser = TweeParser()

    def test_simple_passage(self):
        """Test parsing a simple passage."""
        content = """
:: Start
This is the start passage.
"""
        result = self.parser.parse_twee(content)

        self.assertEqual(len(result.passages), 1)
        self.assertIn('Start', result.passages)
        self.assertEqual(result.passages['Start'].name, 'Start')
        self.assertEqual(result.passages['Start'].content, 'This is the start passage.')
        self.assertEqual(result.passages['Start'].tags, [])

    def test_passage_with_tags(self):
        """Test parsing passage with tags."""
        content = """
:: Start [tag1, tag2, tag3]
Content here.
"""
        result = self.parser.parse_twee(content)

        passage = result.passages['Start']
        self.assertEqual(passage.tags, ['tag1', 'tag2', 'tag3'])

    def test_passage_with_single_tag(self):
        """Test parsing passage with single tag."""
        content = """
:: TestSetup [$metadata]
Some content.
"""
        result = self.parser.parse_twee(content)

        passage = result.passages['TestSetup']
        self.assertEqual(passage.tags, ['$metadata'])

    def test_multiple_passages(self):
        """Test parsing multiple passages."""
        content = """
:: First
First passage.

:: Second
Second passage.

:: Third [tag]
Third passage.
"""
        result = self.parser.parse_twee(content)

        self.assertEqual(len(result.passages), 3)
        self.assertIn('First', result.passages)
        self.assertIn('Second', result.passages)
        self.assertIn('Third', result.passages)

    def test_passage_with_whitespace(self):
        """Test passage names with extra whitespace."""
        content = """
::   Start
Content.
"""
        result = self.parser.parse_twee(content)

        self.assertIn('Start', result.passages)
        self.assertEqual(result.passages['Start'].name, 'Start')

    def test_multiline_content(self):
        """Test passage with multiline content."""
        content = """
:: Story
Line one.
Line two.
Line three.
"""
        result = self.parser.parse_twee(content)

        passage = result.passages['Story']
        self.assertIn('Line one', passage.content)
        self.assertIn('Line two', passage.content)
        self.assertIn('Line three', passage.content)


class TestLinkExtraction(unittest.TestCase):
    """Test link parsing from passages."""

    def setUp(self):
        """Create parser instance for tests."""
        self.parser = TweeParser()

    def test_simple_link(self):
        """Test [[Target]] syntax."""
        content = """
:: Start
Go to [[Next]]
"""
        result = self.parser.parse_twee(content)
        passage = result.passages['Start']
        links = self.parser.extract_links(passage)

        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].target, 'Next')
        self.assertEqual(links[0].display, 'Next')

    def test_link_with_display(self):
        """Test [[Display|Target]] syntax."""
        content = """
:: Start
[[Go to next passage|Next]]
"""
        result = self.parser.parse_twee(content)
        passage = result.passages['Start']
        links = self.parser.extract_links(passage)

        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].display, 'Go to next passage')
        self.assertEqual(links[0].target, 'Next')

    def test_multiple_links(self):
        """Test multiple links in one passage."""
        content = """
:: Start
Choose: [[Option A]] or [[Option B|OptionB]] or [[Option C]]
"""
        result = self.parser.parse_twee(content)
        passage = result.passages['Start']
        links = self.parser.extract_links(passage)

        self.assertEqual(len(links), 3)
        self.assertEqual(links[0].target, 'Option A')
        self.assertEqual(links[1].target, 'OptionB')
        self.assertEqual(links[2].target, 'Option C')

    def test_links_with_underscores(self):
        """Test links with underscores in target."""
        content = """
:: Start
Go [[ACCEPT_QUEST]] or [[ASK_INFO]]
"""
        result = self.parser.parse_twee(content)
        passage = result.passages['Start']
        links = self.parser.extract_links(passage)

        self.assertEqual(len(links), 2)
        self.assertEqual(links[0].target, 'ACCEPT_QUEST')
        self.assertEqual(links[1].target, 'ASK_INFO')


class TestImageExtraction(unittest.TestCase):
    """Test image URL extraction."""

    def setUp(self):
        """Create parser instance for tests."""
        self.parser = TweeParser()

    def test_image_url(self):
        """Test [img[url]] syntax."""
        content = """
:: Gallery
[img[https://example.com/image.png]]
Some text.
"""
        result = self.parser.parse_twee(content)
        passage = result.passages['Gallery']

        self.assertEqual(passage.image_url, 'https://example.com/image.png')

    def test_no_image(self):
        """Test passage without image."""
        content = """
:: NoImage
Just text here.
"""
        result = self.parser.parse_twee(content)
        passage = result.passages['NoImage']

        self.assertIsNone(passage.image_url)


class TestSpecialPassages(unittest.TestCase):
    """Test special passage handling."""

    def setUp(self):
        """Create parser instance for tests."""
        self.parser = TweeParser()

    def test_story_title(self):
        """Test StoryTitle passage."""
        content = """
:: StoryTitle
My Epic Adventure

:: Start
Game starts here.
"""
        result = self.parser.parse_twee(content)

        self.assertIn('StoryTitle', result.passages)
        self.assertEqual(result.passages['StoryTitle'].content, 'My Epic Adventure')

    def test_story_init_exists(self):
        """Test StoryInit passage is parsed."""
        content = """
:: StoryInit
<<set $HEALTH to 100>>
<<set $GOLD to 0>>

:: Start
Game content.
"""
        result = self.parser.parse_twee(content)

        self.assertIn('StoryInit', result.passages)
        # Phase 1: We don't parse variables yet, just verify passage exists
        self.assertIsNotNone(result.passages['StoryInit'])

    def test_test_setup_exists(self):
        """Test TestSetup passage is parsed."""
        content = """
:: TestSetup [$metadata]
<<set $SCENARIO to 1>>

:: Start
Game content.
"""
        result = self.parser.parse_twee(content)

        self.assertIn('TestSetup', result.passages)
        self.assertEqual(result.passages['TestSetup'].tags, ['$metadata'])


class TestPublicAPI(unittest.TestCase):
    """Test public API functions."""

    def test_parse_twee_function(self):
        """Test parse_twee() convenience function."""
        content = """
:: Start
Hello world!
"""
        result = parse_twee(content)

        self.assertIsInstance(result, ParseResult)
        self.assertEqual(len(result.passages), 1)
        self.assertIn('Start', result.passages)

    def test_parse_twee_with_scope(self):
        """Test parse_twee() with scope mode."""
        content = """
:: Start
Test content.
"""
        result = parse_twee(content, scope_mode=VariableScope.USERNAME_PREFIXED)

        self.assertIsInstance(result, ParseResult)
        self.assertEqual(len(result.passages), 1)


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""

    def test_empty_content(self):
        """Test parsing empty content."""
        content = ""
        result = parse_twee(content)

        self.assertEqual(len(result.passages), 0)
        self.assertEqual(len(result.errors), 0)

    def test_no_passages(self):
        """Test content without passage markers."""
        content = "Just some random text\nwith no passages."
        result = parse_twee(content)

        self.assertEqual(len(result.passages), 0)


class TestBarbarianStory(unittest.TestCase):
    """Integration test with real story file."""

    def test_barbarian_story_structure(self):
        """Test parsing the actual barbarian story."""
        import os

        story_path = 'engine/games/barbarian/data/story.twee'
        if not os.path.exists(story_path):
            self.skipTest("Barbarian story file not found")

        with open(story_path, 'r') as f:
            content = f.read()

        result = parse_twee(content)

        # Verify expected passages exist
        self.assertIn('StoryTitle', result.passages)
        self.assertIn('StoryInit', result.passages)
        self.assertIn('TestSetup', result.passages)
        self.assertIn('Start', result.passages)
        self.assertIn('LONGHOUSE', result.passages)
        self.assertIn('DEFEAT', result.passages)

        # Verify passage count (27 passages in barbarian story)
        self.assertGreaterEqual(len(result.passages), 25)

        # Verify tags
        self.assertIn('$start', result.passages['Start'].tags)
        self.assertIn('$metadata', result.passages['TestSetup'].tags)

        # Verify no parsing errors
        self.assertEqual(len(result.errors), 0)


class TestDataStructures(unittest.TestCase):
    """Test data structure representations."""

    def test_passage_repr(self):
        """Test Passage __repr__."""
        passage = Passage(
            name='Test',
            tags=['tag1', 'tag2'],
            content='Content',
            raw_content='Content'
        )
        repr_str = repr(passage)
        self.assertIn('Test', repr_str)
        self.assertIn('tag1', repr_str)

    def test_link_repr(self):
        """Test Link __repr__."""
        link = Link(display='Click here', target='Next')
        repr_str = repr(link)
        self.assertIn('Click here', repr_str)
        self.assertIn('Next', repr_str)

    def test_parse_result_repr(self):
        """Test ParseResult __repr__."""
        result = ParseResult(
            passages={'Start': Passage('Start', [], 'content', 'content')},
            story_init_vars={},
            test_setup_vars={},
            errors=[]
        )
        repr_str = repr(result)
        self.assertIn('1 passages', repr_str)


# ============================================================================
# Main - Run tests
# ============================================================================

if __name__ == '__main__':
    print("TW1X Parser Tests")
    print("=" * 60)
    unittest.main(verbosity=2)
