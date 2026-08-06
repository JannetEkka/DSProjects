# Using this skill everywhere

`SKILL.md` here applies when Claude is working inside this repo.

To make it apply in every repo and every session, copy it to your user-level
skills directory:

```bash
mkdir -p ~/.claude/skills/human-voice
cp .claude/skills/human-voice/SKILL.md ~/.claude/skills/human-voice/
```

Then it loads for any project — SMT, the trading bot, anything.

Invoke it explicitly with `/human-voice`, or just ask for an email, post or
reply and it should load on its own from the description.
