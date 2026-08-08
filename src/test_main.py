import unittest

from main import extract_title


class TestMain(unittest.TestCase):
    def test_extract_title(self):
        self.assertEqual(extract_title("# Hello"), "Hello")

    def test_extract_title_strips_whitespace(self):
        self.assertEqual(extract_title("#   Hello World   "), "Hello World")

    def test_extract_title_ignores_non_h1_headings(self):
        markdown = """## Not the title

# Real Title
"""
        self.assertEqual(extract_title(markdown), "Real Title")

    def test_extract_title_raises_when_missing_h1(self):
        markdown = """## No title here

Paragraph text
"""
        with self.assertRaises(Exception):
            extract_title(markdown)


if __name__ == "__main__":
    unittest.main()
