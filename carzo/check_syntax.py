import re
import os
import sys

def check_html_syntax():
    file_path = r'c:\Users\praty\OneDrive\Desktop\carzo\carzo\admin.html'
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    html_content = open(file_path, encoding='utf-8').read()
    
    # 1. Check style tag block brace matching
    style_blocks = re.findall(r'<style>(.*?)</style>', html_content, re.DOTALL)
    print(f"Found {len(style_blocks)} style blocks.")
    
    # 2. Check script tag blocks
    script_blocks = re.findall(r'<script>(.*?)</script>', html_content, re.DOTALL)
    print(f"Found {len(script_blocks)} script blocks.")
    
    # We will write the scripts out to temp files and run node --check
    import subprocess
    for i, script in enumerate(script_blocks):
        temp_file = f"temp_script_{i}.js"
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(script)
        
        # Check syntax using Node
        res = subprocess.run(['node', '--check', temp_file], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"JS Syntax Error in block {i}:")
            print(res.stderr)
        else:
            print(f"JS block {i} is syntax-valid.")
            
        if os.path.exists(temp_file):
            os.remove(temp_file)

if __name__ == '__main__':
    check_html_syntax()
