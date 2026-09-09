---
name: report
description: Generate daily or weekly progress reports from git commits and Claude Code session activity, for whatever project the current directory belongs to. Use when the user says "daily report", "weekly report", "status report", or invokes /report.
user_invocable: true
---

# Report Generator — Executive-Ready

Generate a **professional, executive-ready** progress report for Managers, Directors, and Managing Directors. The report combines git commit history, Claude Code session activity, and working-tree state. It is written in **business language** — no raw code, no commit hashes in the main body, no file paths, no technical jargon. Leadership cares about: what was delivered, what's at risk, and what's next.

**This report goes to senior leadership with the developer's name on it. Accuracy outranks polish.** Every statement must trace back to actual evidence in commits, tickets, or session logs. See §3d.

---

## 0. Resolve project context (every run)

1. **Repo root:** `git rev-parse --show-toplevel`. If not a git repo, stop and say so.
2. **Developer name:** `git config user.name` (fall back to OS username).
3. **Project name:** in priority order — (a) `displayName` or `name` from `package.json` at the repo root; (b) a `reports/.report-config.json` file if one exists (see below); (c) the repo folder name, title-cased with hyphens/underscores as spaces. Do NOT invent stylized branding (punctuation, capitalization) that isn't in the source. If the derived name looks wrong, ask the user once and offer to save their answer to `reports/.report-config.json` so future runs use it automatically.
4. **Session log folder:** derive from the absolute repo path — replace `:`, `\`, `/` with `-`. Session logs are at:
   - Windows: `$env:USERPROFILE\.claude\projects\<derived>\*.jsonl`
   - macOS/Linux: `~/.claude/projects/<derived>/*.jsonl`
   If that folder doesn't exist, list `~/.claude/projects/` and pick the closest match.
5. **Recipient:** use only if the user names one in this invocation, or if `reports/.report-config.json` defines a default. Otherwise omit the "Prepared for:" line.

Optional `reports/.report-config.json` (per-project, created only when the user confirms):
```json
{
  "projectName": "PL!VE Web UI",
  "recipient": "Abraham",
  "featureAreas": { "payment|billing|subscription": "Payment & Billing" }
}
```

Use resolved values throughout — never hardcode paths, names, or recipients in this skill file.

---

## 1. Report type and period

| User says | Generate | Period |
|-----------|----------|--------|
| "weekly", "week", or names a recipient for a weekly summary | **weekly** | Current week (Mon–today) |
| "last week", "past week", "previous week" | **weekly** | Previous week (Mon–Sun) |
| "week of [date]", "[month] [day] week" | **weekly** | The week containing that date |
| "yesterday" | **daily** | Previous day |
| "[date]" e.g. "Aug 14", "2026-08-14" | **daily** | That specific day |
| "both" | **both** | Current periods |
| anything else | **daily** | Today |

### Resolving the period

```powershell
# Current week (Monday 00:00 → now)
$today = Get-Date
$daysToMon = if ([int]$today.DayOfWeek -eq 0) { 6 } else { [int]$today.DayOfWeek - 1 }
$weekStart = $today.AddDays(-$daysToMon).Date
$weekEnd   = $today

# Last week (previous Monday 00:00 → Sunday 23:59)
$lastWeekStart = $weekStart.AddDays(-7)
$lastWeekEnd   = $weekStart.AddSeconds(-1)

# Specific week containing a given date
$targetDate = [datetime]"2026-08-14"
$dtm = if ([int]$targetDate.DayOfWeek -eq 0) { 6 } else { [int]$targetDate.DayOfWeek - 1 }
$weekStart = $targetDate.AddDays(-$dtm).Date
$weekEnd   = $weekStart.AddDays(7).AddSeconds(-1)
```

Always pass **both** `--since` and `--until` to git when the period is not "current":

```powershell
git log --since="$($start.ToString('yyyy-MM-dd')) 00:00:00" --until="$($end.ToString('yyyy-MM-dd HH:mm:ss'))" --format="%h|%s|%ad" --date=short --no-merges
```

Filter session files by `LastWriteTime -ge $start -and $_.LastWriteTime -le $end`, and filter each JSONL line's `timestamp` to the same window — a session file can span multiple days.

### Handling weeks with no commits

A period can have **session activity but zero commits** (investigation, debugging, planning, code review, or work committed later). This is normal — do NOT report it as "no work done".

When commits are zero but sessions exist:
- Title the delivery section **"Work Performed"** instead of "Deliverables"
- Describe the investigation, analysis, and decisions from session activity
- Set status to reflect reality: "Analysis & Investigation" rather than "On Track"/"Blocked"
- Note in the summary that work was research/debugging-focused with commits landing in a later period

Only report "no activity" when **both** commits and sessions are empty for the period.

---

## 2. Gather git data

Use PowerShell on Windows, bash on macOS/Linux.

### Daily
```powershell
$rawCommits = @(git log --since="midnight" --format="%h|%s|%ad" --date=format:"%H:%M" --no-merges 2>$null | Where-Object { $_ -ne "" })
$branch     = git branch --show-current 2>$null
$firstHash  = git log --since="midnight" --format="%H" --no-merges 2>$null | Select-Object -Last 1
$filesTouched = if ($firstHash) { @(git diff --name-only "${firstHash}^" HEAD 2>$null | Where-Object { $_ -ne "" } | Sort-Object -Unique) } else { @() }
$dirty      = @(git status --porcelain 2>$null | Where-Object { $_ -ne "" })
```

### Weekly (Monday–today)
```powershell
$today     = Get-Date
$dayOfWeek = [int]$today.DayOfWeek
$daysToMon = if ($dayOfWeek -eq 0) { 6 } else { $dayOfWeek - 1 }
$monday    = $today.AddDays(-$daysToMon).Date
$sinceArg  = $monday.ToString("yyyy-MM-dd") + " 00:00:00"
$rawCommits = @(git log --since="$sinceArg" --format="%h|%s|%ad" --date=short --no-merges 2>$null | Where-Object { $_ -ne "" })
$branch     = git branch --show-current 2>$null
$firstHash  = git log --since="$sinceArg" --format="%H" --no-merges 2>$null | Select-Object -Last 1
$statsRaw   = if ($firstHash) { git diff --shortstat "${firstHash}^..HEAD" 2>$null } else { "N/A" }
$dirty      = @(git status --porcelain 2>$null | Where-Object { $_ -ne "" })
```

### Commit processing
- Group by ticket: regex `([A-Z]+)\s*-\s*(\d+)`, normalize to `ABC-1234`. This matches any tracker prefix, not just one project's.
- Detect bug fixes: case-insensitive match on `fix`, `bug`, `issue`, `error`, `freeze`, `crash`, `broken`.
- Strip ticket prefix from display text.

### Ticket titles (preferred source of business language)
If an issue-tracker integration is available (Jira MCP, `gh`, etc.), fetch the **title and summary** for each detected ticket. A ticket title is written in business terms by definition and is the single best source for §3d — far better than inferring impact from a diff. If no tracker is reachable, note that and fall back to commit messages.

---

## 3. Read Claude Code session files

Session files at `$sessionLogDir`. Filter by `LastWriteTime` (today for daily, since Monday for weekly). Also filter each JSONL line's `timestamp` to the reporting period — a session file can span multiple days.

### 3a. Session titles
Extract `ai-title` or `custom-title` entries for session context.

### 3b. User messages (`type == "user"`, `userType != "system"`)

**Skip if any of these match:**
- Shorter than 15 characters
- Starts with: `This session is being continued`, `<system-reminder>`, `<local-command`, `<command-name>`, `<command-message>`, `<!-- attach -->`, `<ide_selection>`
- Contains: `<local-command`, `<command-name>`, `<command-message>`
- Matches: `^\s*#\s+(Schedule|System|MCP|Environment|Report Generator)`
- Starts with: `Unknown command`, `(Re-invocation`, `Base directory for this skill`
- Is a bare slash command or just `daily report` / `weekly report`

Trim, collapse whitespace, truncate at 130 chars.

### 3c. Assistant outcomes (`type == "assistant"`)

Keep first line if it starts with: `Fixed`, `Found`, `Root cause`, `Added`, `Removed`, `Changed`, `Updated`, `Simplified`, `Resolved`, `Refactored`, `Migrated`, `Implemented`, `Created`, `The fix`, `The issue`, `The bug`, `The root cause`, `The problem`

Truncate at 140 chars. Deduplicate (same first 80 chars = duplicate).

### 3d. CRITICAL — Translate the language, not the facts

**This is the most important step, and the easiest to get wrong.**

Raw session messages and commit logs are **source material, not report content** — they must be rewritten. But rewriting means changing *vocabulary and framing*, never *adding claims*. This report carries the developer's name to senior leadership; an invented impact statement that turns out to be wrong is far more damaging than a plainly-worded accurate one.

**What you MAY do:**
- Remove file names, function names, CSS classes, variable names, framework specifics
- Name the feature area instead of the code location
- Use business verbs: Resolved, Implemented, Delivered, Investigated, Optimized, Redesigned
- Carry across impact that is **already stated** in the ticket title, ticket description, commit message, or the session conversation

**What you MUST NOT do:**
- Assert a user-facing symptom that no source mentions ("users experienced a freeze") unless a source says so
- Name a specific screen or flow the sources don't identify
- Claim a change was "per approved design specifications" unless a source says that
- Assert business value ("improves conversion", "reduces churn") — never inferable from a diff
- Upgrade a small change into a "delivery" or "feature"

**Evidence-grounded translation:**

| Raw source | Evidence available | Correct executive version |
|---|---|---|
| commit `UIUX-9236 fix pop-up-mode overflow` + ticket titled "Post-purchase page freezes on mobile" | ticket states symptom | "Resolved the post-purchase page freeze reported in UIUX-9236." |
| commit `fix pop-up-mode overflow hidden`, no ticket title available | only the code change | "Fixed a display issue in the purchase overlay (UIUX-9236)." |
| session: "found bug in handleAccountProfileResponse" + conversation shows SSO email missing | conversation states symptom | "Corrected SSO profile data not populating for signed-in users." |
| commit `remove dead purchaseStatus subject` | internal cleanup only | "Removed unused code in the purchase module to reduce maintenance overhead." |

Note the second row: when evidence is thin, the honest version is **shorter and vaguer**, not invented. That is the correct outcome.

**When impact genuinely can't be determined,** describe the area and nature of the work plainly ("Ongoing work on the payment confirmation flow") rather than inventing a consequence. If several items are like this, add a line to the report: *"Detailed business impact pending ticket cross-reference."*

**Writing guidelines:**
- Reference the ticket ID so leadership can cross-reference
- Keep each item to 1–2 sentences
- No code snippets, file paths, function names, or CSS classes in the main body

---

## 4. Auto-resolve status

Derive status only from signals that actually indicate it. **Never infer completion from commit count or the word "fix" in a message** — those say nothing about whether work is done.

### Status signals, in order of reliability
1. **Issue tracker state** — if a ticket's status is reachable (Jira MCP, `gh issue view`), use it verbatim. This is the only authoritative source.
2. **PR state** — if a PR exists for the branch (`gh pr view --json state,isDraft`), map: open+draft → "In progress"; open+ready → "Under review"; merged → "Completed"; none → unknown.
3. **Branch merged into the default branch?** (`git branch --merged`) → "Completed".
4. **None of the above available** → report status as **"In progress"** and add a note that status could not be verified automatically. Do not guess a more advanced state.

### Other fields
- **Current ticket** from branch name (e.g. `UIUX-9236-accountprofile-fix` → "UIUX-9236").
- **Uncommitted work** (`$dirty` non-empty) → "Additional changes in progress" (not "3 files modified").
- **Next steps** — take from the session conversation if the developer stated a plan; otherwise write "To be confirmed" rather than inventing one.

### Risks & Blockers
- Report a blocker only where there is **positive evidence** of one: the session conversation mentions being blocked/waiting on someone, an unresolved error thread, or repeated failed attempts at the same problem across sessions.
- **No commits today is not a blocker** and must not be reported as one. Meetings, reviews, planning, and investigation are normal. If there are no commits but there is session activity, report the investigative work (per §1 "Handling weeks with no commits"). If there is neither, state "No recorded code activity today" as a neutral fact.
- Default when no evidence exists: "No blockers identified."

### Overall assessment
Report **On Track** unless there is evidence for At Risk or Blocked (an explicit blocker, a slipped deadline mentioned in session or ticket, or a stated dependency on another team). Do not assign At Risk on a hunch. When the period is investigation/analysis-only (commits = 0, sessions > 0), use "Analysis & Investigation" instead of the On Track / At Risk scale.

---

## 5. Categorize by feature area

Derive feature areas from the **repository's own structure** — this keeps the skill portable across projects.

1. **If `reports/.report-config.json` defines `featureAreas`,** use that mapping (regex → business label). This is the per-project override.
2. **Otherwise, derive from the repo:** group changed files by their meaningful top-level grouping directory (e.g. `src/app/<area>/`, `packages/<name>/`, `apps/<name>/`, `modules/<name>/`). Convert the directory name into a readable label (`account-profile` → "Account Profile"). Skip generic wrappers like `src`, `lib`, `app` when they contain only one child.
3. **Optionally enrich** with the ticket's component/epic field if the tracker exposes one — that is already business-labelled.

Only use a domain-specific keyword table if the project defines one in its config. Example of what a project *could* configure — do not apply these defaults to arbitrary repos:

```json
{ "featureAreas": {
    "payment|billing|subscription|plans": "Payment & Billing",
    "account|profile|login|auth|sso":     "User Account & Authentication",
    "player|playback|streaming|drm":      "Video Player & Streaming"
}}
```

If the developer wants a stable set of business area names for their project, offer once to write them into `reports/.report-config.json`.

---

## 6. Report formats

### DAILY REPORT

```
---

DAILY STATUS REPORT
[Full date — e.g. Monday, August 17, 2026]

Project: [$projectName]
Developer: [$developerName]
Branch/Ticket: [ticket from branch — e.g. UIUX-9236]

---

STATUS SUMMARY

[One paragraph, 2-3 sentences. State what was accomplished today at a high level. Mention the ticket(s), the number of items delivered, and the business areas impacted. Every claim must be grounded per §3d. Example:

"Delivered two fixes for UIUX-9236 today, addressing the post-purchase page freeze and SSO profile display issues reported in the ticket. Work touched the Payment and Account Management areas."]

---

COMPLETED TODAY
[Or "WORK PERFORMED" if commits = 0 but sessions exist — see §1]

[ticket] — [Business-friendly ticket title — use the real tracker title where available]
  - [Executive-language work item 1]
  - [Executive-language work item 2]

---

AREAS IMPACTED
- [Area name]: [brief description of what changed]
- [Area name]: [brief description]

---

INVESTIGATION & ANALYSIS
- [Business-language summary of root cause analysis or research done in session]
- [Decisions made and rationale in plain language]

---

CURRENT STATUS
- Ticket: [TICKET] — [Status, per §4 signal order] [add "(status not automatically verified)" if derived from fallback]
- Next steps: [From session if stated, otherwise "To be confirmed"]

RISKS & BLOCKERS
- [Evidence-based only, or "No blockers identified"]

---
```

### WEEKLY REPORT

```
---

WEEKLY STATUS REPORT
[Monday date] — [Friday/end date, year]
Week [YYYY-WNN]

Project: [$projectName]
Developer: [$developerName]
[Prepared for: recipient — only if specified]

---

EXECUTIVE SUMMARY

[3-4 sentences for a director/MD audience. Cover:
- Which tickets/features were worked on this week
- Key deliverables (what shipped or is ready for review)
- Any risks or blockers (evidence-based only)
- Overall assessment: On Track / At Risk / Blocked / Analysis & Investigation

Example:
"This week focused on UIUX-9236, addressing the payment flow freeze and SSO profile display issues described in the ticket. Two fixes were committed and are pending review. Work is on track with no blockers recorded."]

Overall Status: [On Track / At Risk / Blocked / Analysis & Investigation]

---

DELIVERABLES THIS WEEK
[Or "WORK PERFORMED THIS WEEK" if commits = 0 but sessions exist]

[ticket] — [Business-friendly title]
  - [Work item in executive language]
  - [Work item in executive language]

[ticket-2] — [Title]
  - [Work item]

---

KEY DECISIONS & FINDINGS
- [Day]: [Business-language decision, grounded in what the session actually recorded]
- [Day]: [Finding]

---

AREAS OF WORK
- [Area]: [Summary of what changed and why]
- [Area]: [Summary]

---

BUGS RESOLVED
- [TICKET]: [User-facing description where the ticket or session supports one; otherwise a plain description of the defect]

---

IN PROGRESS
- [TICKET]: [Current status, what remains]

PLANNED FOR NEXT WEEK
- [To be filled in before sharing — list 3-5 planned items in business terms]

RISKS & BLOCKERS
- [Evidence-based only, or "No blockers identified"]

---

WEEKLY METRICS
- Deliverables completed: [N]
- Bugs resolved: [N]
- Feature areas impacted: [list]
- Tickets: [list]
- Status: [On Track / At Risk / Blocked / Analysis & Investigation]

---
```

**Before saving, review the draft once against §3d:** for each business-impact claim, confirm a source states it. Soften or remove any that don't survive.

---

## 7. Save and deliver

1. Create `$projectRoot/reports/daily/` or `$projectRoot/reports/weekly/` if needed.
2. Save as `YYYY-MM-DD.md` (daily) or `YYYY-WNN.md` (weekly).
3. Deliver via `SendUserFile`.
4. Print a **one-line summary**: e.g. "Daily report: 2 items on UIUX-9236 across Payment and Account areas. Status: In progress (not tracker-verified)."

Do NOT re-paste the full report.

---

## 8. Technical appendix (at bottom of file)

After the main report, add a separated section titled "Technical Reference":
- Commit hashes and raw messages (for developer's own reference)
- File paths changed
- Session file count and topic count

This lets the developer cross-reference without cluttering the executive sections. Format:

```
---
TECHNICAL REFERENCE (internal use only)
---
Commits:
  - [hash] [raw message] ([time])

Files changed:
  - [file path]

Session activity: [N] sessions, [N] topics discussed
```

---

## Critical rules

1. **Accuracy outranks polish.** This document carries the developer's name to senior leadership. A plain accurate sentence beats a polished invented one.
2. **Translate language, never add facts** — see §3d. If evidence is thin, the honest output is shorter and vaguer, not fabricated.
3. **Executive language only** in the main body — no code, no file paths, no function names, no CSS classes.
4. **Never hardcode** paths, project names, or recipients — resolve dynamically per §0.
5. **Derive feature areas from the repo or its config** — never assume another project's domain vocabulary.
6. **Status comes from tracker/PR/merge state**, not commit counts or keywords. Unknown status is reported as unknown.
7. **Absence of commits is not a blocker.** Only report blockers with positive evidence. Session-only periods are "Analysis & Investigation."
8. **Match shell to OS** — PowerShell on Windows, bash on macOS/Linux.
9. **Deduplicate** all content before writing.
10. **Keep it scannable** — a director should get the full picture from the Executive Summary alone.
