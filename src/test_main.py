import os
import tempfile
import unittest

from main import extract_title, generate_page, generate_pages_recursive


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

    def test_generate_page_applies_basepath(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            from_path = os.path.join(temp_dir, "index.md")
            template_path = os.path.join(temp_dir, "template.html")
            dest_path = os.path.join(temp_dir, "output", "index.html")

            with open(from_path, "w", encoding="utf-8") as file:
                file.write(
                    "# Hello\n\n![Alt text](/images/test.png)\n\n[Link](/blog/test)"
                )

            with open(template_path, "w", encoding="utf-8") as file:
                file.write(
                    "<html><head><title>{{ Title }}</title></head>"
                    "<body>{{ Content }}</body></html>"
                )

            generate_page(from_path, template_path, dest_path, "/repo/")

            with open(dest_path, "r", encoding="utf-8") as file:
                html = file.read()

            self.assertIn('src="/repo/images/test.png"', html)
            self.assertIn('href="/repo/blog/test"', html)
            self.assertIn("<title>Hello</title>", html)

    def test_generate_pages_recursive(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            content_dir = os.path.join(temp_dir, "content")
            blog_dir = os.path.join(content_dir, "blog", "post")
            dest_dir = os.path.join(temp_dir, "docs")
            template_path = os.path.join(temp_dir, "template.html")

            os.makedirs(blog_dir, exist_ok=True)

            with open(os.path.join(content_dir, "index.md"), "w", encoding="utf-8") as file:
                file.write("# Home\n\nHome page")

            with open(os.path.join(blog_dir, "index.md"), "w", encoding="utf-8") as file:
                file.write("# Post\n\nPost body")

            with open(template_path, "w", encoding="utf-8") as file:
                file.write("<html><title>{{ Title }}</title><body>{{ Content }}</body></html>")

            generate_pages_recursive(content_dir, template_path, dest_dir, "/")

            self.assertTrue(os.path.exists(os.path.join(dest_dir, "index.html")))
            self.assertTrue(
                os.path.exists(os.path.join(dest_dir, "blog", "post", "index.html"))
            )


if __name__ == "__main__":
    unittest.main()
