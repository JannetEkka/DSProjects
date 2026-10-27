#!/usr/bin/env bash
# SessionStart hook: shows Jannet each open reminder until its last day (IST).
# One reminder per line below: last day to show it (YYYY-MM-DD) | text.
# Delete a line once it's done.
today=$(TZ=Asia/Kolkata date +%F)
msgs=()
while IFS='|' read -r until text; do
  [[ -z "$until" || "$until" == \#* ]] && continue
  [[ "$today" > "$until" ]] && continue
  msgs+=("$text")
done <<'EOF'
2026-11-02|Rise of AI Agents (lablab): registration was not open on 10-20 (dates TBA). Check https://lablab.ai/ai-hackathons/ai-genesis-2026 and register when it opens; the online build is Oct 26 to Nov 2.
EOF
((${#msgs[@]})) || exit 0
printf '%s\n' "${msgs[@]}" | jq -Rs '{
  systemMessage: ("Reminder: " + (rtrimstr("\n") | gsub("\n"; " | "))),
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: ("Open reminders for Jannet. Mention them in your first reply. Do not check the pages yourself; Jannet checks them.\n" + .)
  }
}'
