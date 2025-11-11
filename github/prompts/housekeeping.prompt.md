# Housekeeping

- Definitions:
    - **issue files** : all files in `.work/agent/issues/` folder
    - **history file** : `.work/agent/issue/history.md`
    - **agent notes** : `.work/agent/notes/` folder

- When the user asks you to do some house-cleaning, that is a keyword for you to:
    - validating the current source code against all issues in the `issues files`. NOTE! **ONLY** use the  for this analysis, and **NOT** files in `proposals` or other places.
    - mark any completed tasks in the `issues files` as done and moving them to the history file. 
    - read all your agent notes, consolidate them, remove outdated, redundant or duplicated information, and create a distilled and optimized version of your notes for easier consumption.

- Based on these prompts, update `issue files` with new issues:
  - `.github\prompts\best-practices-check.prompt.md`
  - `.github\prompts\code-analysis.prompt.md`
  - `.github\prompts\pythonic-code.prompt.md`
  - `.github\prompts\task-assesment.prompt.md`

**MANDATORY RULES**
- do **NOT** create other markdown files except for distilling your own notes. Update or create in issue files only
- `issue files` should contain these files only, do not create anything else:
    - shortlist.md
    - backlog.md
    - critical.md
    - high.md
    - medium.md
    - low.md
    - history.md
- If any issue needs more context, add files in the `./work/agent/issues/references/` folder and link to those in your issue