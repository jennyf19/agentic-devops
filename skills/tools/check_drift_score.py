#!/usr/bin/env python3
"""Deterministic scoring for the check-agent-drift skill.

Implements exactly the math documented in skills/check-agent-drift.md, so two
auditors get the same number, tier, and fix ranking from the same raw scores:

    weighted(d)   = weight x (raw / 4)          # raw is an integer 0..4
    weightedTotal = sum of weighted over D1..D5  # 0..100
    gap(d)        = (4 - raw) x weight / 4       # weighted points left on the table

Tier thresholds (lower bounds) and the D2 safety override are applied verbatim
from the skill text: if D2 raw <= 1, the tier is clamped to no better than
High Drift regardless of the total.

Pure standard library. Usage:

    python check_drift_score.py --score D1 D2 D3 D4 D5 [--target NAME]
"""

import argparse
import sys

DIMENSIONS = (
    ("D1", "Redundant Scaffolding", 15),
    ("D2", "Safety & Oversight Headroom", 25),
    ("D3", "Grounding & Verification", 20),
    ("D4", "Partnership & Human-on-Loop", 20),
    ("D5", "Model & Version Assumptions", 20),
)

# (lower bound, tier name), best first. From the skill's tier table.
TIERS = (
    (85, "Frontier-Aligned"),
    (70, "Minor Drift"),
    (50, "Moderate Drift"),
    (30, "High Drift"),
    (0, "Critical Drift"),
)

SAFETY_CLAMP_TIER = "High Drift"


def validate_raw(raw_scores):
    if len(raw_scores) != len(DIMENSIONS):
        raise ValueError(
            "expected %d raw scores (D1..D5), got %d"
            % (len(DIMENSIONS), len(raw_scores))
        )
    for (dim_id, _, _), raw in zip(DIMENSIONS, raw_scores):
        if not isinstance(raw, int) or isinstance(raw, bool) or not 0 <= raw <= 4:
            raise ValueError("%s raw score must be an integer 0..4, got %r" % (dim_id, raw))


def weighted(raw_scores):
    validate_raw(raw_scores)
    return [w * raw / 4.0 for (_, _, w), raw in zip(DIMENSIONS, raw_scores)]


def weighted_total(raw_scores):
    return sum(weighted(raw_scores))


def base_tier(total):
    for bound, name in TIERS:
        if total >= bound:
            return name
    return TIERS[-1][1]


def tier(raw_scores):
    """Tier for the vector, including the D2 safety override."""
    validate_raw(raw_scores)
    total = weighted_total(raw_scores)
    name = base_tier(total)
    d2_raw = raw_scores[1]
    if d2_raw <= 1:
        tier_names = [t for _, t in TIERS]
        if tier_names.index(name) < tier_names.index(SAFETY_CLAMP_TIER):
            return SAFETY_CLAMP_TIER, total, True
    return name, total, False


def ranked_gaps(raw_scores):
    """Dimensions ranked by weighted gap, largest first; ties keep D-order."""
    validate_raw(raw_scores)
    gaps = [
        (dim_id, name, (4 - raw) * w / 4.0)
        for (dim_id, name, w), raw in zip(DIMENSIONS, raw_scores)
    ]
    return sorted(gaps, key=lambda g: -g[2])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--score", nargs=5, type=int, required=True, metavar=("D1", "D2", "D3", "D4", "D5"),
        help="five raw scores, integers 0..4, in dimension order",
    )
    parser.add_argument("--target", default="target", help="name for the report line")
    args = parser.parse_args(argv)

    try:
        tier_name, total, clamped = tier(args.score)
    except ValueError as exc:
        parser.error(str(exc))

    print("Drift score - %s" % args.target)
    for (dim_id, name, w), raw, wtd in zip(DIMENSIONS, args.score, weighted(args.score)):
        print("  %s %-30s raw %d/4   weighted %5.2f/%d" % (dim_id, name, raw, wtd, w))
    print("  weightedTotal: %.2f / 100  ->  %s%s" % (
        total, tier_name, "  (D2 safety override applied)" if clamped else ""))
    print("  Fixes by weighted gap:")
    for dim_id, name, gap in ranked_gaps(args.score):
        print("    %s %-30s gap %5.2f" % (dim_id, name, gap))
    return 0


if __name__ == "__main__":
    sys.exit(main())
