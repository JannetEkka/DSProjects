# Yatra Test Automation Framework: a hybrid Selenium framework

**Personal project, Feb 16–22, 2024** (after Deloitte; the CPSAT certification was 2022).
**Code:** [github.com/JannetEkka/python-automation](https://github.com/JannetEkka/python-automation) (folder `Yatra/`)

## The 30-second version
A **hybrid (data-driven + Page Object Model) Selenium framework in Python** for yatra.com's flight search: open the site, set from/to/date, search, filter by number of stops, and verify every result has that many stops. Cross-browser (Edge, Chrome, Firefox), test data from external files (`ddt` + OpenPyXL), PyTest with HTML reports, screenshots on failure, logs, and **Jenkins integration** (Feb 22: "failures fixed + integrated Jenkins").

This is the bridge to my Deloitte work: four years of Selenium and Katalon automation for Fortune 500 clients, and a 6-person QA team.

## The four FDE angles
1. **Architecture:** POM (`pages/`) separates locators and page actions from tests (`testcases/`), so a UI change touches one file. A data-driven layer (`testdata/` + `ddt`) means new routes are rows, not code. `base/` and `conftest.py` hold driver setup and fixtures; `utilities/` holds logging and Excel helpers. Why hybrid: maintainability (POM) plus coverage per test (data-driven).
2. **Data & security:** no credentials (search without login, by scope). In a client setting, test credentials go in a secret store or CI variables, never in the data files.
3. **Reliability (the core of test automation):** screenshots and logs on failure, explicit waits rather than sleeps (to verify in the code if asked), cross-browser runs, Jenkins for scheduled and triggered runs. The Feb 22 commit fixed real failures before the Jenkins integration.
4. **Evaluation:** test reports (pass/fail per case, coverage of the in-scope flows). The measured impact numbers on my résumé (**83% faster execution, 75% less manual analysis time**) come from **Deloitte**, not this project. Don't mix them up.

## Sources
`Yatra/README.md` (test strategy, scope, packages, focus areas), folder structure, git log Feb 16–22, 2024.
