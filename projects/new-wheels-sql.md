# New-Wheels Performance Analytics: SQL business intelligence for a vehicle-resale company

**PGP in AI/ML (UT Austin McCombs), Jul – Aug 2024.** Notebook in [`New_Wheels_Performance_Analytics_SQL/`](../New_Wheels_Performance_Analytics_SQL/).

## The 30-second version
A quarterly business review for a vehicle-resale company whose sales and customer sentiment were falling: customer distribution by state, average feedback by quarter, top vehicle makers by customer, orders and **revenue quarter over quarter (QoQ % change)**, revenue vs order correlation, shipping and discount analysis, and a KPI view. The README reports **994 customers** and **total revenue of $1.25B** (I couldn't re-derive those here: the data file in the repo is a Git LFS pointer, so check the notebook before quoting them).

## The four FDE angles
1. **Architecture:** SQL (MySQL in the course) for the queries, a notebook for visualisation. Why SQL first: the questions are aggregations and window functions (QoQ change with `LAG`), which is what a warehouse does best. A BI tool on top is the production version.
2. **Data & security:** customer and order data with locations. In a client deployment, row-level access by region and masking of customer identifiers in the BI layer.
3. **Reliability:** a scheduled refresh; data-quality checks on late or duplicate orders before the KPIs move.
4. **Evaluation:** KPI definitions agreed with the business (what counts as revenue: before or after discount?) matter more than the queries. That's the client-delivery skill this exercise practises.

## Sources
`New_Wheels_Performance_Analytics_SQL/README.md` (analyses, 994 customers, $1.25B, 98% "good feedback" in one KPI); notebook output table headers (QoQ revenue, orders, feedback by quarter).
