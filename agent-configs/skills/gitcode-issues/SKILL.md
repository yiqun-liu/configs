---
name: gitcode-issues
description: >-
  Use only when the user explicitly asks to list, view, search, or read issue
  comments for a repository hosted on gitcode.com. Use the bundled read-only
  CLI; it requires GITCODE_TOKEN, curl, and jq. Do not use raw API calls or
  create, comment on, close, label, or edit issues.
---

# GitCode Issues

Read GitCode repository issues through a read-only CLI.

## Scope

Own issue and issue-comment retrieval from GitCode; do not mutate repository or
issue state.

## Trigger

Use this skill only for an explicit request to list, show, search, or read
comments on GitCode issues.

## Inputs and outcome

Use the requested operation, repository, and issue criteria to return the
relevant issue data without side effects.

- Input: an explicit `OWNER/REPO`, or a GitCode origin remote from which to
  resolve the repository.
- Input: `GITCODE_TOKEN`, plus `curl` and `jq` on `PATH`.
- Outcome: formatted issue data or JSON from the requested read-only command.

## Procedure

Run the bundled `scripts/gitcode-issue` command and handle its diagnostic
result.

| Request | Command |
| --- | --- |
| List issues | `gitcode-issue list [options]` |
| Show issue | `gitcode-issue show <number>` |
| Read comments | `gitcode-issue comments <number>` |
| Search issues | `gitcode-issue search <query>` |

- Pass `--repo OWNER/REPO` when an origin remote cannot identify the target.
- Use `--json` only when formatted output lacks needed fields.
- When list or comments reports a full page, request the next page if needed.
- If search returns no result for a fresh issue or repository, use `list` with
  client-side filtering; GitCode search indexing can lag.
- Ask the user to supply or refresh `GITCODE_TOKEN` for authentication failures.

## Completion

Report the repository, command, result, and any pagination or search-index
limit that affects completeness.

Never bypass the CLI with a mutating raw API request.
