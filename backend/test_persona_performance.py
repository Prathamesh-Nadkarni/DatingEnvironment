"""
Baseline diagnostic: archetype pairs (Soulmates -> Polar Opposites) vs full compatibility pipeline.

Pipeline (see compatibility_engine.run_full_compatibility_report):
  - Static trait compatibility: values, conflict_style, emotional, practical, trust, autonomy (0-1 each)
  - 6 categories x up to 3 weighted scenarios each (18 total simulations max)
  - overall = 30% * (mean trait subscores * 100) + 70% * (weighted mean harmony scores)
             - 10 per flagged dealbreaker (harmony <= 40 on a dealbreaker scenario)
"""

import logging
import json
import random
import argparse
import sys
import os
from statistics import mean
from typing import Dict, Any, List

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(
    level=logging.INFO,
    format="%(name)s | %(message)s",
)

from intake_questions import INTAKE_SECTIONS
from persona_synthesis import PersonaEngine
from compatibility_engine import (
    run_full_compatibility_report,
    TRAIT_WEIGHT,
    SIMULATION_WEIGHT,
    DEALBREAKER_THRESHOLD,
    MAX_DEALBREAKER_PENALTY,
    SCENARIOS_PER_CATEGORY,
)

CATEGORY_ORDER: List[str] = [
    "family_dynamics",
    "autonomy_identity",
    "financial",
    "loyalty_trust",
    "parenting",
    "crisis_resilience",
]

CATEGORY_LABELS = {
    "family_dynamics":   "Family Dynamics",
    "financial":         "Financial Alignment",
    "autonomy_identity": "Autonomy & Identity",
    "parenting":         "Parenting & Commitment",
    "crisis_resilience": "Crisis Resilience",
    "loyalty_trust":     "Loyalty & Trust",
}

DEFAULT_MAX_TURNS = 4


def generate_calibrated_base():
    answers = {}
    for section in INTAKE_SECTIONS:
        for q in section["questions"]:
            q_id = q["id"]
            fmt = q["format"]
            if "scale" in fmt:
                answers[q_id] = 6
            elif fmt in ["multiple_choice", "forced_choice", "sjt"]:
                answers[q_id] = q["options"][0]["id"] if isinstance(q["options"][0], dict) else q["options"][0]
            elif fmt in ["text_input", "short_answer"]:
                answers[q_id] = "I value family harmony and tradition above all."
    return answers


def generate_variant(base: Dict[str, Any], similarity_ratio: float):
    variant = base.copy()
    keys = [k for k in base.keys() if not k.startswith("0.")]

    total = len(keys)
    to_change_count = int(total * (1 - similarity_ratio))
    change_keys = random.sample(keys, to_change_count)

    for k in change_keys:
        q_cfg = None
        for sec in INTAKE_SECTIONS:
            for q in sec["questions"]:
                if q["id"] == k:
                    q_cfg = q
                    break
        if not q_cfg:
            continue

        fmt = q_cfg["format"]
        if "scale" in fmt:
            variant[k] = max(1, 8 - base[k]) if "7" in fmt else max(1, 7 - base[k])
        elif fmt in ["multiple_choice", "forced_choice", "sjt"]:
            opts = q_cfg["options"]
            current = base[k]
            others = [
                o["id"] if isinstance(o, dict) else o
                for o in opts
                if (o["id"] if isinstance(o, dict) else o) != current
            ]
            if others:
                variant[k] = others[-1]
        elif fmt == "short_answer":
            variant[k] = "I prioritize individual autonomy and modern values."

    return variant


