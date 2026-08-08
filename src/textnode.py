from enum import Enum
import re

from leafnode import LeafNode
from parentnode import ParentNode


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"


class TextNode:
    def __init__(self, text, text_type, url=None) -> None:
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other) -> bool:
        if not isinstance(other, TextNode):
            return False
        return (
            self.text == other.text
            and self.text_type == other.text_type
            and self.url == other.url
        )

    def __repr__(self) -> str:
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if text_node.text_type == TextType.TEXT:
        return LeafNode(None, text_node.text)
    if text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)
    if text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)
    if text_node.text_type == TextType.LINK:
        return LeafNode("a", text_node.text, {"href": text_node.url})
    if text_node.text_type == TextType.IMAGE:
        return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})

    raise Exception(f"Unsupported text type: {text_node.text_type}")


def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        parts = old_node.text.split(delimiter)
        if len(parts) == 1:
            new_nodes.append(old_node)
            continue

        if len(parts) % 2 == 0:
            raise Exception(
                f"Invalid markdown syntax: missing closing delimiter {delimiter!r} in {old_node.text!r}"
            )

        for index, part in enumerate(parts):
            if part == "":
                continue
            if index % 2 == 0:
                new_nodes.append(TextNode(part, TextType.TEXT))
            else:
                new_nodes.append(TextNode(part, text_type))

    return new_nodes


def extract_markdown_images(text):
    return re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def extract_markdown_links(text):
    return re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        matches = extract_markdown_images(old_node.text)
        if not matches:
            new_nodes.append(old_node)
            continue

        remaining_text = old_node.text
        for alt_text, url in matches:
            markdown_image = f"![{alt_text}]({url})"
            before, after = remaining_text.split(markdown_image, 1)
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(alt_text, TextType.IMAGE, url))
            remaining_text = after

        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))

    return new_nodes


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    new_nodes = []

    for old_node in old_nodes:
        if old_node.text_type != TextType.TEXT:
            new_nodes.append(old_node)
            continue

        matches = extract_markdown_links(old_node.text)
        if not matches:
            new_nodes.append(old_node)
            continue

        remaining_text = old_node.text
        for anchor_text, url in matches:
            markdown_link = f"[{anchor_text}]({url})"
            before, after = remaining_text.split(markdown_link, 1)
            if before:
                new_nodes.append(TextNode(before, TextType.TEXT))
            new_nodes.append(TextNode(anchor_text, TextType.LINK, url))
            remaining_text = after

        if remaining_text:
            new_nodes.append(TextNode(remaining_text, TextType.TEXT))

    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes


def markdown_to_blocks(markdown):
    blocks = []
    for block in markdown.split("\n\n"):
        block = block.strip()
        if block:
            blocks.append(block)
    return blocks


def block_to_block_type(block):
    if re.match(r"^#{1,6} ", block):
        return BlockType.HEADING

    if block.startswith("```\n") and block.endswith("```"):
        return BlockType.CODE

    lines = block.splitlines()
    if len(lines) > 0 and all(line.startswith(">") for line in lines):
        return BlockType.QUOTE

    if len(lines) > 0 and all(line.startswith("- ") for line in lines):
        return BlockType.UNORDERED_LIST

    if len(lines) > 0:
        ordered_list = True
        for index, line in enumerate(lines, start=1):
            if not line.startswith(f"{index}. "):
                ordered_list = False
                break
        if ordered_list:
            return BlockType.ORDERED_LIST

    return BlockType.PARAGRAPH


def text_to_children(text):
    return [text_node_to_html_node(text_node) for text_node in text_to_textnodes(text)]


def block_to_html_node(block):
    block_type = block_to_block_type(block)

    if block_type == BlockType.PARAGRAPH:
        return ParentNode("p", text_to_children(block.replace("\n", " ")))

    if block_type == BlockType.HEADING:
        heading_match = re.match(r"^(#{1,6}) (.*)$", block)
        heading_level = len(heading_match.group(1))
        heading_text = heading_match.group(2)
        return ParentNode(f"h{heading_level}", text_to_children(heading_text))

    if block_type == BlockType.CODE:
        code_text = block[4:-3]
        return ParentNode("pre", [LeafNode("code", code_text)])

    if block_type == BlockType.QUOTE:
        quote_text = " ".join(
            re.sub(r"^>\s?", "", line) for line in block.splitlines()
        )
        return ParentNode("blockquote", text_to_children(quote_text))

    if block_type == BlockType.UNORDERED_LIST:
        list_items = [
            ParentNode("li", text_to_children(line[2:]))
            for line in block.splitlines()
        ]
        return ParentNode("ul", list_items)

    if block_type == BlockType.ORDERED_LIST:
        list_items = [
            ParentNode("li", text_to_children(re.sub(r"^\d+\. ", "", line, count=1)))
            for line in block.splitlines()
        ]
        return ParentNode("ol", list_items)

    raise Exception(f"Unsupported block type: {block_type}")


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = [block_to_html_node(block) for block in blocks]
    return ParentNode("div", children)
