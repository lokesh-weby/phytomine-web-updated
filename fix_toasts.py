import os
import re

directory = r"c:\Users\lokes\OneDrive\Desktop\Phytomine - Copy\templates"

# Pattern to find Toastify({ text: '...' })
# Handles single or double quotes and spaces around curly braces
pattern = re.compile(r"text\s*:\s*['\"]\{\{\s*message\s*\}\}['\"]", re.MULTILINE)
replacement = 'text: "{{ message|escapejs }}"'

count = 0
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith(".html"):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = pattern.sub(replacement, content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filepath}")
                count += 1

print(f"Total files updated: {count}")
