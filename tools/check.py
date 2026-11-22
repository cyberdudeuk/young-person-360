#!/usr/bin/env python3
"""Checks for the public site built by tools/publish.py. Each exists because of a rule or a defect.

C1  no link to a private Claude artifact (the public page must work for everyone)
C2  no email address anywhere: contact is by the public form only
C3  no former office name and no team name in the published files
C4  no link carries a tracking parameter
C5  the colophon QR code carries the public address, and its drawing is that address (redrawn, not stale)
C6  the standard files are present, and the page links to the contact form
C7  the page has one main heading in its static markup at most (the welcome screen used to add a second)
C8  no auto-fit grid has an uncapped minimum width (Young Person 360º overflowed at 320px: a later uncapped
    minmax(19rem,1fr) overrode the capped one, so the earlier fix, D41, never took effect)
C9  every YAML and CFF file parses (an unquoted "360º: before" in the contact form would have made GitHub drop it)

Run:  python3 tools/check.py              all checks
      python3 tools/check.py --negative   break each check on a copy and prove it fails
"""
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import publish  # shares the public address and the QR drawing
import yaml

FILES = ['index.html', '404.html']
STANDARD = ['README.md', 'LICENSE', 'CITATION.cff', 'SECURITY.md', 'CHANGELOG.md', 'publiccode.yml', '404.html',
            '.nojekyll', '.github/ISSUE_TEMPLATE/contact.yml', '.github/ISSUE_TEMPLATE/config.yml']
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.(?:uk|com|org|net|gov|io)\b')
BANNED = re.compile(r'Office of the Chief Data Officer|\bOCDO\b|Data Management Team', re.IGNORECASE)
UNCAPPED_GRID = re.compile(r'repeat\(auto-fi[lt],\s*minmax\(\d+(?:\.\d+)?(?:rem|em|px),\s*1fr\)\)')
TRACKING = re.compile(r'[?&](?:utm_[a-z]+|gad_[a-z]+|gclid|fbclid|mc_eid|_hsenc)=')


def problems(root):
    root = Path(root)
    out = []
    texts = {f: (root / f).read_text(encoding='utf-8') for f in FILES if (root / f).exists()}
    for f, t in texts.items():
        for link in sorted(set(publish.PRIVATE_LINK.findall(t))):
            out.append(f'C1 {f} links to a private artifact: {link}')
        for e in sorted(set(EMAIL.findall(t)) - getattr(publish, 'ALLOWED_EMAILS', set())):
            out.append(f'C2 {f} shows an email address: {e}')
        if BANNED.search(t):
            out.append(f'C3 {f} names {BANNED.search(t).group(0)}')
        if TRACKING.search(t):
            out.append(f'C4 {f} has a tracking parameter: {TRACKING.search(t).group(0)}')
    page = texts.get('index.html', '')
    m = re.search(r'<svg[^>]*class="qr"[^>]*viewBox="0 0 (\d+) \1"[^>]*data-payload="([^"]*)"[^>]*>.*?<path d="([^"]*)"', page, re.DOTALL)
    if not m:
        out.append('C5 the colophon QR code is missing')
    else:
        size, d = publish.qr_path(publish.PUBLIC)
        if m.group(2) != publish.PUBLIC:
            out.append(f'C5 the QR code carries {m.group(2)}, not the public address')
        if m.group(3) != d or int(m.group(1)) != size:
            out.append('C5 the QR drawing does not encode the public address')
    for f in STANDARD:
        if not (root / f).exists():
            out.append(f'C6 {f} is missing')
    if not re.search(re.escape(f'<a href="{publish.REPO}/issues/new/choose">') + r'Contact(?: form)?</a>', page):
        out.append('C6 the page footer does not link to the contact form')
    static = re.sub(r'<script\b.*?</script>', '', page, flags=re.DOTALL | re.IGNORECASE)  # templates in scripts build headings at run time
    if len(re.findall(r'<h1[\s>]', static)) > 1:
        out.append('C7 the page has more than one main heading in its markup')
    if UNCAPPED_GRID.search(page):
        out.append(f'C8 a grid minimum can force sideways scrolling: {UNCAPPED_GRID.search(page).group(0)}')
    for f in sorted(p for p in root.rglob('*') if p.suffix in ('.yml', '.yaml', '.cff') and '.git' not in p.parts):
        try:
            yaml.safe_load(f.read_text(encoding='utf-8'))
        except yaml.YAMLError as e:
            out.append(f'C9 {f.relative_to(root)} does not parse: {str(e).splitlines()[0]}')
    return out


def _edit(root, f, fn):
    p = Path(root) / f
    p.write_text(fn(p.read_text(encoding='utf-8')), encoding='utf-8')


BREAKS = {
    'C1': lambda r: _edit(r, 'index.html', lambda t: t + '<a href="https://claude.ai/artifact/AbC123">x</a>'),
    'C2': lambda r: _edit(r, '404.html', lambda t: t + '<p>someone@example.org.uk</p>'),
    'C3': lambda r: _edit(r, 'index.html', lambda t: t + '<p>run by the Data Management team</p>'),
    'C4': lambda r: _edit(r, 'index.html', lambda t: t + '<a href="https://www.gov.uk/x?utm_source=y">x</a>'),
    'C5': lambda r: _edit(r, 'index.html', lambda t: t.replace('M4,4h1v1h-1z', 'M5,5h1v1h-1z', 1)),
    'C6': lambda r: (Path(r) / 'SECURITY.md').unlink(),
    'C6b': lambda r: _edit(r, 'index.html', lambda t: t.replace('/issues/new/choose">Contact', '/issues">Contact')),
    'C7': lambda r: _edit(r, 'index.html', lambda t: t.replace('<body', '<body><h1>a</h1><h1>b</h1>', 1)),
    'C8': lambda r: _edit(r, 'index.html', lambda t: t.replace('</style>', '.x{grid-template-columns:repeat(auto-fit,minmax(19rem,1fr))}</style>', 1)),
    'C9': lambda r: _edit(r, '.github/ISSUE_TEMPLATE/config.yml', lambda t: t + '\nbroken: [unclosed\n'),
}


if __name__ == '__main__':
    if '--negative' in sys.argv:
        failed = []
        for code, brk in BREAKS.items():
            with tempfile.TemporaryDirectory() as tmp:
                shutil.copytree(ROOT, tmp, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git'))
                brk(tmp)
                caught = any(p.startswith(code.rstrip('b') + ' ') for p in problems(tmp))
                print(f'{code}: {"caught" if caught else "NOT CAUGHT"}')
                if not caught:
                    failed.append(code)
        sys.exit(1 if failed else 0)
    found = problems(ROOT)
    print('\n'.join(found) if found else f'PASS: {len(BREAKS)} checks')
    sys.exit(1 if found else 0)
