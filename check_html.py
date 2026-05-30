import re
import os

def check_html_tags():
    html_path = r'c:\Users\praty\OneDrive\Desktop\carzo\carzo\admin.html'
    try:
        content = open(html_path, encoding='utf-8').read()
    except Exception as e:
        print(f"Error opening file: {e}")
        return

    # Strip out style and script blocks to only check HTML structure
    content_clean = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
    content_clean = re.sub(r'<script>.*?</script>', '', content_clean, flags=re.DOTALL)
    content_clean = re.sub(r'<!--.*?-->', '', content_clean, flags=re.DOTALL)

    # Find all tags
    tags = re.findall(r'</?([a-zA-Z0-9\-]+)(?:\s+[^>]*)?>', content_clean)
    
    # Self-closing tags in HTML5
    self_closing = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
        'param', 'source', 'track', 'wbr', 'polygon', 'polyline', 'line', 'circle',
        'rect', 'path'
    }
    
    stack = []
    errors = []
    
    # We will search with lines to find line numbers
    lines = content_clean.split('\n')
    for line_no, line in enumerate(lines):
        line_tags = re.finditer(r'</?([a-zA-Z0-9\-]+)(?:\s+[^>]*)?>', line)
        for match in line_tags:
            tag_text = match.group(0)
            tag_name = match.group(1).lower()
            
            if tag_name in self_closing:
                continue
                
            if tag_text.startswith('</'):
                # Closing tag
                if not stack:
                    errors.append(f"Extra closing tag '</{tag_name}>' at line {line_no + 1}")
                else:
                    top_tag, top_line = stack.pop()
                    if top_tag != tag_name:
                        errors.append(f"Mismatched closing tag '</{tag_name}>' at line {line_no + 1} (expected '</{top_tag}>' to match open tag on line {top_line})")
            else:
                # Opening tag
                stack.append((tag_name, line_no + 1))
                
    with open('html_errors.txt', 'w', encoding='utf-8') as f:
        f.write(f"Analyzing HTML tags structure...\n")
        if errors:
            f.write("Errors found:\n")
            for err in errors:
                f.write(err + "\n")
        else:
            f.write("No basic mismatched HTML tag errors found.\n")
            
        if stack:
            f.write("\nUnclosed tags left at the end:\n")
            for item in stack:
                f.write(f"  <{item[0]}> opened at line {item[1]}\n")
        else:
            f.write("\nAll open tags were closed correctly.\n")
            
    print("HTML check finished. Result written to html_errors.txt")

if __name__ == '__main__':
    check_html_tags()
