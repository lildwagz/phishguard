---
name: phishguard-context
description: Load full context for the PhishGuard AI course project (SMS/Email phishing detector, mata kuliah Kecerdasan Buatan UBSI) before doing any work in this directory — status, architecture, requirements, and conventions. Trigger whenever the user asks to continue, check status, or do anything on PhishGuard, this course project, or files under ~/projects/MyProject/PhishGuard.
---

# PhishGuard project context

Before doing anything else in this project:

1. Read `README.md` in this directory — current status checklist, architecture plan, defined functional/nonfunctional requirements, folder layout, and the ordered list of next steps not yet done.
2. Read `AGENTS.md` in this directory — conventions and guardrails (what never to edit, what data to never invent, standing tool preferences like apt-over-snap).
3. Only then proceed with whatever the user asked for.

After finishing a unit of work (chosen dataset, written model code, built an API endpoint, etc.), update `README.md`'s status checklist so the next session/agent doesn't redo it or think it's still pending.

If the user's request conflicts with something in AGENTS.md (e.g. asks to fill in group/member data, or edit a course slide PDF), follow the user's explicit instruction for that turn — AGENTS.md guardrails exist to avoid guessing, not to override a clear direct ask.
