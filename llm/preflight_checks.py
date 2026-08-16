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
import os
import pathlib
import sys
import tempfile
import time

import axelrod as axl

import grid_config
import machine_gate
import prompt_loader
import run_analysis
import run_experiment
import run_ownership
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


def a_message_turn_is_not_an_action_turn():
    """The cheap-talk call must not carry the answer-format instruction.

    It did, in the first run. The scenario ends with "answer in exactly this
    format, and nothing else", the message call inherited it, and both models
    sent each other a literal `ACTION: Defect` line as their message. That is
    not a non-binding signal, it is announcing the move before a simultaneous
    choice, and it would have been reported as cheap talk failing to sustain
    cooperation when cheap talk had never been tested.
    """
    action = prompt_loader.render("prisoners_dilemma", 0, "action")
    message = prompt_loader.render("prisoners_dilemma", 0, "message")
    assert action != message, "both calls would be given the same instructions"
    assert "ACTION: <Cooperate or Defect>" in action, "the action call lost its format"
    assert "ACTION:" not in message, (
        "the message call still tells the model to answer with an ACTION line")
    for shared in ("you get 3 points", "unknown number of rounds"):
        assert shared in action and shared in message, (
            f"the two calls disagree about the game itself, missing: {shared}")
    player = OllamaPlayer("phi3:mini", action, message_prompt=message)
    assert player.system_prompt != player.message_prompt, (
        "the player was built with one prompt for both kinds of call")


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


def _no_gate():
    """Stub players load no model and heat nothing, so nothing is gated."""


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
        run_experiment.run(specs[:2], make=_stub_pair, log=log, gate=_no_gate)
        with open(log, "a") as handle:
            handle.write('{"key": "half-written and then kil')
        run_experiment.run(specs, make=_stub_pair, log=log, gate=_no_gate)
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


def one_stage_at_a_time_and_the_owner_is_named():
    """A second launch must be refused, and the owner findable without guessing.

    On 2026-08-16 the grid was launched three times and killed twice in
    seventeen minutes, by a session and by that session's own subagent. Neither
    could see the other, and the second kill needed `-9` because the first had
    been answered with `setsid nohup`. The overlap is what this refuses; the
    owner file is so the next agent reaching for a `pkill` can ask instead.
    """
    with tempfile.TemporaryDirectory() as folder:
        marker = pathlib.Path(folder) / ".running"
        assert run_ownership.read_owner(marker) is None, "claimed an empty marker"
        with run_ownership.owning_the_run("stage-under-test", marker):
            held = run_ownership.read_owner(marker)
            assert held is not None and held["pid"] == os.getpid(), held
            assert held["stage"] == "stage-under-test", held
            assert "ask the owner" in held["note"], "the marker does not say to ask"
            try:
                with run_ownership.owning_the_run("second", marker):
                    raise AssertionError("a second stage was allowed to start")
            except run_ownership.AlreadyRunning as refusal:
                assert str(os.getpid()) in str(refusal), (
                    "the refusal does not name the PID to ask about")
        assert not marker.exists(), "the marker outlived the run that wrote it"

    stale = pathlib.Path(tempfile.mkdtemp()) / ".running"
    stale.write_text(json.dumps({"pid": 2 ** 22, "stage": "long gone"}))
    assert run_ownership.read_owner(stale) is None, (
        "a marker from a dead process would block every future stage")


def the_machine_is_checked_before_the_card_is_touched():
    """Temperature belongs in the gate, not just memory.

    Memory is what killed the machine in August; heat is what nearly did the
    next day. One pinned core from another session holds this package at
    79-87 C against a 52 C idle, so the ceiling is really a test for "is anyone
    else working".
    """
    assert (machine_gate.MAXIMUM_RUNNING_TEMPERATURE_C
            > machine_gate.MAXIMUM_START_TEMPERATURE_C), (
        "the running ceiling must be looser than the start ceiling, or the grid "
        "aborts on heat it makes itself")
    assert machine_gate.MAXIMUM_RUNNING_TEMPERATURE_C < 100, (
        "the running ceiling must leave margin below the 100 C critical")
    assert (machine_gate.COOLDOWN_TARGET_C
            < machine_gate.MAXIMUM_RUNNING_TEMPERATURE_C), (
        "cooling to a temperature the gate would already reject is not cooling")
    reading = machine_gate.package_temperature_c(samples=2, interval=0.05)
    assert reading is None or 20 < reading < 110, f"implausible reading {reading}"
    original = machine_gate.MAXIMUM_START_TEMPERATURE_C
    machine_gate.MAXIMUM_START_TEMPERATURE_C = -1
    try:
        machine_gate.check_can_start()
    except machine_gate.OutOfHeadroom as refusal:
        assert "start ceiling" in str(refusal), refusal
    else:
        raise AssertionError("the start ceiling never fires")
    finally:
        machine_gate.MAXIMUM_START_TEMPERATURE_C = original


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
        run_experiment.run(sample, make=_stub_pair, log=log, gate=_no_gate)

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


