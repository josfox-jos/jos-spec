## What changes

<!-- one paragraph -->

## Change class (GOVERNANCE.md)

- [ ] editorial (no semantic change)
- [ ] compatible addition (MINOR)
- [ ] breaking (MAJOR, needs an accepted JEP: `proposals/JEP-NNNN`)

## The golden rule (all three move together, or none)

- [ ] `SPECIFICATION.md` updated
- [ ] `schema/jos.schema.json` updated
- [ ] `conformance/` vectors updated (valid and invalid)

## Checks

- [ ] `CHANGELOG.md` entry
- [ ] media type and extension unchanged everywhere (`application/vnd.jos+json`, `.jos`)
- [ ] examples validate; invalid vectors are rejected
- [ ] no new external links without checking them
