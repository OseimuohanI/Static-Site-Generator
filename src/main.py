import os
import shutil
import sys

from textnode import markdown_to_html_node


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
CONTENT_DIR = os.path.join(PROJECT_ROOT, "content")
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "template.html")


def copy_directory(source_dir, destination_dir):
    if os.path.exists(destination_dir):
        shutil.rmtree(destination_dir)

    os.mkdir(destination_dir)

    for entry in os.listdir(source_dir):
        source_path = os.path.join(source_dir, entry)
        destination_path = os.path.join(destination_dir, entry)

        if os.path.isfile(source_path):
            shutil.copy(source_path, destination_path)
            print(f"Copied {source_path} to {destination_path}")
        else:
            copy_directory(source_path, destination_path)


def copy_directory_contents(source_dir, destination_dir):
    os.makedirs(destination_dir, exist_ok=True)

    for entry in os.listdir(source_dir):
        source_path = os.path.join(source_dir, entry)
        destination_path = os.path.join(destination_dir, entry)

        if os.path.isfile(source_path):
            shutil.copy2(source_path, destination_path)
        else:
            if os.path.exists(destination_path):
                shutil.rmtree(destination_path)
            copy_directory_contents(source_path, destination_path)


def extract_title(markdown):
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()

    raise Exception("No h1 header found in markdown")


def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r", encoding="utf-8") as file:
        markdown = file.read()

    with open(template_path, "r", encoding="utf-8") as file:
        template = file.read()

    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    page = template.replace("{{ Title }}", title).replace("{{ Content }}", html)
    page = page.replace('href="/', f'href="{basepath}')
    page = page.replace('src="/', f'src="{basepath}')

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as file:
        file.write(page)


def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    for entry in os.listdir(dir_path_content):
        source_path = os.path.join(dir_path_content, entry)
        destination_path = os.path.join(dest_dir_path, entry)

        if os.path.isdir(source_path):
            generate_pages_recursive(source_path, template_path, destination_path, basepath)
        elif source_path.endswith(".md"):
            html_destination = destination_path[:-3] + ".html"
            generate_page(source_path, template_path, html_destination, basepath)


def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    copy_directory(STATIC_DIR, DOCS_DIR)
    generate_pages_recursive(CONTENT_DIR, TEMPLATE_PATH, DOCS_DIR, basepath)


if __name__ == "__main__":
    main()
