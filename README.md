# Young Person 360º: before the label

Every child and young person the state holds, loses or never sees, across the UK, from birth: who they are, how many
there are, the records kept about them, and where the trail breaks. Every figure cites its source.

**Open it:** https://cyberdudeuk.github.io/young-person-360/

A prototype and independent analysis, not an official government service. Journeys are fictional composites.

## What is in it

- **The cohorts:** children held by the state or another adult (in care, in custody, with a parent in prison, in
  licensed work), and those lost or unseen (children not in school, missing from education, outside oversight).
- **BEET and CHEET:** the states before NEET, so a young person is seen before they are labelled.
- **The record trail:** who holds each record, which number identifies it, and where it breaks.
- **Departure events:** the moments a child leaves oversight, which the NEET and adult portals pick up.
- **History, the four nations, and the options** for joining the records up.

## How it fits with the other 360º portals

Each topic lives in one place, and the others link to it
([shared glossary and routing](https://cyberdudeuk.github.io/data/shared-glossary.json)):

| Portal | Owns |
|---|---|
| **Young Person 360º** (this one) | Children and young people held, lost or unseen by the system, from birth |
| [Earning, learning and training](https://cyberdudeuk.github.io/earning-learning-training/) | How a 16 to 24 year old gets into work, learning or training |
| [Starting a business in the UK](https://cyberdudeuk.github.io/start-a-business-uk/) | Starting a business at any age, including a parent's duties when children are involved |
| Whole-life 360º (not yet published) | Adults, including learning, retraining and going back to work |

## How it is built and run

The portal is edited as a private Claude artifact. `tools/publish.py` turns its export into `index.html`, fit to
publish: its own address and QR code become the public ones, links to private artifacts become public addresses or
plain text, contact goes to the [contact form](https://github.com/cyberdudeuk/young-person-360/issues/new/choose), and
names are brought up to date. Every replacement is asserted.

The fixes that belong in the artifact too (contact, names, layout, the page's own contact checks) are *source fixes*:
they were carried back into the artifact on 22 November 2026, and the build confirms them rather than reapplying
them. `python3 tools/publish.py --source export.html out.html` applies only those, for republishing the artifact.

The page runs 107 checks on itself in your browser, each with a negative test. `tools/check.py` runs 11 checks in CI,
each proved by a deliberate break (`--negative`).

```
python3 tools/publish.py path/to/export.html   # after editing the artifact
python3 tools/check.py                          # 11 checks
python3 tools/check.py --negative               # prove each check fails when it should
```

## Keeping it running

| Task | When | Effort |
|---|---|---|
| Recheck the sources (the page warns when they fall outside its review window) | Each quarter | Two to three hours |
| Republish after editing the artifact | After each change | Minutes |
| Answer contact-form issues | As they come | Minutes each |

## Contact and licence

Contact is by the [contact form](https://github.com/cyberdudeuk/young-person-360/issues/new/choose) only; it is public,
so leave out personal details. If a child is in danger, call 999; children can call Childline on 0800 1111.
Security problems: see [SECURITY.md](SECURITY.md).

Code: MIT. Written content: Open Government Licence v3.0. Quoted content stays under its owners' terms. See
[LICENSE](LICENSE).
