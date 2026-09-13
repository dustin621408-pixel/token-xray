---
name: Report a reproduction
about: Share a bounded benchmark result, including failures or deviations.
title: "Reproduction: "
labels: ''
assignees: ''
---

## Before sharing

Review all text and attachments. Do not include API keys, passwords, credentials, proprietary prompts, private customer data, or sensitive local paths. Redact sensitive details and describe any redactions that affect interpretation.

## Environment

- Operating system and version:
- Hardware (CPU, GPU, RAM; no serial numbers or device identifiers):
- Python version:
- Ollama version:
- Model name, tag, and model ID/digest if available:
- Repository commit hash:
- Run date:

## Workload and method

- Workload ID/file:
- Unmodified included workload, or describe changes using public-safe details:
- Command used:
- Quality criterion:
- Any runner/model-setting changes:

The current runner's PASS checks assume the included ten-request workload. Disclose changes when reporting another workload.

## Results

| Metric | Baseline | Governed |
|---|---|---|
| Quality (passed/total) | | |
| Model calls | | |
| Ollama-reported tokens | | |
| Reported latency (ms) | | |

- PASS/FAIL or execution error:
- Calls avoided:
- Tokens avoided:
- Number of runs and variability, if measured:

## Result file

Attach or paste your reviewed `results/result.json` below. Do not substitute the README's example values for your measured output.

```json

```

## Errors or deviations

Describe failures, unexpected answers, missing usage fields, or differences from the README example. Include only reviewed, public-safe error output. If sharing per-request result files, review them for sensitive prompts and answers first.
