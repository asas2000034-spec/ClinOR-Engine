"""Regenerate the deterministic *synthetic* API examples. Run: python examples/create_demos.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
options = [
    {"option_id":"A", "label":"Synthetic intervention A", "benefit":75, "burden":20, "cost":15,
     "incompatible_with":["C"]},
    {"option_id":"B", "label":"Synthetic intervention B", "benefit":60, "burden":10, "cost":8},
    {"option_id":"C", "label":"Synthetic intervention C", "benefit":82, "burden":35, "cost":16,
     "incompatible_with":["A"]},
]

scen_options = [
    {"option_id":"A", "label":"High-variance scenario A", "benefit":80, "burden":0, "cost":2},
    {"option_id":"B", "label":"Stable scenario B", "benefit":60, "burden":0, "cost":2},
]
examples = {
    "mcda": {"mode":"sandbox", "method":"topsis", "options":options,
             "benefit_weight":2, "burden_weight":1, "cost_weight":1},
    "pareto": {"mode":"sandbox", "options":options},
    "scenarios": {"mode":"sandbox", "options":scen_options, "strategy":"maximin",
        "max_selections":1, "min_selections":1, "budget":3,
        "scenarios":[
            {"scenario_id":"high_demand", "probability":0.8, "payoffs":[
                {"option_id":"A", "benefit":95, "burden":0, "cost":2},
                {"option_id":"B", "benefit":60, "burden":0, "cost":2}]},
            {"scenario_id":"low_demand", "probability":0.2, "payoffs":[
                {"option_id":"A", "benefit":10, "burden":0, "cost":2},
                {"option_id":"B", "benefit":60, "burden":0, "cost":2}]}
        ]},
    "monte_carlo": {"mode":"sandbox", "simulations":2000, "seed":42,
       "options":[
           {"option_id":"A", "benefit_mean":70, "benefit_sd":12, "burden_mean":25, "burden_sd":8, "cost":12},
           {"option_id":"B", "benefit_mean":65, "benefit_sd":6, "burden_mean":15, "burden_sd":5, "cost":9}]},
    "markov": {"mode":"sandbox", "state_names":["state_1", "state_2"],
       "initial_distribution":[1,0], "cycles":10, "discount_rate":0.03,
       "policies":[
         {"policy_id":"policy_A", "transition":[[0.9,0.1],[0.1,0.9]],
          "reward_per_state":[10,4],"cost_per_state":[2,3]},
         {"policy_id":"policy_B", "transition":[[0.8,0.2],[0.2,0.8]],
          "reward_per_state":[9,4],"cost_per_state":[1,2]}]},
    "dynamic_programming": {"mode":"sandbox", "states":["active","complete"],
       "initial_state":"active", "horizon":5, "discount_factor":0.95,
       "actions":[
         {"state":"active","action":"complete_now","immediate_reward":5,
          "outcomes":[{"next_state":"complete","probability":1}]},
         {"state":"active","action":"wait","immediate_reward":2,
          "outcomes":[{"next_state":"active","probability":1}]},
         {"state":"complete","action":"maintain","immediate_reward":1,
          "outcomes":[{"next_state":"complete","probability":1}]}]},
    "queueing": {"mode":"sandbox", "arrival_rate":8,
       "service_rate_per_server":5, "servers":2, "rate_unit":"hour"},
    "cp_sat": {"mode":"sandbox", "options":options, "min_selections":1,
       "max_selections":2, "budget":25},
    "milp": {"mode":"sandbox", "options":options, "min_selections":1,
       "max_selections":2, "budget":25},
}
for key, data in examples.items():
    (ROOT / f"or_{key}.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
# Public synthetic examples; not derived from patient records.
(ROOT.parent / "clinor" / "static" / "or_examples.json").write_text(json.dumps(examples, indent=2) + "\n", encoding="utf-8")
