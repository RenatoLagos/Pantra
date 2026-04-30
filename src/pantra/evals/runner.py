from __future__ import annotations

import asyncio
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml

from pantra.llm.classifier import Classifier

CASES_DIR = Path(__file__).parent / "cases"


@dataclass(slots=True)
class CaseResult:
    name: str
    passed: bool
    failures: list[str]


async def _run_classifier_case(case: dict) -> CaseResult:
    failures: list[str] = []
    classifier = Classifier()
    out = await classifier.classify(
        text=case["input"]["text"],
        business_domain=case["input"].get("business_domain", "other"),
    )
    expect = case.get("expect", {})

    if "language" in expect and out.language != expect["language"]:
        failures.append(f"language: expected {expect['language']!r}, got {out.language!r}")
    if "intent" in expect and out.intent != expect["intent"]:
        failures.append(f"intent: expected {expect['intent']!r}, got {out.intent!r}")
    if "needs_human" in expect and out.needs_human != expect["needs_human"]:
        failures.append(f"needs_human: expected {expect['needs_human']}, got {out.needs_human}")
    for substring in expect.get("extracted_must_contain", []):
        if substring not in json.dumps(out.extracted.model_dump()):
            failures.append(f"extracted missing substring: {substring!r}")
    for pattern in expect.get("matches_regex", []):
        if not re.search(pattern, json.dumps(out.model_dump())):
            failures.append(f"output does not match regex: {pattern!r}")

    return CaseResult(name=case["name"], passed=not failures, failures=failures)


async def run_all() -> list[CaseResult]:
    results: list[CaseResult] = []
    for path in sorted(CASES_DIR.glob("*.yaml")):
        case = yaml.safe_load(path.read_text())
        if case.get("kind", "classifier") == "classifier":
            results.append(await _run_classifier_case(case))
        else:
            results.append(CaseResult(
                name=case["name"], passed=False,
                failures=[f"case kind {case.get('kind')!r} not supported yet"],
            ))
    return results


def _print_report(results: list[CaseResult]) -> int:
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        print(f"[{status}] {r.name}")
        for f in r.failures:
            print(f"        ↳ {f}")
    print(f"\n{passed}/{len(results)} passed, {failed} failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    results = asyncio.run(run_all())
    sys.exit(_print_report(results))
