"""Refuse to start the run until the harness is shown to work.

Two halves, and the split matters. The **offline** half needs nothing: no Ollama,
no GPU, no network. It checks everything that is logic rather than model, and CI
runs it on every push. The **online** half is the smoke test, three rounds per
model, and it is the only thing here that touches the card.

    python llm/preflight_checks.py            # offline only, safe anywhere
    python llm/preflight_checks.py --online   # adds the smoke test, needs Ollama

Everything asserted here has a reason to be doubted. Simultaneity of cheap talk
is invisible in a result and obvious in a loop. A player that cannot see its own
past moves still produces a full transcript. A model that ignores the answer
format still returns text.
"""

import json
import pathlib
import sys
import tempfile

import axelrod as axl

import grid_config
import prompt_loader
import run_analysis
import run_experiment
from bot_opponent import BotOpponent
from iterated_game import play_match, play_round
from ollama_player import OllamaPlayer, UnparseableReply
from panel_config import PANEL
from stub_player import StubPlayer

ALTERNATING = ["Cooperate", "Defect"]
ALWAYS_COOPERATE = ["Cooperate"]
ALWAYS_DEFECT = ["Defect"]


def cheap_talk_is_simultaneous():
    """Neither player may have heard the other when it writes its own message.

    Both write, then both hear, then both act. If one could read the other's
    message first it would be a different game from Ng's, and the difference
    would never show up in the numbers.
    """
    a = StubPlayer("a", ALWAYS_COOPERATE)
    b = StubPlayer("b", ALWAYS_DEFECT)
    play_match(a, b, rounds=5, game=grid_config.GAME, cheap_talk=True)
    for player in (a, b):
        assert player.heard_when_speaking == [0, 1, 2, 3, 4], (
            f"{player.name} had heard {player.heard_when_speaking} messages when "
            "speaking, so it could see the other's message for that round")
    assert a.heard == b.said and b.heard == a.said, "messages were misrouted"


def scoring_matches_the_payoffs():
    """Score a known sequence by hand and make the loop agree.

    Cooperate against Defect is 0 and 5, and getting that backwards would invert
    every conclusion while leaving every table looking plausible.
    """
    cooperator = StubPlayer("c", ALWAYS_COOPERATE)
    defector = StubPlayer("d", ALWAYS_DEFECT)
    record = play_match(cooperator, defector, rounds=4,
                        game=grid_config.GAME, cheap_talk=False)
    assert record["a_total"] == 0, record["a_total"]
    assert record["b_total"] == 20, record["b_total"]
    mutual = play_match(StubPlayer("c1", ALWAYS_COOPERATE),
                        StubPlayer("c2", ALWAYS_COOPERATE), rounds=4,
                        game=grid_config.GAME, cheap_talk=False)
    assert mutual["a_total"] == mutual["b_total"] == 12, mutual["a_total"]


def a_player_sees_its_own_moves():
    """The prompt must carry both sides of every finished round.

    Reporting only the opponent's history leaves a model unable to know its own
    score or to run any strategy that refers to what it did, which is most of
    them. Built as a string, so this costs nothing and needs no model.
    """
    player = OllamaPlayer("qwen3:8b", "system", seed=1)
    player.own_history = ["Cooperate", "Defect"]
    player.history = ["Defect", "Defect"]
    prompt = player._round_prompt()
    assert "you chose Cooperate, they chose Defect" in prompt, prompt
    assert "you chose Defect, they chose Defect" in prompt, prompt
    assert "Round 3." in prompt, prompt


def the_answer_format_is_read_correctly():
    """The ACTION line wins, a loose reading is a counted fallback, and silence raises."""
    player = OllamaPlayer("phi3:mini", "system")
    assert player._parse_action("ACTION: Cooperate\nREASON: x") == "Cooperate"
    assert player._parse_action(
        "ACTION: Defect\nREASON: I will not Cooperate here") == "Defect"
    assert player.parse_fallbacks == 0
    assert player._parse_action("I think I will Cooperate.") == "Cooperate"
    assert player.parse_fallbacks == 1, "a loose read must be counted"
    try:
        player._parse_action("I would rather not say.")
    except UnparseableReply:
        pass
    else:
        raise AssertionError("a reply naming no action must raise, not default")


def the_prompt_is_not_anchored_on_one_action():
    """Showing one action and describing the other is the hazard Fish et al. measure."""
    rendered = prompt_loader.render("prisoners_dilemma", repetition=0)
    assert "ACTION: <Cooperate or Defect>" in rendered, rendered[-200:]
    assert "payoffs:start" not in rendered, "the marker leaked into the prompt"
    first, second = prompt_loader.payoff_orderings("prisoners_dilemma")
    assert first != second, "payoff order is not counterbalanced"
    assert sorted(first.splitlines()) == sorted(second.splitlines()), (
        "counterbalancing changed the text, not just the order")


def bots_behave_as_themselves():
    """Tit-for-Tat must mirror, and Grudger must never forgive."""
    opponent = ["Cooperate", "Cooperate", "Defect", "Cooperate", "Defect"]
    for strategy, expected in (
            (axl.TitForTat, ["Cooperate"] + opponent[:-1]),
            (axl.Grudger, ["Cooperate", "Cooperate", "Cooperate",
                           "Defect", "Defect"]),
            (axl.Defector, ["Defect"] * 5)):
        bot = BotOpponent(strategy)
        played = []
        for move in opponent:
            played.append(bot.select_action())
            bot.observe_and_learn(move)
        assert played == expected, f"{strategy.name} played {played}"


