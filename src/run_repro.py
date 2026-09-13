import hashlib
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "llama3.2:latest"
URL = "http://127.0.0.1:11434/api/generate"


def sha256_text(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def call_model(prompt):
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0,
            "seed": 1
        }
    }

    request = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    started = time.perf_counter()

    with urllib.request.urlopen(request, timeout=180) as response:
        data = json.loads(response.read().decode("utf-8"))

    return {
        "actual": data.get("response", "").strip(),
        "input_tokens": data.get("prompt_eval_count", 0) or 0,
        "output_tokens": data.get("eval_count", 0) or 0,
        "latency_ms": (time.perf_counter() - started) * 1000.0
    }


workload = json.loads(
    (ROOT / "workloads" / "workload.json").read_text(
        encoding="utf-8-sig"
    )
)

tasks = workload["tasks"]


def baseline():
    rows = []

    for task in tasks:

        result = call_model(task["prompt"])

        rows.append({
            "id": task["id"],
            "expected": task["expected"],
            "actual": result["actual"],
            "quality_pass":
                result["actual"] == task["expected"],
            "model_called": True,
            "reused": False,
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "latency_ms": result["latency_ms"]
        })

    return rows


def governed():
    rows = []
    verified = {}

    for task in tasks:

        key = sha256_text(task["prompt"])

        if key in verified:

            previous = verified[key]

            rows.append({
                "id": task["id"],
                "expected": task["expected"],
                "actual": previous["actual"],
                "quality_pass":
                    previous["actual"] == task["expected"],
                "model_called": False,
                "reused": True,
                "input_tokens": 0,
                "output_tokens": 0,
                "latency_ms": 0.0
            })

            continue

        result = call_model(task["prompt"])

        row = {
            "id": task["id"],
            "expected": task["expected"],
            "actual": result["actual"],
            "quality_pass":
                result["actual"] == task["expected"],
            "model_called": True,
            "reused": False,
            "input_tokens": result["input_tokens"],
            "output_tokens": result["output_tokens"],
            "latency_ms": result["latency_ms"]
        }

        rows.append(row)

        if row["quality_pass"]:
            verified[key] = row

    return rows


def summarize(rows):
    return {
        "quality": sum(1 for x in rows if x["quality_pass"]),
        "calls": sum(1 for x in rows if x["model_called"]),
        "reused": sum(1 for x in rows if x["reused"]),
        "tokens": sum(
            x["input_tokens"] + x["output_tokens"]
            for x in rows
        ),
        "latency_ms": sum(
            x["latency_ms"]
            for x in rows
        )
    }


print("Running baseline...")
baseline_rows = baseline()

print("Running governed...")
governed_rows = governed()

b = summarize(baseline_rows)
g = summarize(governed_rows)

quality_ok = (
    b["quality"] == len(tasks)
    and g["quality"] == len(tasks)
)

behavior_ok = (
    b["calls"] == 10
    and g["calls"] == 5
    and g["reused"] == 5
)

passed = quality_ok and behavior_ok

result = {
    "status": "PASS" if passed else "FAIL",
    "model": MODEL,
    "workload_id": workload["workload_id"],

    "baseline_quality": b["quality"],
    "governed_quality": g["quality"],

    "baseline_calls": b["calls"],
    "governed_calls": g["calls"],
    "calls_avoided":
        b["calls"] - g["calls"],

    "baseline_tokens": b["tokens"],
    "governed_tokens": g["tokens"],
    "tokens_avoided":
        b["tokens"] - g["tokens"],

    "baseline_latency_ms": b["latency_ms"],
    "governed_latency_ms": g["latency_ms"],
    "latency_difference_ms":
        b["latency_ms"] - g["latency_ms"],

    "token_source":
        "Ollama prompt_eval_count and eval_count",

    "measurement_boundary":
        "Exact quality-verified prompt reuse on this workload only."
}

(ROOT / "results").mkdir(exist_ok=True)

(ROOT / "results" / "baseline.json").write_text(
    json.dumps(baseline_rows, indent=2),
    encoding="utf-8"
)

(ROOT / "results" / "governed.json").write_text(
    json.dumps(governed_rows, indent=2),
    encoding="utf-8"
)

(ROOT / "results" / "result.json").write_text(
    json.dumps(result, indent=2),
    encoding="utf-8"
)

print("")
print("============================================================")
print(" TOKEN X-RAY PUBLIC REPRO RESULT")
print("============================================================")
print("")
print(f"PASS               : {passed}")
print(f"Baseline quality   : {b['quality']}/{len(tasks)}")
print(f"Governed quality   : {g['quality']}/{len(tasks)}")
print(f"Baseline calls     : {b['calls']}")
print(f"Governed calls     : {g['calls']}")
print(f"Calls avoided      : {result['calls_avoided']}")
print(f"Baseline tokens    : {b['tokens']}")
print(f"Governed tokens    : {g['tokens']}")
print(f"Tokens avoided     : {result['tokens_avoided']}")
print("")

if not passed:
    raise SystemExit(1)
