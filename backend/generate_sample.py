from synthetic_testing.runners.pair_runner import PairRunner
from synthetic_testing.schemas.persona_spec import SyntheticPersonaSpec
from synthetic_testing.schemas.pair_spec import PairSpec
import yaml

with open("backend/synthetic_testing/pairs/anxious_avoidant.yaml") as f:
    pair_dict = yaml.safe_load(f)
    pair = PairSpec(**pair_dict)

with open(f"backend/synthetic_testing/personas/{pair.person_a}.yaml") as f:
    pa = SyntheticPersonaSpec(**yaml.safe_load(f))

with open(f"backend/synthetic_testing/personas/{pair.person_b}.yaml") as f:
    pb = SyntheticPersonaSpec(**yaml.safe_load(f))

runner = PairRunner(mode="sample_generation")
report = runner.run(pa, pb, pair, seed=42)

import shutil

report_path = f"backend/synthetic_testing/reports/{report['run_id']}.json"
shutil.copy(report_path, "frontend/public/sample-report.json")
print("Successfully generated and copied sample-report.json to frontend/public/")