def compute_report_breakdown(report: Dict[str, Any]) -> Dict[str, Any]:
    tc = report["trait_compatibility"]
    trait_avg = mean(tc.values())
    dim_scores = list(report["dimensional_scores"].values())
    sim_avg = mean(dim_scores) if dim_scores else 0.0
    n_db = len(report.get("dealbreakers") or [])
    raw = TRAIT_WEIGHT * (trait_avg * 100) + SIMULATION_WEIGHT * sim_avg
    penalty = n_db * 10
    return {
        "trait_avg": trait_avg,
        "sim_avg": sim_avg,
        "raw_overall": raw,
        "dealbreaker_penalty": penalty,
        "formula_line": (
            f"raw = {TRAIT_WEIGHT:.0%}x({trait_avg:.3f}x100) + {SIMULATION_WEIGHT:.0%}x({sim_avg:.1f}) "
            f"= {raw:.1f}  |  -{penalty} dealbreaker -> {report['overall_compatibility_score']}/100"
        ),
    }


def print_algorithm_banner(max_turns: int) -> None:
    print("\n" + "=" * 78)
    print("  MIROFISH COMPATIBILITY BASELINE (test_persona_performance.py)")
    print("=" * 78)
    print(f"  Formula: overall = {TRAIT_WEIGHT:.0%} x trait_mean x 100 + {SIMULATION_WEIGHT:.0%} x mean(harmony)")
    print(f"           minus 8 per dealbreaker (capped at -{MAX_DEALBREAKER_PENALTY}); triggers when marked scenario & harmony <= {DEALBREAKER_THRESHOLD}.")
    print(f"  Simulations: 6 categories x up to {SCENARIOS_PER_CATEGORY} scenarios each, max_turns={max_turns}.")
    print(f"  Trait dimensions: values, conflict_style, emotional, practical, trust, autonomy.")
    print(f"  Random seed: fixed at 42 for reproducibility.")
    print("=" * 78)


def print_report(name: str, ratio: float, report: Dict[str, Any]) -> None:
    bar_width = 30

    def bar(score: int) -> str:
        filled = int(score / 100 * bar_width)
        return "[" + "#" * filled + "-" * (bar_width - filled) + f"] {score:3d}/100"

    def trait_bar(val: float) -> str:
        filled = int(val * bar_width)
        return "[" + "#" * filled + "-" * (bar_width - filled) + f"] {val:.0%}"

    br = compute_report_breakdown(report)

    print(f"\n{'=' * 78}")
    print(f"  CASE: {name}  |  Answer overlap vs base: ~{int(ratio * 100)}%")
    print(f"{'=' * 78}")

    print(f"\n  OVERALL COMPATIBILITY  {bar(report.get('overall_compatibility_score', report.get('overall_score', 0)))}")
    print(f"  {br['formula_line']}")

    if report.get("flagged_dealbreakers", []):
        print("\n  DEALBREAKER TRIGGERED:")
        for db in report.get("flagged_dealbreakers", []):
            print(f"    ! {db}")

    print("\n  -- Static trait compatibility (no simulation) --")
    tc = report["trait_compatibility"]
    print(f"    Trait mean (0-1): {br['trait_avg']:.3f}")
    print(f"    Values           {trait_bar(tc['values'])}")
    print(f"    Conflict style   {trait_bar(tc['conflict_style'])}")
    print(f"    Emotional        {trait_bar(tc['emotional'])}")
    print(f"    Practical        {trait_bar(tc['practical'])}")
    print(f"    Trust            {trait_bar(tc['trust'])}")
    print(f"    Autonomy         {trait_bar(tc['autonomy'])}")

    print(f"\n  -- Per-category simulation (up to {SCENARIOS_PER_CATEGORY} scenarios each, weighted) --")
    details = report["dimensional_details"]
    for cat in CATEGORY_ORDER:
        if cat not in report["dimensional_scores"]:
            continue
        cat_score = report["dimensional_scores"][cat]
        label = CATEGORY_LABELS.get(cat, cat)
        cat_details = details.get(cat, [])

        print(f"\n    [{label}]  Weighted avg: {bar(cat_score)}")
        for i, d in enumerate(cat_details, 1):
            sid = d.get("scenario_id", "?")
            title = d.get("scenario_title", "")
            score = d.get("harmony_score", 0)
            traj = (d.get("trajectory") or "").upper()
            inf = (d.get("inference") or "").strip()
            w = d.get("weight", 1)
            db = " [DEALBREAKER]" if d.get("dealbreaker") else ""
            print(f"      {i}. {title} (id={sid}, w={w}{db})")
            print(f"         harmony={score}  trajectory={traj}")
            if inf:
                print(f"         inference: {inf}")

    print(f"\n  -- Summary axes --")
    print(f"    Top friction: {CATEGORY_LABELS.get(report.get('top_friction_axis', 'None'), report.get('top_friction_axis', 'None'))}")
    print(f"    Top strength: {CATEGORY_LABELS.get(report.get('top_strength_axis', 'None'), report.get('top_strength_axis', 'None'))}")
    print(f"\n  Verdict:\n    {report.get('verdict', report.get('inference', 'No verdict generated'))}")
    print()


