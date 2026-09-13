# Token X-Ray

Token X-Ray is a small local benchmark for measuring whether
previously quality-verified identical work can avoid unnecessary
model execution without reducing measured task quality.

## Reproduce it yourself

Requirements:

- Python 3
- Ollama
- llama3.2:latest installed locally

Run:

    python src/run_repro.py

The result will be written to:

    results/result.json

## What is measured

- model calls
- Ollama-reported input/output tokens
- exact-match task quality
- local wall-clock latency
- calls avoided
- tokens avoided

## Reuse rule

A result is reused only when:

1. the complete prompt hash matches exactly, and
2. the previous result passed the predefined quality check.

## Claim boundary

Results apply only to the named workload, model, environment,
version and measurement method.

No universal AI-compute savings percentage is claimed.

Local dollar cost is not inferred.

No telemetry is transmitted.
