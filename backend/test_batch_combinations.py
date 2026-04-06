"""
Batch baseline: many participants, all mutually viable pairs, full compatibility report per pair.

Uses the same pipeline as test_persona_performance.run_diagnostic():
  run_full_compatibility_report(prompt_a, prompt_b, max_turns=...)

Default logging is WARNING so per-turn simulation logs stay quiet; summary prints to stdout.
Use:  python test_batch_combinations.py
       python test_batch_combinations.py --verbose   (INFO logs from engines)
"""

import argparse
import json
import logging
import random
import sys
import os
from statistics import mean, stdev
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass, asdict

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from test_persona_performance import (
    generate_calibrated_base,
    generate_variant,
    CATEGORY_ORDER,
    CATEGORY_LABELS,
    compute_report_breakdown,
    DEFAULT_MAX_TURNS,
)
from persona_synthesis import PersonaEngine
from compatibility_engine import (
    run_full_compatibility_report,
    TRAIT_WEIGHT,
    SIMULATION_WEIGHT,
    DEALBREAKER_THRESHOLD,
    MAX_DEALBREAKER_PENALTY,
    SCENARIOS_PER_CATEGORY,
)


def _short_verdict(verdict: str, max_len: int = 120) -> str:
    s = " ".join(verdict.split())
    if len(s) <= max_len:
        return s
    return s[: max_len - 3] + "..."


def _print_pair_block(title: str, p1: "Participant", p2: "Participant", rep: Dict[str, Any]) -> None:
    br = compute_report_breakdown(rep)
    print(f"\n  {'-' * 74}")
    print(f"  {title}:  {p1.p_id}  +  {p2.p_id}")
    print(f"    similarity_index: {p1.ratio} / {p2.ratio}  |  prefs: {p1.preference} / {p2.preference}")
    print(f"    OVERALL {rep['overall_score']}/100  |  {br['formula_line']}")
    if rep.get("dealbreakers"):
        print(f"    DEALBREAKERS: {rep['dealbreakers']}")

    tc = rep["trait_compatibility"]
    print(
        f"    Traits (0-1): values={tc['values']:.2f}  conflict={tc['conflict_style']:.2f}  "
        f"emotional={tc['emotional']:.2f}  practical={tc['practical']:.2f}  "
        f"trust={tc['trust']:.2f}  autonomy={tc['autonomy']:.2f}"
    )

    print("    Dimensions:")
    for cat in CATEGORY_ORDER:
        if cat not in rep["dimensional_scores"]:
            continue
        cat_score = rep["dimensional_scores"][cat]
        lab = CATEGORY_LABELS.get(cat, cat)
        cat_details = rep["dimensional_details"].get(cat, [])
        print(f"      {lab:22s} {cat_score:3d}/100  (avg of {len(cat_details)} scenario(s))")
        for d in cat_details:
            sid = d.get("scenario_id", "?")
            traj = (d.get("trajectory") or "").upper()
            h = d.get("harmony_score", 0)
            db = " *DB*" if d.get("dealbreaker") else ""
            inf = (d.get("inference") or "").strip()
            print(f"        - {sid}: {h}/100 {traj}{db}")
            if inf:
                print(f"          {inf}")

    print(f"    Friction: {CATEGORY_LABELS.get(rep['top_friction_axis'], rep['top_friction_axis'])}")
    print(f"    Strength: {CATEGORY_LABELS.get(rep['top_strength_axis'], rep['top_strength_axis'])}")
    print(f"    Verdict: {rep['verdict']}")


@dataclass
class Participant:
    p_id: str
    gender: str
    preference: str
    ratio: float
    system_prompt: str = ""
    answers: Dict[str, Any] = None

    def __post_init__(self):
        if self.answers is None:
            self.answers = {}

    def init_persona(self, base_answers: Dict[str, Any]):
        self.answers = generate_variant(base_answers, self.ratio)
        engine = PersonaEngine()
        persona = engine.synthesize(self.answers)
        self.system_prompt = persona["system_prompt"]

    def __repr__(self):
        return f"{self.p_id}({self.gender},{self.preference})"


