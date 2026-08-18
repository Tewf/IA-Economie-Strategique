# The data, and the conditions it was produced under

What every file here holds, and what has to be reported with it for a number to
mean anything. The finding these files support is in
[`../README.md`](../README.md#what-it-found).

`matches.jsonl` is the measurement and costs 4.81 h on a GPU. Every `.csv` beside
it is arithmetic over that file by [`../measurements.py`](../measurements.py), and
CI re-derives all seven on each push and fails on any difference, so a table here
cannot drift from the log it came from.

## Provenance, and what has to be reported with any reuse

220 matches of 30 rounds played 2026-08-17 on one machine: Ubuntu 24.04, Intel
i5-12450H, 16 GB RAM, NVIDIA RTX 4060 Mobile (8 GB), Ollama serving one model at
a time. Temperature 0.7, context window 8192 tokens, per-player seeds derived
from `BASE_SEED = 0`, payoff order counterbalanced across the four repetitions of
every cell. All five models are 4-bit quantised local builds:

| model | parameters | quantisation | Ollama digest (first 24) | build pulled |
|---|---|---|---|---|
| qwen3:8b | 8.2B | Q4_K_M | `500a1f067a9f782620b40bee` | 2026-07-25 |
| qwen2.5:7b-instruct | 7.6B | Q4_K_M | `845dbda0ea48ed749caafd9e` | 2026-07-24 |
| mistral:7b | 7.2B | Q4_K_M | `6577803aa9a036369e481d64` | 2025-10-31 |
| gemma3:4b | 4.3B | Q4_K_M | `a2af6cc3eb7fa8be8504abaf` | 2026-07-26 |
| phi3:mini | 3.8B | **Q4_0** | `4f222292793889a9a40a0207` | 2025-10-31 |

**A tag is not a version.** `qwen3:8b` names whatever build Ollama last resolved
that tag to, so the digests above are the only reproducible identifier of what
actually played, and a rerun that resolves a different digest is a different
experiment.

**A confound to carry, not to bury.** phi3:mini is the model whose replies could
not be parsed, and it is also the only model in the panel at `Q4_0` rather than
`Q4_K_M`, one of the two oldest builds, and the smallest. Those explanations are
not separated by this design: its failure to hold an answer format may be the
model, the coarser quantisation, or the nine-month-older build, and nothing here
distinguishes them. That is why its cells are reported as unreadable rather than
as a result about phi3.

Every model in the panel is 4B to 8B and 4-bit quantised on an 8 GB card. Where
these results differ from work using frontier models, model scale and
quantisation are live explanations that this design cannot rule out.

## `matches.jsonl`, one JSON object per finished match

Append-only, one line per match, never regenerated. 220 lines.

| field | type | meaning |
|---|---|---|
| `key` | string | The match's identity, `cell\|model\|opponent\|condition\|opening\|repetition`. Idempotency is keyed on this: a run skips any key already present, which is what makes a multi-hour sweep resumable |
| `cell` | string | `self_play` or `vs_bot` |
| `model` | string | The Ollama tag seated in seat A |
| `opponent` | string | The same tag again in `self_play`, or the Axelrod strategy name in `vs_bot` |
| `condition` | string | `with_cheap_talk` or `without_cheap_talk` |
| `opening` | string | The synthetic first round injected before play: `neutral`, `mutual_cooperation` or `mutual_defection` |
| `repetition` | int | 0 to 3. Parity selects the payoff-line order, so repetitions are not interchangeable draws |
| `rounds` | list | **The play itself**, one object per round: `a_action` and `b_action` (`"Cooperate"` / `"Defect"`), `a_score` and `b_score`, and `a_message` / `b_message` when the condition has a channel. Its length is how far the match got: 30 in a whole match, fewer in a lost one |
| `a_total`, `b_total` | int | Payoff summed over the match, seat A first. 90 is mutual cooperation throughout, 30 mutual defection throughout |
| `a_transcript`, `b_transcript` | list | The raw model replies for that seat, one entry per **call** rather than per round: 30 with no channel and 60 with one, since a cheap-talk round costs a message call and an action call. Each is `{content, thinking, seconds}`, keeping a reasoning field apart from the answer text for the models that return one |
| `a_parse_fallbacks`, `b_parse_fallbacks` | int | Rounds where the strict `ACTION:` read failed and a lenient read was used. Non-zero means the reply's prose was trusted more than its format |
| `seconds` | float | Wall-clock for the match, including model load on a cold model |
| `package_c_at_end` | int | CPU package temperature in °C at the final round, kept because thermal throttling changes latency and a stopped run has to be explainable |

A match that could not be completed is recorded with the rounds it reached rather
than dropped, so a gap in the grid is always visible as a short match and never
as a missing line.

## The seven derived tables

| file | one row per | what it answers |
|---|---|---|
| `cooperation_rates.csv` | model × condition × opening | The headline: how often the model cooperated in each experimental cell |
| `self_play_lock_in.csv` | model × opening × condition | Whether a pair *settled*, and on what. The ratchet measurement, comparable to `mirror_neurons/results/self_play_lock_in.csv` |
| `vs_bots.csv` | model × Axelrod strategy | Score per turn both ways, cooperation rate, reciprocity index |
| `reciprocity.csv` | model × condition | The reciprocity index over self-play seats, on the shared definition in [`../../reciprocity.py`](../../reciprocity.py) |
| `reason_matches_action.csv` | model | Of the rounds whose reasoning named an action, how often the move agreed with it |
| `parse_health.csv` | model | Matches played, matches lost, lenient reads, mean rounds before a loss. **Read this before any other table** |
| `context_headroom.csv` | model | Longest prompt against the requested window. The audit trail for a truncation fault that once invalidated a run silently |

`reciprocity_index` is P(cooperate | opponent cooperated last) minus
P(cooperate | opponent defected last), on the shared definition in
[`../../reciprocity.py`](../../reciprocity.py). It is `NaN`, and not zero, whenever
**the opponent never varied**, which is exactly the case against a pure defector
or against a partner that cooperated in every round, because the conditional the
measure subtracts was never observed. `0.000000` means something different: the
seat's action ignored what the opponent just did. Treat the two as different
facts, and note that a model reported at `NaN` under cheap talk is usually a model
whose partner cooperated throughout.

Rates are proportions in `[0, 1]`, scores are payoff per turn, and every float is
written to six decimals because CI compares these files byte for byte.

## The three figures

`self_play_lock_in.png`, `cooperation_by_condition.png` and
`reciprocity_against_the_imitator.png`, drawn from the CSVs above by
[`../plot_results.py`](../plot_results.py). They are committed for the write-up
and the site, and are deliberately **not** byte-compared in CI: a PNG is
rasterised through the host's own freetype, so two machines can draw the same
figure into different bytes.

## Reproducing this

```sh
pip install -r requirements.txt                # axelrod pinned at 4.13.1
for m in qwen3:8b qwen2.5:7b-instruct mistral:7b gemma3:4b phi3:mini; do
    ollama pull "$m"                           # one model per invocation
done
export PYTHONPATH=.                            # run from the repository root
python llm/preflight_checks.py                # 19 offline checks, no GPU
python llm/preflight_checks.py --online        # smoke test, prices the run
python llm/run_experiment.py                   # hours; resumable; one stage at a time
python llm/run_analysis.py && python llm/plot_results.py
```

Check the digests you actually pulled against the table above before treating a
rerun as a replication. Expect roughly 5 h of match time plus cooldown on
comparable hardware, and read
[`../README.md`](../README.md#what-runs-and-what-it-costs) first: one model fits
on an 8 GB card at a time, and switching in a tight loop took this machine down.
