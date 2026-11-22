# Changelog

## 22 November 2026: published as a public site

- First public release, from release 1.6.0 of the private artifact, under the name *Young Person 360º: before the
  label*.
- Contact goes through the public contact form. The colophon and the accessibility statement no longer show an email
  address or a team name, and name the Government Data Directorate.
- The sibling NEET portal is called by its current name, *Earning, learning and training*, which keeps the 16 to 24
  record trail and risk tools; this portal owns children held, lost or unseen from birth.
- The colophon QR code opens the public address and has a title and description.
- Fixed sideways scrolling at 320px, found by the visual inspection before publishing. Root cause: a later,
  uncapped grid rule beat the artifact's own capped one (D41), and a later stylesheet cancelled the narrow-screen
  group bar. The build caps every auto-fit grid minimum and restates the narrow bar; check C8 and the page's own
  K43 guard both.
- The page's own checks K103 and K106 asked for the team inbox (ADR 0008). They now check the contact-form rule
  instead: no mailto link, no team inbox, and a contact-form link. The suite still has 107 checks.
- New check C9: every YAML and CFF file parses. The contact form's description needed quoting once it named this portal.
- Links to the sibling portal, *Earning, learning and training*, from the welcome note and the Relationship with NEET panel, now both are public.
- The source fixes (contact, names, layout, the page's own contact checks) were carried back into the artifact, now release 21 of it. `tools/publish.py` confirms them instead of reapplying them, and has a `--source` mode; the public page built from the new export is byte-identical to the one it replaces.
