#!/usr/bin/env python3
"""Turn the private artifact export of Young Person 360º: before the label into the public page, index.html.

The portal is edited as a private Claude artifact. This step makes the exported page fit to publish:

  1. its own address, everywhere it appears, becomes the public address, and the colophon QR code is redrawn for it;
  2. links to private artifacts become public addresses, or plain text where nothing public exists;
  3. contact goes through this repository's public contact form: no email address, no team name;
  4. the former office name becomes the Government Data Directorate, and the sibling portal its current name.

Every replacement is asserted, so a change in the export stops the build instead of publishing something half-done.

Run:  python3 tools/publish.py path/to/artifact-export.html   writes index.html
"""
import re
import sys
from pathlib import Path

import segno

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = 'https://cyberdudeuk.github.io/young-person-360/'
REPO = 'https://github.com/cyberdudeuk/young-person-360'
SELF = 'https://claude.ai/artifact/D5Z5M9w61vdEdVQU1sP587'
SIBLING = 'https://cyberdudeuk.github.io/earning-learning-training/'
# A safeguarding helpline's own published address, quoted so adults worried about a child can use it.
ALLOWED_EMAILS = {'help@nspcc.org.uk'}
PRIVATE_LINK = re.compile(r'https://claude\.ai/(?:artifact|code/artifact|chat|project)/[A-Za-z0-9-]+')
UNCAPPED = re.compile(r'(repeat\(auto-fi[lt],)minmax\((\d+(?:\.\d+)?rem),1fr\)')
# The narrow-screen group bar (a five-column grid with wrapping labels) is cancelled by a later stylesheet that makes
# the bar a scrolling row with nowrap tabs (nav.tabs a outranks .gtab), so self-check K43 failed at 320px. Restated
# with higher specificity so it wins wherever it sits in the cascade.
NARROW_BAR = ('<style>@media (max-width:640px){html body nav.tabs .wrap{display:grid;grid-template-columns:repeat(5,minmax(0,auto));'
              'justify-content:space-between;padding:0 .5rem;overflow:visible}html body nav.tabs a.gtab{display:flex;padding:.55rem .35rem;'
              'font-size:var(--fs-1);white-space:normal;text-align:center;justify-content:center;line-height:1.2}'
              'html body nav.tabs a.gtab .ico{display:none}}</style>')
CONTACT_FOOTER = f'<dt>Contact</dt><dd><a href="{REPO}/issues/new/choose">Contact form</a> (public, so leave out personal details)</dd>'


def qr_path(payload):
    """The QR code as the same path drawing the colophon uses: one 1x1 square per dark module, 4-module border."""
    q = segno.make(payload, error='m', boost_error=False)
    rows = list(q.matrix_iter(scale=1, border=4))
    d = ''.join(f'M{x},{y}h1v1h-1z' for y, row in enumerate(rows) for x, dark in enumerate(row) if dark)
    return len(rows), d


def swap(text, old, new, at_least=1):
    n = text.count(old)
    if n < at_least:
        raise SystemExit(f'publish: expected {old[:70]!r} in the export, found {n}')
    return text.replace(old, new)


