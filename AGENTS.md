# Skill synchronization

- `skills/` is the common install set. Sync this directory only on headless Linux.
- `desktop-skills/` is desktop-only opt-in under this repository's deployment policy.
  Never include it in headless Linux installs or recursively discover installable
  skills from the repository root. This includes both `ego-browser` and
  `pptx-editability`, even though the latter can technically run on Linux.
- Preserve system/plugin-managed skills and Ego-managed symlinks. Do not use a
  deletion-capable mirror without an explicit cleanup request.
- See `README.md` for synchronization commands and desktop installation guidance.
