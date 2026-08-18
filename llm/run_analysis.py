"""Write the derived tables into `results/`, from the raw log alone.

    PYTHONPATH=. python llm/run_analysis.py

Needs no GPU and no network, so CI runs it on every push and asks git whether
any table moved. Until a real run exists there is nothing to derive and it says
so and exits cleanly, which is correct: the check starts guarding the moment
there is something to guard.

Floats are written to six decimals for the same reason as the Hebbian side, so
two runs produce byte-identical files.
"""

import csv
import pathlib

import measurements

RESULTS = pathlib.Path(__file__).parent / "results"
DECIMALS = 6

TABLES = [
    ("cooperation_rates.csv",
     ["model", "condition", "opening", "matches", "cooperation_rate"],
     lambda played, lost: measurements.cooperation_rates(played)),
    ("vs_bots.csv",
     ["model", "bot", "matches", "model_score_per_turn", "bot_score_per_turn",
      "model_cooperation", "reciprocity_index"],
     lambda played, lost: measurements.vs_bots(played)),
    ("reciprocity.csv",
     ["model", "condition", "seats_measured", "reciprocity_index"],
     lambda played, lost: measurements.reciprocity(played)),
    ("self_play_lock_in.csv",
     ["model", "opening", "condition", "matches",
      "settled_on_mutual_cooperation", "settled_on_mutual_defection",
      "unsettled", "mean_score_per_turn"],
     lambda played, lost: measurements.self_play_lock_in(played)),
    ("contrast_parse_health.csv",
     ["contrast", "varies", "control_model", "control_matches", "control_lost",
      "control_loss_rate", "original_matches", "original_lost",
      "original_loss_rate"],
     lambda played, lost: measurements.contrast_parse_health(
         played, lost, measurements.read_contrasts())),
    ("reasoning_contrast.csv",
     ["condition", "matches_reasoning_off", "cooperation_reasoning_off",
      "matches_reasoning_on", "cooperation_reasoning_on", "difference"],
     lambda played, lost: measurements.reasoning_contrast(
         played, measurements.read_contrasts())),
    ("one_shot_offers.csv",
     ["model", "dictator_decisions", "dictator_offer", "ultimatum_decisions",
      "ultimatum_offer", "paid_to_avoid_refusal", "responder_decisions",
      "minimum_accepted", "would_reject_own_offer"],
     lambda played, lost: measurements.one_shot_offers(
         measurements.read_one_shot())),
    ("opening_round.csv",
     ["model", "opening", "condition", "seats", "cooperated_in_round_0"],
     lambda played, lost: measurements.opening_round(played)),
    ("settling.csv",
     ["model", "opening", "condition", "matches",
      "settled_cooperative", "mean_round_settled_cooperative",
      "settled_defective", "mean_round_settled_defective", "unsettled"],
     lambda played, lost: measurements.settling(played)),
    ("message_content.csv",
     ["model", "opening", "messages_sent", "share_naming_cooperate",
      "share_naming_defect", "mean_characters", "rounds_both_seats_identical"],
     lambda played, lost: measurements.message_content(played)),
    ("reason_matches_action.csv",
     ["model", "rounds_naming_an_action", "rounds_agreeing", "agreement_rate"],
     lambda played, lost: measurements.reason_matches_action(played)),
    ("context_headroom.csv",
     ["model", "context_tokens", "longest_prompt", "headroom"],
     lambda played, lost: measurements.context_headroom(played, lost)),
    ("parse_health.csv",
     ["model", "matches_played", "matches_lost", "loose_reads",
      "mean_rounds_before_loss"],
     lambda played, lost: measurements.parse_health(played, lost)),
]


def formatted(value):
    """Counts stay counts; anything measured gets fixed decimals."""
    if isinstance(value, (int, str)):
        return value
    return f"{value:.{DECIMALS}f}"


def write_csv(name, header, rows, results=RESULTS):
    results.mkdir(parents=True, exist_ok=True)
    with open(results / name, "w", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows([formatted(value) for value in row] for row in rows)


def main(log=measurements.LOG, results=RESULTS):
    played = measurements.read(log)
    lost = measurements.failures(log)
    if not played and not lost:
        print(f"no matches in {log}, nothing to derive yet")
        return
    for name, header, derive in TABLES:
        write_csv(name, header, derive(played, lost), results)
    print(f"derived {len(TABLES)} tables from {len(played)} matches "
          f"({len(lost)} lost to unparseable replies)")


if __name__ == "__main__":
    main()