def transform(s):
    # 1. the page's own address and its QR code (given a title and description too)
    m = re.search(r'(<svg[^>]*class="qr"[^>]*viewBox=")0 0 (\d+) \2("[^>]*>)(.*?)(<path d=")([^"]*)(")', s, re.DOTALL)
    if not m or SELF not in m.group(0):
        raise SystemExit('publish: colophon QR code not found where expected')
    size, d = qr_path(PUBLIC)
    title = '' if '<title>' in m.group(4) else f'<title>QR code</title><desc>QR code that opens this page: {PUBLIC}</desc>'
    s = s[:m.start()] + m.group(1) + f'0 0 {size} {size}' + m.group(3) + title + m.group(4) + m.group(5) + d + m.group(7) + s[m.end():]
    s = swap(s, SELF, PUBLIC, 3)
    # 2. links to private artifacts
    s = swap(s, 'https://claude.ai/artifact/VtxD1e8ZSzBR4NWP2RTB7y', 'https://cyberdudeuk.github.io/black-mixed-heritage/', 1)
    s = swap(s, 'const DOC_LINK="https://claude.ai/code/artifact/b9f5521b-1157-4425-bf1e-78c00c05d601";', 'const DOC_LINK="";', 1)
    s = swap(s, 'el("a",{href:DOC_LINK,target:"_blank",rel:"noopener",text:"Before the label: a young person\'s own 360º view of the state"})',
             'el("span",{text:"Before the label: a young person\'s own 360º view of the state (not yet published)"})', 1)
    # 3. contact by the public form only
    s = swap(s, '<dd><a href="mailto:GDSDataManagement@dsit.gov.uk">Emanuel Silva</a>, Data Management Lead, Office of the Chief Data Officer, Government Digital Service</dd>',
             '<dd>Emanuel Silva, Data Management Lead, Government Data Directorate, Government Digital Service</dd>' + CONTACT_FOOTER, 1)
    s = swap(s, '"contact": "GDSDataManagement@dsit.gov.uk"', '"contact": "the contact form"', 1)
    s = swap(s, 'It is run by the Data Management team, Office of the Chief Data Officer, Government Digital Service.',
             'It is run by Emanuel Silva, Government Data Directorate, Government Digital Service.', 1)
    s = swap(s, 'email the Data Management team at GDSDataManagement@dsit.gov.uk.', 'use the contact form.', 1)
    s = swap(s, 'el("a",{href:"mailto:"+A11Y.contact+"?subject=Before%20the%20label%20feedback",text:A11Y.contact})',
             f'el("a",{{href:"{REPO}/issues/new/choose",text:A11Y.contact}})', 1)
    # 3b. the page's own checks: K103 and K106 encoded contact by team inbox (ADR 0008); restate them for the
    #     contact-form rule (3 Nov 2026) instead of deleting them, so the suite never shrinks
    s = swap(s, 'mail:!!col.querySelector(\'a[href^="mailto:GDSDataManagement@dsit.gov.uk"]\')',
             'contact:!!col.querySelector(\'a[href$="/issues/new/choose"]\')', 1)
    s = swap(s, '&&d.COLO.bc===d.RELEASE&&d.COLO.mail,', '&&d.COLO.bc===d.RELEASE&&d.COLO.contact&&d.COLO.rows.includes("Contact"),', 1)
    s = swap(s, '.split("GDSData"+"Management").length-1,',
             '.split("GDSData"+"Management").length-1,CONTACT_FORM:document.querySelectorAll(\'a[href$="/issues/new/choose"]\').length,', 1)
    k106 = re.search(r'\{id:"K106",name:"[^"]*",run:d=>[^\n]*?breakIt:d=>\{d\.INBOX=0\}\}', s)
    if not k106:
        raise SystemExit('publish: self-check K106 not found where expected')
    s = s[:k106.start()] + ('{id:"K106",name:"Contact is by the public contact form only (rule of 3 Nov 2026, replacing ADR 0008): '
                            'no mailto link in the colophon, no team inbox anywhere, and a contact-form link",'
                            'run:d=>d.OWNER_LINK.length===0&&d.INBOX===0&&d.CONTACT_FORM>0,breakIt:d=>{d.INBOX=1}}') + s[k106.end():]
    # 3c. cap every auto-fit grid minimum at the container width; an uncapped rule later in the cascade beat the
    #     artifact's own capped rule (D41) and made the page scroll sideways at 320px (check C8)
    s, n = UNCAPPED.subn(lambda m: f'{m.group(1)}minmax(min({m.group(2)},100%),1fr)', s)
    if n < 1:
        raise SystemExit('publish: expected uncapped grid minimums in the export, found none')
    s = swap(s, '</head>', NARROW_BAR + '</head>', 1)
    # 4. names
    s = swap(s, 'Earning or learning', 'Earning, learning and training', 5)
    # 5. now both portals are public, link the sibling where a reader would follow it
    s = swap(s, 'Covered in depth by the separate "Earning, learning and training" portal.',
             f'Covered in depth by the separate <a href="{SIBLING}">Earning, learning and training</a> portal.', 1)
    s = swap(s, '<h3>Earning, learning and training</h3><ul id="neetScope">',
             f'<h3><a href="{SIBLING}">Earning, learning and training</a></h3><ul id="neetScope">', 1)
    left = sorted(set(PRIVATE_LINK.findall(s)))
    if left:
        raise SystemExit(f'publish: links to private artifacts remain: {left}')
    return s


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    out = transform(Path(sys.argv[1]).read_text(encoding='utf-8'))
    (ROOT / 'index.html').write_text(out, encoding='utf-8')
    print(f'wrote index.html ({len(out):,} characters)')
