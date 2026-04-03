import os
import re

# Target only SUS module
templates_dir = r"C:\Users\lokes\OneDrive\Desktop\Phytomine - Copy\templates\acc"

# New clean light table CSS
new_css = """
.fixed-table-wrapper {
    max-width: 100%;
    margin: 25px auto;
    padding: 15px;
    background: #ffffff;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    overflow-x: auto;
}

.fixed-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    color: #333;
}

.fixed-table thead th {
    background: #f5f5f5;
    color: #333;
    padding: 12px;
    text-transform: uppercase;
    border-bottom: 2px solid #ddd;
    text-align: center;
}

.fixed-table tbody td {
    padding: 10px;
    border-bottom: 1px solid #eee;
    text-align: center;
    background: #ffffff;
}

.fixed-table tbody tr:nth-child(even) td {
    background: #fafafa;
}

.fixed-table tbody tr:hover {
    background: #f1f7ff;
}
"""

# Regex to detect your existing table CSS block
pattern = re.compile(r'\.fixed-table-wrapper\s*\{.*?\@keyframes glowFade\s*\{.*?\}\s*\}', re.DOTALL)

count = 0

for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith(".html"):
            file_path = os.path.join(root, file)

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Only modify files that contain your table styles
            if ".fixed-table-wrapper" in content and "glowFade" in content:

                # Backup (VERY IMPORTANT)
                backup_path = file_path + ".bak"
                with open(backup_path, "w", encoding="utf-8") as b:
                    b.write(content)

                # Replace old CSS with new CSS
                new_content = pattern.sub(new_css, content)

                if new_content != content:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(new_content)

                    print(f"Updated: {file_path}")
                    count += 1

print(f"\n✅ Total updated files: {count}")