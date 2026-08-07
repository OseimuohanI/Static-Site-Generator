import os
import shutil


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
STATIC_DIR = os.path.join(PROJECT_ROOT, "static")
PUBLIC_DIR = os.path.join(PROJECT_ROOT, "public")


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


def main():
    copy_directory(STATIC_DIR, PUBLIC_DIR)


main()
