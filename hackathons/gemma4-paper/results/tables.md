## Checker control

Tasks tried: 114. Reference patch passes and empty patch fails here: 68.

| Repository | Tried | Valid here |
|---|---|---|
| Textualize/rich | 44 | 39 |
| encode/httpx | 1 | 0 |
| fastapi/fastapi | 62 | 29 |
| psf/requests | 7 | 0 |

Harness-error tasks (left out of every comparison): 0 []

## Main comparison: json vs text (n = 68 tasks)

| | `json` | `text` |
|---|---|---|
| Tasks fixed | 3 of 68 | 3 of 68 |
| Malformed turns | 30 of 2403 | 4 of 637 |
| Turns cut off at the output cap | 23 | 141 |
| Turns with more than one action written | 0 | 153 |
| Output tokens spent in turns cut off at the cap | 141312 of 888773 | 866304 of 1099072 |
| Model seconds spent in turns cut off at the cap | 6422 of 43224 | 40671 of 51807 |
| Tasks with at least one turn cut off at the cap | 19 | 65 |
| Turns with no thinking text | 1442 of 2403 | 2 of 637 |
| Thinking characters per turn (median) | 0 | 786 |
| Turns that changed the workspace | 74 | 31 |
| Turns that ran python or pytest | 79 | 26 |
| Runs that submitted | 1 | 2 |
| Runs stopped by the time limit | 35 | 65 |
| Runs stopped by the turn limit | 32 | 0 |
| Runs that left a patch | 25 | 18 |
| Turns per task (median / mean) | 45 / 35.3 | 7.5 / 9.4 |
| Agent seconds per task (median / mean) | 900 / 683 | 902 / 897 |
| Output tokens per turn (mean) | 370 | 1725 |
| Output tokens per task (mean) | 13086 | 16344 |

- `json` vs `text`: both 1, only `json` 2, only `text` 2, neither 63; exact two-sided sign test on the 4 disagreements: p = 1.000

Why unfixed runs failed (fixed rules, in order):

| Failure type | `json` | `text` |
|---|---|---|
| no_patch | 43 | 50 |
| stuck_on_format | 0 | 0 |
| out_of_budget_with_patch | 22 | 14 |
| submitted_tests_fail | 0 | 1 |

Malformed turns by reason: `json`: {'no_tool_call': 7, 'cut_off_at_max_tokens': 23}; `text`: {'cut_off_at_max_tokens': 4}

By repository (fixed / tasks): Textualize/rich: `json` 1/39, `text` 0/39; fastapi/fastapi: `json` 2/29, `text` 3/29

Most used command words: `json`: [('grep', 1277), ('cat', 518), ('sed', 353), ('ls', 88), ('python3', 67), ('find', 47)]; `text`: [('grep', 315), ('cat', 126), ('sed', 111), ('ls', 40), ('python3', 24), ('find', 10)]

## Tasks run in all three arms (n = 68 tasks)

| | `json` | `text` | `text_stop` |
|---|---|---|---|
| Tasks fixed | 3 of 68 | 3 of 68 | 11 of 68 |
| Malformed turns | 30 of 2403 | 4 of 637 | 7 of 1380 |
| Turns cut off at the output cap | 23 | 141 | 7 |
| Turns with more than one action written | 0 | 153 | 0 |
| Output tokens spent in turns cut off at the cap | 141312 of 888773 | 866304 of 1099072 | 43008 of 1267187 |
| Model seconds spent in turns cut off at the cap | 6422 of 43224 | 40671 of 51807 | 1602 of 55262 |
| Tasks with at least one turn cut off at the cap | 19 | 65 | 7 |
| Turns with no thinking text | 1442 of 2403 | 2 of 637 | 40 of 1380 |
| Thinking characters per turn (median) | 0 | 786 | 1108 |
| Turns that changed the workspace | 74 | 31 | 99 |
| Turns that ran python or pytest | 79 | 26 | 98 |
| Runs that submitted | 1 | 2 | 3 |
| Runs stopped by the time limit | 35 | 65 | 65 |
| Runs stopped by the turn limit | 32 | 0 | 0 |
| Runs that left a patch | 25 | 18 | 34 |
| Turns per task (median / mean) | 45 / 35.3 | 7.5 / 9.4 | 19 / 20.3 |
| Agent seconds per task (median / mean) | 900 / 683 | 902 / 897 | 902 / 890 |
| Output tokens per turn (mean) | 370 | 1725 | 918 |
| Output tokens per task (mean) | 13086 | 16344 | 18712 |

- `json` vs `text`: both 1, only `json` 2, only `text` 2, neither 63; exact two-sided sign test on the 4 disagreements: p = 1.000
- `json` vs `text_stop`: both 2, only `json` 1, only `text_stop` 9, neither 56; exact two-sided sign test on the 10 disagreements: p = 0.021
- `text` vs `text_stop`: both 3, only `text` 0, only `text_stop` 8, neither 57; exact two-sided sign test on the 8 disagreements: p = 0.008

Why unfixed runs failed (fixed rules, in order):

| Failure type | `json` | `text` | `text_stop` |
|---|---|---|---|
| no_patch | 43 | 50 | 34 |
| stuck_on_format | 0 | 0 | 0 |
| out_of_budget_with_patch | 22 | 14 | 23 |
| submitted_tests_fail | 0 | 1 | 0 |

Malformed turns by reason: `json`: {'no_tool_call': 7, 'cut_off_at_max_tokens': 23}; `text`: {'cut_off_at_max_tokens': 4}; `text_stop`: {'cut_off_at_max_tokens': 7}

By repository (fixed / tasks): Textualize/rich: `json` 1/39, `text` 0/39, `text_stop` 6/39; fastapi/fastapi: `json` 2/29, `text` 3/29, `text_stop` 5/29

Most used command words: `json`: [('grep', 1277), ('cat', 518), ('sed', 353), ('ls', 88), ('python3', 67), ('find', 47)]; `text`: [('grep', 315), ('cat', 126), ('sed', 111), ('ls', 40), ('python3', 24), ('find', 10)]; `text_stop`: [('grep', 615), ('sed', 299), ('cat', 280), ('python3', 83), ('ls', 50), ('pytest', 15)]

Task ids in the main comparison: fastapi_11194, fastapi_13537, fastapi_13920, fastapi_14258, fastapi_14301, fastapi_14306, fastapi_14372, fastapi_14419, fastapi_14448, fastapi_14458, fastapi_14463, fastapi_14479, fastapi_14487, fastapi_14492, fastapi_14616, fastapi_14786, fastapi_14794, fastapi_14873, fastapi_14986, fastapi_15280, fastapi_15588, fastapi_15589, fastapi_15661, fastapi_15800, fastapi_5077, fastapi_5624, fastapi_9425, fastapi_9555, fastapi_9753, rich_2725, rich_2943, rich_3006, rich_3043, rich_3052, rich_3061, rich_3063, rich_3067, rich_3105, rich_3180, rich_3278, rich_3454, rich_3468, rich_3470, rich_3471, rich_3472, rich_3506, rich_3518, rich_3521, rich_3535, rich_3675, rich_3676, rich_3718, rich_3777, rich_3882, rich_3894, rich_3905, rich_3930, rich_3934, rich_3935, rich_3938, rich_3942, rich_3944, rich_3953, rich_4070, rich_4075, rich_4076, rich_4077, rich_4079
