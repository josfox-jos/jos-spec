## What changes and why

<!-- One intention per pull request. Link the issue or proposal. -->

## Synchronization list (golden rule)

- [ ] Prose (`SPECIFICATION.md`), schema (`schema/`) and vectors (`tests/`) change **together**; a change that touches only one of them is not mergeable
- [ ] Change class stated (`GOVERNANCE.md`): editorial / patch / minor / major
- [ ] `CHANGELOG.md` entry
- [ ] `SECURITY.md` sections affected are listed, or "none"
- [ ] `python3 -I tools/check-superset.py` exits 0; every `tests/invalid-*.json` still fails
- [ ] No trademark or product name in normative text; language tags are BCP 47 (`en-US`)
- [ ] No `<pending>` marker added without an open issue that tracks it

## Evidence

<!-- Paste the last line of check-superset.py and the validator output. -->
