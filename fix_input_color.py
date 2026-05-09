import os
import re

directories = ["c:\\Users\\lokes\\OneDrive\\Desktop\\Phytomine - Copy\\templates\\admins"]
files_to_update = ["cul_approve.html", "acc_approve.html", "ext_approve.html", "sus_approve.html"]

for directory in directories:
    for file in files_to_update:
        filepath = os.path.join(directory, file)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content.replace(
                'style="border: 2px solid #ddd; border-radius: 8px; padding: 10px;"',
                'style="border: 2px solid #ddd; border-radius: 8px; padding: 10px; color: #000 !important;"'
            )
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {file}")

print("Done.")
