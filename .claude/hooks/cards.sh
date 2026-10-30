#!/usr/bin/env bash
# Card hooks. The ledger is hackathons/cards.md; its table is what this reads.
#   cards.sh session  SessionStart: the accounts marked "on file" or "unknown",
#                     and any next check due within 7 days (IST).
#   cards.sh prompt   UserPromptSubmit: a message that mentions a card or
#                     billing reminds Claude to update the ledger.
ledger="${CLAUDE_PROJECT_DIR:-.}/hackathons/cards.md"
[[ -f "$ledger" ]] || exit 0

case "$1" in
session)
  today=$(TZ=Asia/Kolkata date +%F)
  soon=$(TZ=Asia/Kolkata date -d '+7 days' +%F)
  # Columns: | Account | Used for | Card since | How | Guard | Next check | Status |
  rows=$(awk -F'|' '/^\| / && $2 !~ /^ *(Account|-+) *$/ {
      for (i = 2; i <= 8; i++) gsub(/^ +| +$/, "", $i)
      if ($8 == "on file" || $8 == "unknown") print $2 "|" $3 "|" $7 "|" $8
    }' "$ledger")
  [[ -z "$rows" ]] && exit 0
  accounts=() due=() short=()
  while IFS='|' read -r account used check status; do
    accounts+=("$account ($status)")
    when=${check:0:10}
    [[ "$when" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ && ! "$when" > "$soon" ]] || continue
    [[ "$when" < "$today" ]] && label="OVERDUE" || label="due"
    due+=("$account, $label $check")
    short+=("$account: $label ${when:5}")
  done <<< "$rows"
  list=$(IFS=';'; echo "${accounts[*]}" | sed 's/;/, /g')
  context="Card ledger (hackathons/cards.md): Jannet's card is on file or unknown at $list."
  if ((${#due[@]})); then
    checks=$(printf '%s\n' "${due[@]}")
    brief=$(printf '%s\n' "${short[@]}")
    jq -n --arg c "$context" --arg d "$checks" --arg b "$brief" '{
      systemMessage: ("Card check: " + ($b | rtrimstr("\n") | gsub("\n"; " · ")) + ". Details in hackathons/cards.md."),
      hookSpecificOutput: {
        hookEventName: "SessionStart",
        additionalContext: ($c + "\nCard checks due within 7 days. Mention them in your first reply; Jannet does the check and you record the result in the ledger:\n" + $d)
      }
    }'
  else
    jq -n --arg c "$context" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $c}}'
  fi
  ;;
prompt)
  prompt=$(jq -r '.prompt // empty')
  grep -Eiq '(credit|debit|visa|master|rupay|bank|my|her|the|a|your|new) card|card (on file|added|details|number|required|needed|charged|verification|check|hold|was|is)|payment (method|details|info)|billing|billed|\bcharged|top[ -]?up|pre-?auth|auto-?(pay|charge)|subscription|invoice|pay[ -]as[ -]you[ -]go|paid (plan|tier)|upgrade(d)? to paid|free trial|spending limit' <<< "$prompt" || exit 0
  jq -n '{
    systemMessage: "Card or billing mentioned: Claude will note it in hackathons/cards.md.",
    hookSpecificOutput: {
      hookEventName: "UserPromptSubmit",
      additionalContext: "This message mentions a card or billing. If a card was added, held, charged or removed on any account, or a sign-up, trial, credit claim or top-up needs one, add or update its row in hackathons/cards.md in this session (keep the columns; Next check starts with YYYY-MM-DD or reads none; Status is on file, unknown, removed or closed), and tell Jannet it is recorded. No card digits, account IDs or logins: the repo is public. If the message is not about a payment card (a share card, a portfolio card), ignore this."
    }
  }'
  ;;
esac
