import unittest

from leafnode import LeafNode
from textnode import TextNode, TextType
from textnode import extract_markdown_images
from textnode import extract_markdown_links
from textnode import split_nodes_delimiter
from textnode import split_nodes_image
from textnode import split_nodes_link
from textnode import text_node_to_html_node


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_equal_text(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a different text node", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_equal_text_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_equal_url(self):
        node = TextNode("This is a text node", TextType.LINK, "https://www.boot.dev")
        node2 = TextNode("This is a text node", TextType.LINK, "https://www.google.com")
        self.assertNotEqual(node, node2)

    def test_url_defaults_to_none(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.TEXT, None)
        self.assertEqual(node, node2)

    def test_text_node_to_html_node_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, None)
        self.assertEqual(html_node.value, "This is a text node")

    def test_text_node_to_html_node_bold(self):
        node = TextNode("Bold text", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node, LeafNode("b", "Bold text"))

    def test_text_node_to_html_node_italic(self):
        node = TextNode("Italic text", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node, LeafNode("i", "Italic text"))

    def test_text_node_to_html_node_code(self):
        node = TextNode("Code text", TextType.CODE)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node, LeafNode("code", "Code text"))

    def test_text_node_to_html_node_link(self):
        node = TextNode("Click me", TextType.LINK, "https://www.boot.dev")
        html_node = text_node_to_html_node(node)
        self.assertEqual(
            html_node,
            LeafNode("a", "Click me", {"href": "https://www.boot.dev"}),
        )

    def test_text_node_to_html_node_image(self):
        node = TextNode("alt text", TextType.IMAGE, "https://www.boot.dev/image.png")
        html_node = text_node_to_html_node(node)
        self.assertEqual(
            html_node,
            LeafNode(
                "img",
                "",
                {"src": "https://www.boot.dev/image.png", "alt": "alt text"},
            ),
        )

    def test_text_node_to_html_node_invalid_type(self):
        node = TextNode("Unsupported", "not-a-text-type")
        with self.assertRaises(Exception):
            text_node_to_html_node(node)

    def test_split_nodes_delimiter_code(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
        )

    def test_split_nodes_delimiter_bold(self):
        node = TextNode("This is **bolded** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("bolded", TextType.BOLD),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_split_nodes_delimiter_italic(self):
        node = TextNode("This is _italic_ text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)
        self.assertEqual(
            new_nodes,
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" text", TextType.TEXT),
            ],
        )

    def test_split_nodes_delimiter_preserves_non_text_nodes(self):
        old_nodes = [
            TextNode("This is ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(old_nodes, "**", TextType.BOLD)
        self.assertEqual(new_nodes, old_nodes)

    def test_split_nodes_delimiter_multiple_nodes(self):
        old_nodes = [
            TextNode("Hello `code` world", TextType.TEXT),
            TextNode(" and **bold** too", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(old_nodes, "`", TextType.CODE)
        new_nodes = split_nodes_delimiter(new_nodes, "**", TextType.BOLD)
        self.assertEqual(
            new_nodes,
            [
                TextNode("Hello ", TextType.TEXT),
                TextNode("code", TextType.CODE),
                TextNode(" world", TextType.TEXT),
                TextNode(" and ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
                TextNode(" too", TextType.TEXT),
            ],
        )

    def test_split_nodes_delimiter_missing_closing_raises(self):
        node = TextNode("This is **broken text", TextType.TEXT)
        with self.assertRaises(Exception):
            split_nodes_delimiter([node], "**", TextType.BOLD)

    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual(
            [("image", "https://i.imgur.com/zjjcJKZ.png")],
            matches,
        )

    def test_extract_markdown_images_multiple(self):
        matches = extract_markdown_images(
            "![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertListEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            matches,
        )

    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev)"
        )
        self.assertListEqual(
            [("to boot dev", "https://www.boot.dev")],
            matches,
        )

    def test_extract_markdown_links_multiple(self):
        matches = extract_markdown_links(
            "This has [one](https://one.example) and [two](https://two.example)"
        )
        self.assertListEqual(
            [
                ("one", "https://one.example"),
                ("two", "https://two.example"),
            ],
            matches,
        )

    def test_extract_markdown_links_ignores_images(self):
        matches = extract_markdown_links(
            "This has an ![image](https://example.com/image.png) and [link](https://example.com)"
        )
        self.assertListEqual(
            [("link", "https://example.com")],
            matches,
        )

    def test_split_images(self):
        node = TextNode(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png) and another ![second image](https://i.imgur.com/3elNhQu.png)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])
        self.assertListEqual(
            [
                TextNode("This is text with an ", TextType.TEXT),
                TextNode("image", TextType.IMAGE, "https://i.imgur.com/zjjcJKZ.png"),
                TextNode(" and another ", TextType.TEXT),
                TextNode("second image", TextType.IMAGE, "https://i.imgur.com/3elNhQu.png"),
            ],
            new_nodes,
        )

    def test_split_images_no_matches_returns_original(self):
        node = TextNode("This has no images", TextType.TEXT)
        self.assertListEqual([node], split_nodes_image([node]))

    def test_split_images_preserves_non_text_nodes(self):
        old_nodes = [
            TextNode("prefix ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" suffix", TextType.TEXT),
        ]
        self.assertListEqual(old_nodes, split_nodes_image(old_nodes))

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertListEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode("to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"),
            ],
            new_nodes,
        )

    def test_split_links_no_matches_returns_original(self):
        node = TextNode("This has no links", TextType.TEXT)
        self.assertListEqual([node], split_nodes_link([node]))

    def test_split_links_preserves_non_text_nodes(self):
        old_nodes = [
            TextNode("prefix ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" suffix", TextType.TEXT),
        ]
        self.assertListEqual(old_nodes, split_nodes_link(old_nodes))

    def test_split_links_trims_empty_text_segments(self):
        node = TextNode("[link](https://example.com)", TextType.TEXT)
        self.assertListEqual(
            [TextNode("link", TextType.LINK, "https://example.com")],
            split_nodes_link([node]),
        )


if __name__ == "__main__":
    unittest.main()
