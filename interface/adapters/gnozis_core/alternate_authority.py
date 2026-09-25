#!/usr/bin/env python3
"""Adversarial alternate-authority probe for deterministic Select."""
from __future__ import annotations
import argparse, hashlib, json, subprocess
from pathlib import Path
from gnosis.core.budget import Budget
from gnosis.core.evolution import Engine
from gnosis.core.types import Candidate, State

def digest(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,default=str,separators=(",",":")).encode()).hexdigest()

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--core-revision",required=True); p.add_argument("--execution-id",required=True); p.add_argument("--report")
    a=p.parse_args(); actual=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    checks=[]
    if actual != a.core_revision:
        result="BLOCKED"; checks.append({"case":"target_revision_identity","result":"BLOCKED"})
    else:
        state=State()
        z=Candidate(parent_state_id=state.state_id,proposed_state=State(elements={"z":1}, version=1),origin="z-authority")
        aa=Candidate(parent_state_id=state.state_id,proposed_state=State(elements={"a":1}, version=1),origin="a-authority")
        engine1=Engine(state=state,budget=Budget(total=1))
        first=engine1.step_select([z,aa])
        engine2=Engine(state=state,budget=Budget(total=1))
        second=engine2.step_select([aa,z])
        result="PASS" if first.candidate_id==second.candidate_id else "FAIL"
        checks.append({"case":"alternate-authority","result":result,
                       "selected_candidate_id_forward":first.candidate_id,
                       "selected_candidate_id_reverse":second.candidate_id,
                       "selection_order_forward":["z-authority","a-authority"],
                       "selection_order_reverse":["a-authority","z-authority"],
                       "observation":"selection result is invariant under adversarial input ordering"})

