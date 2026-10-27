"""Prompts and the output schema for Muse Spark."""

LANGUAGES = {
    "en": "English",
    "hi": "Hindi (हिन्दी, Devanagari script)",
    "bn": "Bengali (বাংলা, Bengali script)",
}

READ = """Transcribe every piece of text in this image exactly as printed, in reading order, one printed line per line.
Rules:
- Copy characters exactly: numbers, punctuation, currency signs, capital letters, and the original script (English, Hindi, Bengali).
- Do not translate, correct, summarise, or add anything. Never guess a digit; if a character is unreadable, write [?].
- For a table, write one row per line with cells separated by " | ".
Reply with the transcription only."""

EXPLAIN = """You explain an official Indian letter to the person who received it. They may not read formal English or official Hindi.
You are given the letter's text, as read from a photo. Write in {language}, in plain words a person with little schooling understands.

Return JSON with:
- "kind": what this letter is, in a few words, in {language}.
- "summary": two short sentences in {language}: who sent it and what it wants.
- "points": the things the reader must know: what to pay, by when, what happens if they don't, what to do next. 3 to 7 points, most urgent first.

Each point has:
- "say": one or two short sentences in {language}.
- "quote": the exact words from the letter that this point rests on, copied character for character from the letter text (keep its language, spelling, numbers and punctuation). A quote is one passage of the letter, at most two lines.
- "topic": one of "amount", "deadline", "consequence", "action", "other".

Rules that a program will check before anything is shown:
- Every date and every number in "say" must appear in that point's "quote". Do not add, compute, round or convert numbers: no totals you added up, no "3 things", no day counts that aren't in the quote.
- Write dates as DD/MM/YYYY and amounts as ₹ followed by the amount exactly as in the letter, using 0-9 digits.
- One fact per point. If the letter is unclear about something, say so; never guess.
- Do not give legal or medical advice; say who to contact instead, if the letter names someone."""

REPAIR = """Some points failed the check that compares them against the letter. For each one, the reason is given.
Rewrite only those points so that each passes: the quote must be words copied exactly from the letter, and every date and number in "say" must be in that quote.
If a point cannot be supported by the letter's words, drop it.
Return the same JSON shape, with only the rewritten points in "points" (keep "kind" and "summary" as they were)."""

ANSWER = """The reader asked a question about this letter. Answer in {language} as points, with the same rules: each point quotes the letter's exact words, and every date and number you say must be in its quote.
If the letter doesn't answer the question, return one point whose "say" tells them that, in {language}, and whose "quote" is the passage closest to the question.
Question: {question}"""

POINTS_SCHEMA = {
    "title": "chithi_explanation",
    "type": "object",
    "additionalProperties": False,
    "required": ["kind", "summary", "points"],
    "properties": {
        "kind": {"type": "string"},
        "summary": {"type": "string"},
        "points": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["say", "quote", "topic"],
                "properties": {
                    "say": {"type": "string"},
                    "quote": {"type": "string"},
                    "topic": {"type": "string", "enum": ["amount", "deadline", "consequence", "action", "other"]},
                },
            },
        },
    },
}
