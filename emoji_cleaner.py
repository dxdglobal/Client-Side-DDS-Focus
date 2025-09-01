import os
import re

def remove_emojis_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove emojis and non-ASCII characters
    cleaned = re.sub(r'[^\x00-\x7F]+', '', content)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    print(f" Cleaned: {file_path}")

def clean_all_py_files(root_dir):
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                remove_emojis_from_file(os.path.join(root, file))

if __name__ == "__main__":
    base_dir = os.getcwd()  # or set to a specific folder path
    clean_all_py_files(base_dir)
    print("\n All Python files cleaned of emojis and problematic Unicode characters.")

