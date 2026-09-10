# Claude-skills

A backup of all Claude skills currently enabled on this account, synced from `~/.claude/skills`.

Each skill lives in its own folder under [`skills/`](skills/) with a `SKILL.md` describing when and how it triggers. `skills/manifest.json` has the full sync metadata (skill IDs, sources, update timestamps).

## Skills

| Skill | Source |
| --- | --- |
| advanced-architecture-review | custom |
| angular-architect | custom |
| angular-developer | plugin |
| cache-components | imported |
| code-reviewer | custom |
| debugging-wizard | custom |
| legacy-modernizer | custom |
| nestjs-expert | imported |
| next-cache-components-adoption | imported |
| next-cache-components-optimizer | imported |
| next-dev-loop | imported |
| next-partial-prefetching-adoption | imported |
| nextjs | imported |
| nextjs-16-perf-cache | imported |
| nextjs-developer | imported |
| nextjs-seo | imported |
| playwright | imported |
| playwright-expert | imported |
| react | imported |
| react-expert | custom |
| react-hook-form | imported |
| report | custom |
| secure-code-guardian | custom |
| skill-creator | anthropic-example |
| test-master | custom |
| typescript | imported |
| typescript-pro | imported |
| web-quality | plugin |

- **custom** — authored directly by the user
- **plugin** — installed from a marketplace plugin
- **anthropic** / **anthropic-example** — built-in skills shipped by Anthropic
- **imported** — added manually from an external source (not part of the account sync); see below

## Imported skills

The following skills were added manually (not via the `~/.claude/skills` sync) and are not reflected in `skills/manifest.json`:

- `typescript-pro`, `playwright-expert`, `nextjs-developer`, `nestjs-expert` — from [Jeffallan/claude-skills](https://github.com/Jeffallan/claude-skills)
- `next-cache-components-adoption`, `next-cache-components-optimizer`, `next-dev-loop`, `next-partial-prefetching-adoption` — from the official [vercel/next.js](https://github.com/vercel/next.js) `nextjs` plugin (`skills/` directory, canary branch)
- `nextjs` — from [pproenca/dotskills](https://github.com/pproenca/dotskills) (`master/skills.curated/nextjs`)
- `nextjs-seo`, `cache-components` — from [laguagu/claude-code-nextjs-skills](https://github.com/laguagu/claude-code-nextjs-skills)
- `nextjs-16-perf-cache` — hand-authored Next.js 16 performance/caching skill, uploaded as a plain Markdown file; wrapped with standard `SKILL.md` frontmatter to match this repo's convention
- `playwright`, `react-hook-form`, `typescript`, `react` — from [pproenca/dotskills](https://github.com/pproenca/dotskills) (`master/skills.curated/`); distinct from the same-topic `playwright-expert`, `typescript-pro`, `react-expert` skills from Jeffallan/claude-skills