def generates_participants() -> List[Participant]:
    participants = []

    m_prefs = ["hetero"] * 6 + ["homo"] * 3 + ["bi"] * 3
    for i in range(12):
        ratio = round(random.uniform(0.1, 1.0), 2)
        p = Participant(f"M{i+1:02d}", "M", m_prefs[i], ratio)
        participants.append(p)

    f_prefs = ["hetero"] * 4 + ["homo"] * 2 + ["bi"] * 2
    for i in range(8):
        ratio = round(random.uniform(0.1, 1.0), 2)
        p = Participant(f"F{i+1:02d}", "F", f_prefs[i], ratio)
        participants.append(p)

    return participants


def is_match(p1: Participant, p2: Participant) -> bool:
    if p1.p_id == p2.p_id:
        return False

    def matches(chooser: Participant, target: Participant) -> bool:
        if chooser.preference == "hetero":
            return chooser.gender != target.gender
        if chooser.preference == "homo":
            return chooser.gender == target.gender
        if chooser.preference == "bi":
            return True
        return False

    return matches(p1, p2) and matches(p2, p1)


def run_batch_simulation(
    max_turns: int = DEFAULT_MAX_TURNS,
    verbose: bool = False,
    detail_sample: int = 3,
) -> List[Dict[str, Any]]:
    log_level = logging.INFO if verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(name)s | %(message)s", force=True)

    random.seed(42)

    print("=" * 78)
    print(" MIROFISH BATCH MATCHMAKING BASELINE (test_batch_combinations.py)")
    print("=" * 78)
    print(f"  Pipeline: run_full_compatibility_report (trait {TRAIT_WEIGHT:.0%} + sim {SIMULATION_WEIGHT:.0%})")
    print(f"  Dealbreaker: -8pts each (cap -{MAX_DEALBREAKER_PENALTY}) when marked scenario & harmony <= {DEALBREAKER_THRESHOLD}.")
    print(f"  Scenarios/category: up to {SCENARIOS_PER_CATEGORY}  |  max_turns={max_turns}")
    print(f"  Trait dimensions: values, conflict_style, emotional, practical, trust, autonomy")
    print(f"  random.seed(42)  |  engine log level: {'INFO' if verbose else 'WARNING'}")
    print("=" * 78)

    print("\n[1] Generating participants from calibrated base...")
    base_answers = generate_calibrated_base()
    participants = generates_participants()
    for p in participants:
        p.init_persona(base_answers)
        print(f"    {p!r}  similarity_index={p.ratio}")

    print("\n[2] Mutually viable pairs (preference + gender rules)...")
    valid_pairs: List[Tuple[Participant, Participant]] = []
    seen = set()
    for p1 in participants:
        for p2 in participants:
            pair_id = tuple(sorted([p1.p_id, p2.p_id]))
            if pair_id not in seen and is_match(p1, p2):
                valid_pairs.append((p1, p2))
                seen.add(pair_id)

    print(f"    Pairs: {len(valid_pairs)} (from {len(participants)} participants)")

    total_sims = len(valid_pairs) * 6 * SCENARIOS_PER_CATEGORY
    print(f"\n[3] Running full compatibility (~{total_sims} simulations total)...")
    results: List[Dict[str, Any]] = []

    for idx, (p1, p2) in enumerate(valid_pairs):
        sys.stdout.write(f"\r    Progress {idx + 1}/{len(valid_pairs)}  {p1.p_id}+{p2.p_id}   ")
        sys.stdout.flush()

        report = run_full_compatibility_report(
            p1.system_prompt,
            p2.system_prompt,
            max_turns=max_turns,
        )
        results.append({
            "pair": (p1, p2),
            "report": report,
        })

    print()

    results.sort(key=lambda x: x["report"]["overall_score"], reverse=True)
    scores = [r["report"]["overall_score"] for r in results]
    db_pairs = sum(1 for r in results if r["report"]["dealbreakers"])

    print("\n[4] Aggregate statistics")
    print(f"    overall_score: min={min(scores)}  max={max(scores)}  mean={mean(scores):.1f}", end="")
    if len(scores) > 1:
        print(f"  stdev={stdev(scores):.1f}")
    else:
        print()
    print(f"    pairs with >= 1 dealbreaker flag: {db_pairs} / {len(results)}")

    hetero_hetero = sum(
        1 for a, b in valid_pairs
        if a.preference == "hetero" and b.preference == "hetero"
    )
    print(f"    hetero-hetero pairs in pool: {hetero_hetero}")

    # Category-level breakdown across all pairs
    print("\n    Category score distribution (across all pairs):")
    for cat in CATEGORY_ORDER:
        cat_scores = [r["report"]["dimensional_scores"].get(cat, 0) for r in results]
        if cat_scores:
            lab = CATEGORY_LABELS.get(cat, cat)
            print(
                f"      {lab:22s}  min={min(cat_scores):3d}  max={max(cat_scores):3d}  "
                f"mean={mean(cat_scores):.1f}  stdev={stdev(cat_scores):.1f}" if len(cat_scores) > 1 else
                f"      {lab:22s}  single={cat_scores[0]}"
            )

    n = min(detail_sample, len(results))
    print(f"\n[5] TOP {n} matches (compact)")
    print("-" * 78)
    for i, res in enumerate(results[:n], start=1):
        p1, p2 = res["pair"]
        rep = res["report"]
        print(
            f"  #{i:2d}  {p1.p_id}+{p2.p_id}  overall={rep['overall_score']:3d}  "
            f"friction={rep['top_friction_axis'][:12]:12s}  "
            f"{_short_verdict(rep['verdict'])}"
        )

    print(f"\n[6] BOTTOM {n} matches (compact)")
    print("-" * 78)
    for i, res in enumerate(results[-n:], start=len(results) - n + 1):
        p1, p2 = res["pair"]
        rep = res["report"]
        print(
            f"  #{i:3d}  {p1.p_id}+{p2.p_id}  overall={rep['overall_score']:3d}  "
            f"friction={rep['top_friction_axis'][:12]:12s}  "
            f"{_short_verdict(rep['verdict'])}"
        )

    print(f"\n[7] Detailed blocks — top {n} and bottom {n}")
    print("=" * 78)
    for i, res in enumerate(results[:n], start=1):
        p1, p2 = res["pair"]
        _print_pair_block(f"TOP #{i}", p1, p2, res["report"])

    for i, res in enumerate(results[-n:], start=len(results) - n + 1):
        p1, p2 = res["pair"]
        _print_pair_block(f"BOTTOM #{i}", p1, p2, res["report"])

    print("\n" + "=" * 78)
    print("  Batch run complete.")
    print("=" * 78)

    return results