def the_log_records_the_prompt_once_and_never_echoes_it():
    """What is kept is what cannot be recovered, and only that.

    The per-round user message is `OllamaPlayer._round_prompt` applied to rounds
    the record already holds, so storing it grew the log with the square of the
    match: prompt echoes reached 94% of a projected 39 MB, and the system
    prompt, which is the treatment and is not derivable from the record, was the
    one thing not stored at all. This asserts the trade in both directions.
    """
    player = OllamaPlayer("stub", "system", message_prompt="messages")
    player.transcript.append({"content": "ACTION: Cooperate", "thinking": "",
                              "seconds": 0.1})
    record = play_match(player, StubPlayer("b", ALWAYS_COOPERATE), rounds=0,
                        game=grid_config.GAME, cheap_talk=False)
    for seat in ("a_transcript", "b_transcript"):
        for reply in record[seat]:
            assert "prompt" not in reply, (
                f"{seat} echoes the prompt back into the log, which is what made "
                "it 39 MB of text already present in `rounds`")

    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / "prompts_used.json"
        rendered = run_experiment.write_prompts_used(path)
        assert set(rendered) == {"action|even_repetition", "action|odd_repetition",
                                 "message|even_repetition",
                                 "message|odd_repetition"}, sorted(rendered)
        assert rendered["action|even_repetition"] != rendered["action|odd_repetition"], (
            "the payoff counterbalancing is not visible in the pinned prompts")
        assert rendered["action|even_repetition"] != rendered["message|even_repetition"], (
            "the action turn and the message turn were pinned as the same text")
        written = json.loads(path.read_text())
        assert written["prompts"] == rendered and written["game"], written


OFFLINE = [cheap_talk_is_simultaneous, scoring_matches_the_payoffs,
           a_player_sees_its_own_moves, the_answer_format_is_read_correctly,
           the_prompt_is_not_anchored_on_one_action,
           a_message_turn_is_not_an_action_turn, bots_behave_as_themselves,
           a_bot_is_never_asked_to_talk, seeds_are_stable_across_processes,
           the_run_resumes_where_it_stopped, an_opening_reaches_both_players,
           one_stage_at_a_time_and_the_owner_is_named,
           the_machine_is_checked_before_the_card_is_touched,
           the_analysis_is_deterministic_and_covers_every_cell,
           an_empty_log_derives_nothing_and_says_so,
           the_log_records_the_prompt_once_and_never_echoes_it]


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
    system = prompt_loader.render("prisoners_dilemma", 0, "action")
    messages = prompt_loader.render("prisoners_dilemma", 0, "message")
    rates = {}
    for model in PANEL:
        player = OllamaPlayer(model, system, seed=1, message_prompt=messages)
        opponent = BotOpponent(axl.TitForTat)
        record = play_match(player, opponent, rounds=4,
                            game=grid_config.GAME, cheap_talk=False)
        # The first call also pays to load the model from disk. A long run pays
        # that once per model, so pricing the grid on a rate that includes it
        # overstates the cost several times over. It is reported separately.
        timings = [reply["seconds"] for reply in player.transcript]
        load, steady = timings[0], timings[1:]
        rates[model] = sum(steady) / len(steady)
        print(f"  ok  {model}: {[r['a_action'] for r in record['rounds']]}, "
              f"{player.parse_fallbacks} loose reads, "
              f"{rates[model]:.2f} s a call warm "
              f"(first call {load:.1f} s, cold)")
    print("\nMeasured rates, so the grid can be priced rather than guessed:")
    print(f"  full grid as configured: "
          f"{run_experiment.hours_at(rates):.1f} h")
    return rates


if __name__ == "__main__":
    run_offline()
    if "--online" in sys.argv:
        run_smoke_test()