def run_diagnostic(max_turns: int = DEFAULT_MAX_TURNS) -> Dict[str, Any]:
    random.seed(42)

    base_answers = generate_calibrated_base()
    print_algorithm_banner(max_turns)

    test_cases = [
        ("Soulmates (100% Aligned)", 1.0),
        ("Good Match (50% Aligned)", 0.5),
        ("Unlikely Pair (25% Aligned)", 0.25),
        ("Polar Opposites (0% Aligned)", 0.0),
    ]

    all_reports: Dict[str, Dict[str, Any]] = {}

    for name, ratio in test_cases:
        user_b_answers = generate_variant(base_answers, ratio)

        engine_a = PersonaEngine()
        engine_b = PersonaEngine()

        persona_a = engine_a.synthesize(base_answers)
        persona_b = engine_b.synthesize(user_b_answers)

        report = run_full_compatibility_report(
            persona_a,
            persona_b,
            max_turns=max_turns,
        )
        all_reports[name] = report
        print_report(name, ratio, report)

    print("\n" + "=" * 78)
    print("  BASELINE SANITY CHECKS (expected with seed=42; middle tiers may cross)")
    print("=" * 78)
    soulmates = all_reports["Soulmates (100% Aligned)"].get("overall_compatibility_score", all_reports["Soulmates (100% Aligned)"].get("overall_score", 0))
    goodmatch = all_reports["Good Match (50% Aligned)"].get("overall_compatibility_score", all_reports["Good Match (50% Aligned)"].get("overall_score", 0))
    unlikely = all_reports["Unlikely Pair (25% Aligned)"].get("overall_compatibility_score", all_reports["Unlikely Pair (25% Aligned)"].get("overall_score", 0))
    polar = all_reports["Polar Opposites (0% Aligned)"].get("overall_compatibility_score", all_reports["Polar Opposites (0% Aligned)"].get("overall_score", 0))

    print(f"  Scores: Soulmates={soulmates}  GoodMatch={goodmatch}  UnlikelyPair={unlikely}  PolarOpposites={polar}")
    checks = [
        ("Soulmates >= PolarOpposites (more aligned -> not worse)", soulmates >= polar, f"{soulmates} vs {polar}"),
        ("Soulmates is strict maximum", soulmates == max(soulmates, goodmatch, unlikely, polar), f"max={max(soulmates, goodmatch, unlikely, polar)}"),
        ("Score spread >= 10 (differentiation)", soulmates - polar >= 10, f"spread={soulmates - polar}"),
    ]
    for label, ok, detail in checks:
        status = "PASS" if ok else "WARN"
        print(f"  [{status}] {label}  ({detail})")
    print()

    return all_reports


def main():
    parser = argparse.ArgumentParser(description="Mirofish archetype compatibility baseline")
    parser.add_argument(
        "--max-turns",
        type=int,
        default=DEFAULT_MAX_TURNS,
        help=f"Simulation depth per scenario (default {DEFAULT_MAX_TURNS})",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        help="Path to save the reports in JSON format",
    )
    args = parser.parse_args()

    all_reports = run_diagnostic(args.max_turns)

    if args.json_output:
        with open(args.json_output, "w") as f:
            json.dump(all_reports, f, indent=2)
        print(f"\n  [JSON] Results saved to {args.json_output}")


if __name__ == "__main__":
    main()
