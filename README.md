# Token X-Ray

### Measure it. Verify it. Reproduce it yourself.

Token X-Ray is a small, reproducible benchmark for measuring whether previously quality-verified repeated AI work can avoid unnecessary model execution **without reducing measured task quality**.

Instead of asking you to trust a savings percentage, Token X-Ray gives you the workload, runner, and measurement method so you can run the test and inspect your own results.

## Why Token X-Ray exists

AI workloads can repeat work. Sometimes that repetition is necessary. Sometimes it is not.

Token X-Ray compares two lanes:

| Lane | Behavior |
|---|---|
| **BASELINE** | Execute every request. |
| **GOVERNED** | Reuse a previously quality-verified result only when the complete prompt hash matches within the same run. Otherwise, execute the model. |

Then it compares task quality, model calls, input/output tokens, calls avoided, tokens avoided, and local wall-clock latency recorded around model calls.

> Reduce unnecessary execution only when measured quality is preserved.

## Reported bounded reproduction

A prior local reproduction was reported using:

- **Model:** `llama3.2:latest`
- **Provider/runtime:** Ollama
- **Workload:** `tokenxray-public-v1`, ten deterministic requests in five identical prompt pairs
- **Quality criterion:** exact expected-answer match after trimming the model response

| Metric | Baseline | Governed |
|---|---:|---:|
| Quality | 10/10 | 10/10 |
| Model calls | 10 | 5 |
| Ollama-reported tokens | 412 | 206 |

On that workload, **5 model calls** and **206 reported tokens** were avoided, while measured quality remained **10/10 in both lanes**.

These figures describe a **reported, workload-specific reproduction result**, not a new run or independent validation. The raw result and full environment record for that prior run are not included in this repository. Run the benchmark to generate your own evidence.

This is **not evidence that every AI workload will save 50%**. Different prompts, models, providers, workloads, caching behavior, and quality requirements can produce different results. The `latest` model tag can also change over time.

## Quick start

### Requirements

- Python 3
- Ollama running locally
- `llama3.2:latest` installed

Confirm the model is installed:

```bash
ollama list
```

From the repository root, run:

```bash
python src/run_repro.py
```

The runner uses the local Ollama endpoint at `http://127.0.0.1:11434/api/generate` and writes:

```text
results/result.json      # Summary
results/baseline.json    # Baseline per-request measurements
results/governed.json    # Governed per-request measurements
```

### How reuse works

The included workload contains repeated deterministic prompts. In the governed lane, a previous result may be reused only when:

1. The SHA-256 hash of the complete prompt matches.
2. The previous result passed the predefined quality check.

Otherwise, the model executes normally. Reuse is held in memory within the governed run; reused requests do not call the model. Their answers are still checked against the current task's expected answer.

This is exact-prompt reuse with fixed model settings, not similarity matching or a persistent cache. The prompt hash does not include every field of the model request.

### Example terminal summary

The reported prior run corresponds to this summary; your token counts and outcome may differ:

```text
TOKEN X-RAY PUBLIC REPRO RESULT

PASS               : True
Baseline quality   : 10/10
Governed quality   : 10/10
Baseline calls     : 10
Governed calls     : 5
Calls avoided      : 5
Baseline tokens    : 412
Governed tokens    : 206
Tokens avoided     : 206
```

Token counts come from Ollama's `prompt_eval_count` and `eval_count` fields. Reused requests record zero model tokens. Local dollar cost is not inferred.

The runner measures wall-clock time around each model call and sums those measurements. Reused requests record zero latency, so this is not an end-to-end measurement of all benchmark or reuse overhead.

`PASS` requires all ten answers to pass in both lanes, ten baseline calls, five governed calls, and five reuses. It does not require the example token totals. The runner exits with a nonzero status if those quality and call-count checks fail; its pass criteria are specific to the included workload.

## Repository structure

```text
README.md
SHA256SUMS.csv
docs/
  CLAIM_REGISTER.md
src/
  run_repro.py
workloads/
  workload.json
.github/
  ISSUE_TEMPLATE/
    reproduction_result.md
```

| File | Purpose |
|---|---|
| `src/run_repro.py` | Runs both lanes and records measurements. |
| `workloads/workload.json` | Defines the workload and expected answers. |
| `docs/CLAIM_REGISTER.md` | Defines what the current evidence does and does not support. |
| `SHA256SUMS.csv` | Provides SHA-256 hashes for the listed files in this revision; the manifest does not hash itself. |
| `.github/ISSUE_TEMPLATE/reproduction_result.md` | Helps outside testers report a reproduction with its environment and results. |

## Claim boundaries

Token X-Ray currently demonstrates a bounded local reproduction. It does not establish:

- Universal AI compute or percentage savings
- Guaranteed financial savings or provider-dollar savings
- Independent third-party validation
- Hardware attestation or hardware-backed enforcement
- Quantum advantage

Results should always be reported with the workload, model, environment, version, quality criterion, and measurement method that produced them. See the [Claim Register](docs/CLAIM_REGISTER.md).

## Report your reproduction

**Run it. Inspect the result. Decide for yourself.**

If you reproduce the benchmark on another system, model, or workload, [open a reproduction report](https://github.com/dustin621408-pixel/token-xray/issues/new?template=reproduction_result.md). Include the commit, environment, measured results, and any deviations, including failed runs.

Review attachments before sharing. Do not include credentials, proprietary prompts, or private customer data.