def main():
    parser = argparse.ArgumentParser(description="Mirofish batch compatibility baseline")
    parser.add_argument(
        "--max-turns", type=int, default=DEFAULT_MAX_TURNS,
        help=f"Simulation depth per scenario (default {DEFAULT_MAX_TURNS})",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable INFO logging from simulation/evaluation/compatibility modules",
    )
    parser.add_argument(
        "--detail-sample", type=int, default=3,
        help="How many top and bottom pairs get full dimensional + inference blocks",
    )
    parser.add_argument(
        "--smoke-archetype", action="store_true",
        help="Run Twins case from test_persona_performance after batch (sanity check)",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        help="Path to save the batch results in JSON format",
    )
    args = parser.parse_args()

    results = run_batch_simulation(
        max_turns=args.max_turns,
        verbose=args.verbose,
        detail_sample=max(1, args.detail_sample),
    )

    if args.json_output:
        # Convert Participants to dicts for JSON serialization
        serializable_results = []
        for res in results:
            p1, p2 = res["pair"]
            serializable_results.append({
                "p1": asdict(p1),
                "p2": asdict(p2),
                "report": res["report"]
            })
        with open(args.json_output, "w") as f:
            json.dump(serializable_results, f, indent=2)
        print(f"\n  [JSON] Results saved to {args.json_output}")

    if args.smoke_archetype:
        from test_persona_performance import run_diagnostic
        print("\n[SMOKE] Running test_persona_performance.run_diagnostic() ...\n")
        run_diagnostic(max_turns=args.max_turns)


if __name__ == "__main__":
    main()
