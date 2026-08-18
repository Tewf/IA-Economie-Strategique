# The data, and the conditions it was produced under

What every file here holds, and what has to be reported with it for a number to
mean anything. The finding these files support is in
[`../README.md`](../README.md#what-it-found).

`matches.jsonl` is the measurement and costs 4.81 h on a GPU. Every `.csv` beside
it is arithmetic over that file by [`../measurements.py`](../measurements.py), and
CI re-derives all of them on each push and fails on any difference, so a table
here cannot drift from the log it came from.

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

**`phi3:mini` is the 128k build**, not the 4k one: it reports
`phi3.context_length` 131072. Worth stating because the name does not, and a
control built on the assumption that `mini` means 4k varied two things at once.
Every model above was asked for a `num_ctx` of 8192, which all five support.

**A tag is not a version.** `qwen3:8b` names whatever build Ollama last resolved
that tag to, so the digests above are the only reproducible identifier of what
actually played, and a rerun that resolves a different digest is a different
experiment.

**A confound, and the arm that tests it.** phi3:mini is the model whose replies
could not be parsed, and it is also the only model in the panel at `Q4_0` rather
than `Q4_K_M`, one of the two oldest builds, and the smallest. The grid separates
none of those, which is why its cells are reported as unreadable rather than as a
result about phi3. [`../run_contrasts.py`](../run_contrasts.py) replays its whole
stage on the `Q4_K_M` build of the *same* 128k weights, holding the seed stream,
so quantisation is the only thing that moves; `contrast_parse_health.csv` reports
it beside the original, with a `varies` column because the first attempt at that
arm did not vary what it claimed to.

**The answer, in one line: quantisation is much of it and not all of it.** At the
same 128k context and the same seeds, `Q4_K_M` loses 4 of 44 matches against
`Q4_0`'s 10 of 44. That is a real effect and still the only non-zero loss rate in
the panel, so phi3's cells remain uninterpreted rather than rehabilitated. The
mis-specified arm, a 4k build asked for the grid's 8192-token window, loses 33 of
44 and measures a context-window mismatch instead.

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

## The thirteen derived tables

| file | one row per | what it answers |
|---|---|---|
| `cooperation_rates.csv` | model × condition × opening | The headline: how often the model cooperated in each experimental cell |
| `self_play_lock_in.csv` | model × opening × condition | Whether a pair *settled*, and on what. The ratchet measurement, comparable to `mirror_neurons/results/self_play_lock_in.csv` |
| `settling.csv` | model × opening × condition | *When* it settled. Round 0 means the opening decided the match outright; a late round means there was a window. Lock-in cannot show this |
| `message_content.csv` | model × opening | What the channel actually carried: whether a message named an action, how long it was, and how often both seats sent the identical string |
| `reasoning_contrast.csv` | condition | qwen3 in the imposed defective cell with reasoning off against on. The grid runs `think` off for every model because it costs qwen3 34 s a call, so this is the arm that tests the panel's hardest case |
| `one_shot_offers.csv` | model | The Dictator and Ultimatum games. What a model gives when refusal is impossible, what it gives when refusal is possible, the difference between them, and the least it says it would accept |
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

`message_content.csv` counts a message as naming an action when the substring
`COOPERAT` or `DEFECT` appears in it, which is a proxy and misses a paraphrase.
It is reported with verbatim samples in the article for exactly that reason: the
counts alone do not distinguish a model that sends nothing of substance from one
that sends fluent collaborative prose and defects anyway, and both are in here.

## `contrasts.jsonl` and `contrast-*.jsonl`, the follow-up arms

Matches run after the grid to answer one question each, kept out of
`matches.jsonl` so the declared 220 stays 220. Each record carries a `contrast`
field naming its arm, and otherwise has the same shape as a grid match.

**Arms added after 2026-08-18 write their own file.** Resumability is keyed on
the match rather than on the arm, so two arms replaying the same cells of the
same model produce identical keys and the second would skip the first's work.
The three arms already in `contrasts.jsonl` stayed there: moving records between
raw logs to tidy a naming scheme is not worth the risk to data that cost hours.

**A lost match keeps its last two replies per seat.** It used to record only how
far it got, which is why two qwen3 matches lost to an empty answer could not be
diagnosed from the log at all.

## `one_shot.jsonl`, one JSON object per decision

Sixty decisions played 2026-08-18 on the same machine and the same five models,
one call each rather than thirty rounds a match, so the whole run is minutes of
card time. Same temperature, same context window, and seeds derived from the same
base with the game and role in the key.

The Dictator and Ultimatum games are one decision rather than thirty rounds, so
they share no field with `matches.jsonl` and are logged separately. `game` and
`role` name the decision (`dictator` has the empty role), `field` is the line the
prompt asked for, `value` is the integer read from it or `null` if the reply named
no number, `loose_read` marks a number taken from anywhere other than that line,
and `reply` is the whole answer with its reasoning kept apart.

**An offer outside 0 to 100 is recorded rather than clipped.** A model that
answers 150 has not understood the endowment, and clipping would hide that. None
did, in this run.

## The eight figures

`self_play_lock_in.png`, `cooperation_by_condition.png`,
`reciprocity_against_the_imitator.png`, `escape_from_an_imposed_regime.png`,
`settling_round.png`, `opening_round.png`, `message_content.png` and
`one_shot_offers.png`, drawn from the CSVs above by
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
