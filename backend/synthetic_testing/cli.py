import argparse
import sys
import yaml
import os

from synthetic_testing.schemas.persona_spec import SyntheticPersonaSpec
from synthetic_testing.schemas.pair_spec import PairSpec
from synthetic_testing.runners.pair_runner import PairRunner
from synthetic_testing.config import PERSONAS_DIR, PAIRS_DIR

def load_persona(persona_id: str) -> SyntheticPersonaSpec:
    path = os.path.join(PERSONAS_DIR, f"{persona_id}.yaml")
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return SyntheticPersonaSpec(**data)

def load_pair(pair_id: str) -> PairSpec:
    path = os.path.join(PAIRS_DIR, f"{pair_id}.yaml")
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return PairSpec(**data)

def main():
    parser = argparse.ArgumentParser(description="Synthetic Testing CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run-pair command
    run_pair_parser = subparsers.add_parser("run-pair")
    run_pair_parser.add_argument("--pair", required=True)
    run_pair_parser.add_argument("--mode", default="quick")
    run_pair_parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    if args.command == "run-pair":
        pair_spec = load_pair(args.pair)
        person_a = load_persona(pair_spec.person_a)
        person_b = load_persona(pair_spec.person_b)
        
        runner = PairRunner(mode=args.mode)
        runner.run(person_a, person_b, pair_spec, seed=args.seed)

if __name__ == "__main__":
    main()
