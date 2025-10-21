# SpecKit Immersive Workflow (Easy Mode)

SpecKit turns planning into a guided conversation. This repo already includes everything you need. Follow these steps and you’re good to go.

---

## 1. Run a quick health check

```bash
python scripts/speckit_check.py
```

The script tells you:
- whether the `.speckit/` folder exists (it contains all command prompts)
- if your Python version is high enough for the official SpecKit CLI (needs 3.11+)
- optional tools you can install later (`uv`, `pipx`)

You can keep using Python 3.9/3.10—the templates still work. Upgrading is only needed if you want the real CLI.

---

## 2. Follow the command trail

Think of this like a simple roadmap. Run each command in order and copy the results into the matching OpenSpec files.

```
/speckit.constitution → /speckit.specify → /speckit.plan → /speckit.tasks → /speckit.implement
```

Where to find the prompts:
- `.speckit/commands/constitution.md`
- `.speckit/commands/specify.md`
- `.speckit/commands/plan.md`
- `.speckit/commands/tasks.md`
- `.speckit/commands/implement.md`
- Bonus helpers live in the same folder: `clarify`, `checklist`, `analyze`

Each prompt is written so a 10th grader (or an AI assistant) can fill it in. Copy the answers into these OpenSpec files:

| Step | Save the results in |
|------|---------------------|
| `/speckit.specify` | `openspec/changes/<change-id>/specs/<capability>/spec.md` |
| `/speckit.plan` | `openspec/changes/<change-id>/proposal.md` |
| `/speckit.tasks` | `openspec/changes/<change-id>/tasks.md` |
| `/speckit.checklist` (optional) | `openspec/changes/<change-id>/checklists/requirements.md` |

---

## 3. Want automation? Use the official CLI later

If you upgrade to Python 3.11+ (or install `uv`), you can run the same flow with real slash commands:

```bash
# Install uv (one line)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run SpecKit helpers
uvx gh+github/spec-kit specify-cli check
uvx gh+github/spec-kit specify-cli init --here
```

These commands scaffold folders and run the scripts for you. They’re optional—the templates already do the job.

---

## 4. Finish with OpenSpec validation

When the spec, plan, and tasks look good:

```bash
openspec validate <change-id> --strict
```

If everything passes, you’re ready to implement and later archive the change.

---

## Reference Links
- SpecKit repo: https://github.com/github/spec-kit
- Spec-driven playbook: https://github.com/github/spec-kit/blob/main/spec-driven.md
- This project’s OpenSpec primer: `openspec/AGENTS.md`
