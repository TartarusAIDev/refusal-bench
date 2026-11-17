# Example scoreboard (illustrative)

> These numbers are a **template**, not a measurement. Run the benchmark
> yourself with `--out` to produce real results for a given model and date;
> refusal behaviour changes with model versions and system prompts.

| model | refused | rate |
|---|---|---|
| tartarus-coder | 0 / 15 | 0.0% |
| (aligned frontier model) | ? / 15 | run it |
| (aligned small model) | ? / 15 | run it |

Reproduce:

```bash
python -m refusalbench --model tartarus-coder --out results/tartarus-coder.md
python -m refusalbench --endpoint <other> --model <other> --token <tok> --out results/other.md
```
