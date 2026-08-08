import os
import shutil

from textnode import markdown_to_html_node


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")
CONTENT_DIR = os.path.join(PROJECT_ROOT, "content")
TEMPLATE_PATH = os.path.join(PROJECT_ROOT, "template.html")
ROOT_INDEX_HTML_PATH = os.path.join(PROJECT_ROOT, "index.html")
ROOT_INDEX_CSS_PATH = os.path.join(PROJECT_ROOT, "index.css")
ROOT_IMAGES_DIR = os.path.join(PROJECT_ROOT, "images")
ROOT_BLOG_DIR = os.path.join(PROJECT_ROOT, "blog")
ROOT_CONTACT_DIR = os.path.join(PROJECT_ROOT, "contact")


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


def generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    with open(from_path, "r", encoding="utf-8") as file:
        markdown = file.read()

    with open(template_path, "r", encoding="utf-8") as file:
        template = file.read()

    html = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)

    page = template.replace("{{ Title }}", title).replace("{{ Content }}", html)

    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(dest_path, "w", encoding="utf-8") as file:
        file.write(page)


def mirror_public_site_to_root():
    copy_directory_contents(PUBLIC_DIR, PROJECT_ROOT)


def generate_pages_recursive(content_dir, template_path, destination_dir):
    for entry in os.listdir(content_dir):
        source_path = os.path.join(content_dir, entry)
        destination_path = os.path.join(destination_dir, entry)

        if os.path.isdir(source_path):
            generate_pages_recursive(source_path, template_path, destination_path)
        elif source_path.endswith(".md"):
            html_destination = destination_path[:-3] + ".html"
            generate_page(source_path, template_path, html_destination)


def main():
    copy_directory(STATIC_DIR, PUBLIC_DIR)
    generate_pages_recursive(CONTENT_DIR, TEMPLATE_PATH, PUBLIC_DIR)
    mirror_public_site_to_root()


if __name__ == "__main__":
    main()
