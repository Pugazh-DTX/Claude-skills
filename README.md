# Claude-skills

A backup of all Claude skills currently enabled on this account, synced from `~/.claude/skills`.

Each skill lives in its own folder under [`skills/`](skills/) with a `SKILL.md` describing when and how it triggers. `skills/manifest.json` has the full sync metadata (skill IDs, sources, update timestamps).

## Skills

| Skill | Source |
| --- | --- |
| advanced-architecture-review | custom |
| angular-architect | custom |
| angular-developer | plugin |
| code-reviewer | custom |
| codedtx-carousel-layout | plugin |
| codedtx-post | plugin |
| debugging-wizard | custom |
| docx | anthropic |
| import-memory | anthropic-example |
| legacy-modernizer | custom |
| linkedin-post-manager | plugin |
| morning | anthropic-example |
| pdf | anthropic |
| post | custom |
| pptx | anthropic |
| pugazh | plugin |
| react-expert | custom |
| report | custom |
| secure-code-guardian | custom |
| skill-creator | anthropic-example |
| test-master | custom |
| web-quality | plugin |
| xlsx | anthropic |

- **custom** — authored directly by the user
- **plugin** — installed from a marketplace plugin
- **anthropic** / **anthropic-example** — built-in skills shipped by Anthropic
