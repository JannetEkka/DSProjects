#!/usr/bin/env bash
# SessionStart hook: shows Jannet each open reminder until its last day (IST).
# One reminder per line below: [first day..]last day to show it (YYYY-MM-DD) | text.
# A first day is optional: 2026-11-29..2026-12-06|text shows from Nov 29 to Dec 6.
# Delete a line once it's done.
today=$(TZ=Asia/Kolkata date +%F)
msgs=()
while IFS='|' read -r until text; do
  [[ -z "$until" || "$until" == \#* ]] && continue
  from=""
  if [[ "$until" == *..* ]]; then from=${until%%..*}; until=${until##*..}; fi
  [[ -n "$from" && "$today" < "$from" ]] && continue
  [[ "$today" > "$until" ]] && continue
  msgs+=("$text")
done <<'EOF'
2026-11-29..2026-12-06|Deloitte pay check: did your CA send the income tax portal login? Open AIS / Form 26AS for FY 2021-22 and FY 2022-23 and send Claude the gross salary from Deloitte for each year, so we can work out your variable pay. Remove this line once done.
2026-12-01..2026-12-07|HackCulture Adaptive Challenge: details go live Dec 1. Paste the event page (rules, dates, team size, prizes) into a session so it goes into hackathons/november-2026.md.
EOF
((${#msgs[@]})) || exit 0
printf '%s\n' "${msgs[@]}" | jq -Rs '{
  systemMessage: ("Reminder: " + (rtrimstr("\n") | gsub("\n"; " | "))),
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: ("Open reminders for Jannet. Mention them in your first reply. Do not check the pages yourself; Jannet checks them.\n" + .)
  }
}'