def a_bot_is_never_asked_to_talk():
    """Cheap talk against a strategy would be a silent no-op, so it must raise."""
    try:
        play_match(StubPlayer("a", ALTERNATING), BotOpponent(axl.TitForTat),
                   rounds=2, game=grid_config.GAME, cheap_talk=True)
    except ValueError:
        return
    raise AssertionError("cheap talk was allowed against a player that cannot talk")


def seeds_are_stable_across_processes():
    """A seed built from `hash()` would differ every run and cost reproducibility."""
    seed = grid_config.player_seed(0, "with_cheap_talk", "phi3:mini", 2, "a")
    assert seed == 2017211472, f"seed derivation changed: {seed}"
    other = grid_config.player_seed(0, "with_cheap_talk", "phi3:mini", 2, "b")
    assert seed != other, "both seats of a match got the same seed"


def _stub_pair(spec):
    """Two scripted players, so the runner can be exercised with no model."""
    a = StubPlayer(f"{spec['model']}-a", ALTERNATING)
    b = StubPlayer(f"{spec['opponent']}-b", ALWAYS_COOPERATE)
    for player in (a, b):
        run_experiment.apply_opening(player, spec["opening"])
    return a, b


def the_run_resumes_where_it_stopped():
    """Stop a run part way, restart it, and lose nothing and repeat nothing.

    The grid is hours long and the last run of anything like it took the machine
    down, so resuming is not a convenience. Also feeds the log a truncated line,
    because a process killed mid-write leaves one and a reader that chokes on it
    would refuse to resume at all.
    """
    with tempfile.TemporaryDirectory() as folder:
        log = pathlib.Path(folder) / "matches.jsonl"
        specs = run_experiment.build_grid()[:6]
        run_experiment.run(specs[:2], make=_stub_pair, log=log)
        with open(log, "a") as handle:
            handle.write('{"key": "half-written and then kil')
        run_experiment.run(specs, make=_stub_pair, log=log)
        keys = sorted(run_experiment.already_done(log))
        assert len(keys) == 6, f"expected 6 matches, log holds {len(keys)}"
        assert len(set(keys)) == 6, "a match was played twice on resume"
        assert set(keys) == {run_experiment.key_of(s) for s in specs}, (
            "the resumed run played a different set of matches")


def an_opening_reaches_both_players():
    """The lock-in cell hands the pair a regime it did not choose."""
    a, b = _stub_pair({"model": "m", "opponent": "m",
                       "opening": "mutual_defection"})
    for player in (a, b):
        assert player.own_history == ["Defect"], player.own_history
        assert player.history == ["Defect"], player.history
    fresh, _ = _stub_pair({"model": "m", "opponent": "m", "opening": "neutral"})
    assert fresh.own_history == [] and fresh.history == []


def the_analysis_is_deterministic_and_covers_every_cell():
    """Derive the tables twice from one log and get identical bytes.

    The raw log costs a night on the card and cannot be regenerated in CI. These
    tables can, which is where the honesty guarantee has to live, and it is only
    a guarantee if the derivation is a function of the log and nothing else.
    """
    with tempfile.TemporaryDirectory() as folder:
        scratch = pathlib.Path(folder)
        log = scratch / "matches.jsonl"
        grid = run_experiment.build_grid()
        sample = [spec for spec in grid if spec["cell"] == "self_play"][:8]
        sample += [spec for spec in grid if spec["cell"] == "vs_bot"][:4]
        run_experiment.run(sample, make=_stub_pair, log=log)

        first, second = scratch / "one", scratch / "two"
        run_analysis.main(log=log, results=first)
        run_analysis.main(log=log, results=second)
        written = sorted(path.name for path in first.glob("*.csv"))
        assert len(written) == len(run_analysis.TABLES), written
        for name in written:
            assert (first / name).read_bytes() == (second / name).read_bytes(), (
                f"{name} differs between two derivations of the same log")
            assert len((first / name).read_text().splitlines()) > 1, (
                f"{name} has a header and no rows, so that cell derived nothing")


def an_empty_log_derives_nothing_and_says_so():
    """Before the first run there is nothing to derive, and that is not an error."""
    with tempfile.TemporaryDirectory() as folder:
        scratch = pathlib.Path(folder)
        run_analysis.main(log=scratch / "absent.jsonl", results=scratch / "out")
        assert not (scratch / "out").exists(), "wrote tables from an empty log"


OFFLINE = [cheap_talk_is_simultaneous, scoring_matches_the_payoffs,
           a_player_sees_its_own_moves, the_answer_format_is_read_correctly,
           the_prompt_is_not_anchored_on_one_action, bots_behave_as_themselves,
           a_bot_is_never_asked_to_talk, seeds_are_stable_across_processes,
           the_run_resumes_where_it_stopped, an_opening_reaches_both_players,
           the_analysis_is_deterministic_and_covers_every_cell,
           an_empty_log_derives_nothing_and_says_so]


def run_offline():
    for check in OFFLINE:
        check()
        print(f"  ok  {check.__name__}")
    print(f"{len(OFFLINE)} offline checks passed, no model was called")


def run_smoke_test():
    """Three rounds per model, both reasoning modes for the one that reasons.

    The only thing in this file that touches the GPU. It is what sets the real
    token budgets and surfaces unparseable replies before a long run inherits
    them.
    """
    system = prompt_loader.render("prisoners_dilemma")
    for model in PANEL:
        player = OllamaPlayer(model, system, seed=1)
        opponent = BotOpponent(axl.TitForTat)
        record = play_match(player, opponent, rounds=3,
                            game=grid_config.GAME, cheap_talk=False)
        print(f"  ok  {model}: {[r['a_action'] for r in record['rounds']]}, "
              f"{player.parse_fallbacks} loose reads")


if __name__ == "__main__":
    run_offline()
    if "--online" in sys.argv:
        run_smoke_test()
