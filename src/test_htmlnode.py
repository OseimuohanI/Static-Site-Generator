import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    def test_props_to_html_multiple_props(self):
        node = HTMLNode(
            "a",
            "Click me",
            None,
            {
                "href": "https://www.google.com",
                "target": "_blank",
            },
        )
        self.assertEqual(
            node.props_to_html(),
            ' href="https://www.google.com" target="_blank"',
        )

    def test_props_to_html_empty(self):
        node = HTMLNode("p", "Hello, world")
        self.assertEqual(node.props_to_html(), "")

    def test_repr(self):
        node = HTMLNode("p", "Hello, world")
        self.assertEqual(
            repr(node),
            "HTMLNode(p, Hello, world, None, None)",
        )

    def test_to_html_not_implemented(self):
        node = HTMLNode("p", "Hello, world")
        with self.assertRaises(NotImplementedError):
            node.to_html()


if __name__ == "__main__":
    unittest.main()
