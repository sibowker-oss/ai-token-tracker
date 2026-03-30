#!/usr/bin/env python3
"""
Syncs markdown files from ~/Documents/Claude/Project Ideas/ into the
In Development page (in-development.html) as "Idea" cards.

Reads each .md file's title (first # heading) and opening paragraph,
then rebuilds the ideas section of in-development.html.

Existing prototype/spec/planned cards are preserved — only the
"Idea (from Project Ideas)" section is regenerated.

Run: python3 scripts/sync_ideas.py
Cron: daily (added to crontab)
"""

import json
import os
import re
import glob
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDEAS_DIR = os.path.expanduser('~/Documents/Claude/Project Ideas')
INDEV_PAGE = os.path.join(BASE_DIR, 'in-development.html')

# Marker comments in the HTML to delimit the auto-generated section
START_MARKER = '<!-- AUTO-IDEAS-START -->'
END_MARKER = '<!-- AUTO-IDEAS-END -->'


def extract_md_meta(filepath):
    """Extract title and first paragraph from a markdown file."""
    with open(filepath) as f:
        content = f.read()

    # Title: first # heading
    title_match = re.search(r'^#\s+(.+)', content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else os.path.basename(filepath).replace('.md', '').replace('-', ' ').title()

    # First paragraph after title (skip blank lines and ## headings)
    lines = content.split('\n')
    para = ''
    found_title = False
    for line in lines:
        if line.startswith('# '):
            found_title = True
            continue
        if found_title:
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('---') or stripped.startswith('**'):
                continue
            if stripped:
                para = stripped
                break

    # Truncate to ~150 chars
    if len(para) > 150:
        para = para[:147] + '...'

    return {
        'title': title,
        'description': para or 'Project idea — click to view spec.',
        'filename': os.path.basename(filepath),
        'path': filepath,
        'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d'),
    }


def generate_idea_cards(ideas):
    """Generate HTML for idea cards."""
    if not ideas:
        return ''

    html = f'\n    {START_MARKER}\n'
    for idea in ideas:
        # Link to the md file — copy it to the repo so it's accessible on GitHub Pages
        html += f'''
    <div class="dev-card">
      <div class="dev-thumb spec">
        <div class="wireframe">
          <div class="wireframe-icon">&#x1f4a1;</div>
          <div class="wireframe-label">Project Idea</div>
        </div>
      </div>
      <div class="dev-body">
        <span class="dev-status status-idea">Idea</span>
        <h3>{idea['title']}</h3>
        <p>{idea['description']}</p>
        <span style="font-size:10px;color:var(--text-dim);">Added: {idea['modified']}</span>
        <a class="dev-link" href="ideas/{idea['filename']}" target="_blank">View spec &rarr;</a>
      </div>
    </div>
'''
    html += f'    {END_MARKER}\n'
    return html


def sync_idea_files(ideas):
    """Copy .md files to ideas/ directory so they're accessible on GitHub Pages."""
    ideas_dir = os.path.join(BASE_DIR, 'ideas')
    os.makedirs(ideas_dir, exist_ok=True)

    for idea in ideas:
        src = idea['path']
        dst = os.path.join(ideas_dir, idea['filename'])
        with open(src) as f:
            content = f.read()
        with open(dst, 'w') as f:
            f.write(content)


def update_indev_page(ideas):
    """Update in-development.html with idea cards."""
    with open(INDEV_PAGE) as f:
        html = f.read()

    new_section = generate_idea_cards(ideas)

    if START_MARKER in html and END_MARKER in html:
        # Replace existing auto-generated section
        pattern = re.escape(START_MARKER) + r'.*?' + re.escape(END_MARKER)
        html = re.sub(pattern, new_section.strip(), html, flags=re.DOTALL)
    else:
        # Insert before the closing </div> of dev-grid
        insert_point = html.rfind('</div>', 0, html.find('class="back"'))
        if insert_point > 0:
            html = html[:insert_point] + new_section + html[insert_point:]

    with open(INDEV_PAGE, 'w') as f:
        f.write(html)


def main():
    today = datetime.now().strftime('%Y-%m-%d')
    print(f"💡 Sync Project Ideas — {today}")

    if not os.path.isdir(IDEAS_DIR):
        print(f"  ⚠ Ideas directory not found: {IDEAS_DIR}")
        return

    md_files = sorted(glob.glob(os.path.join(IDEAS_DIR, '*.md')))
    print(f"  Found {len(md_files)} idea(s) in {IDEAS_DIR}")

    if not md_files:
        print("  Nothing to sync.")
        return

    ideas = [extract_md_meta(f) for f in md_files]
    for idea in ideas:
        print(f"  📄 {idea['title']} ({idea['filename']}, modified {idea['modified']})")

    sync_idea_files(ideas)
    update_indev_page(ideas)

    print(f"  ✅ In Development page updated with {len(ideas)} idea card(s)")
    print(f"  ✅ Specs copied to ideas/ directory")


if __name__ == '__main__':
    main()
