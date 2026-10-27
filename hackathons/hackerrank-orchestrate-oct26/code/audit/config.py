"""Tunable constants of the audit engine, in one place.

Every value here is a modelling choice, not a fact about one case; the timing values are only upper
bounds and support thresholds - the regularities themselves are learned from the data at run time."""

#: Hours before `reported_at` in which a request's deletion workflow runs its account job.
WORKFLOW_WINDOW_H = 3.0

#: The data catalog registers a business artifact (screenshot / PDF) at most this many seconds after
#: capture; used to pair an artifact with the resource its catalog entry names.
CATALOG_MEDIA_WINDOW_S = 1800

#: How far after its account job a workflow may still emit events (lattice learning and matching).
LATTICE_HORIZON_S = 5 * 3600

#: Longest spacing considered between two consecutive links of one policy-action chain.
CHAIN_MAX_GAP_S = 1200

#: Owner-attributed observations needed before a learned regularity (lattice band, chain gap,
#: single-instance category) is trusted.
MIN_SUPPORT = 10

#: A chain gap is kept only if at least this share of same-owner pairs within +-CHAIN_SHARP_WINDOW_S
#: seconds of it fall exactly on it (blurred timing => no chain is learned).
CHAIN_SHARPNESS = 0.8
CHAIN_SHARP_WINDOW_S = 3

#: Widest phase band (seconds) a lattice template may have; periods are searched from high to low.
LATTICE_MAX_BAND_S = 2
LATTICE_PERIODS = range(120, 9, -1)
