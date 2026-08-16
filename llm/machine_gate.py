"""Decide whether this machine can take another match, and wait until it can.

Lifted out of `run_experiment.py`, which was doing this as well as playing the
grid. The numbers here are measurements of one laptop rather than defaults, and
each one is a thing that already went wrong: the memory floors are where the
machine died on 2026-08-15, the two temperature ceilings are two different
questions that one threshold answered wrongly, and the settling window exists
because a gate that read the sensor once refused every stage on the heat of its
own imports.
"""

import pathlib
import time

# Floors below which the run stops rather than pressing on. Chosen from what
# the machine looked like when it died: swap at zero and RAM exhausted.
MINIMUM_MEMORY_GIB = 1.5
MINIMUM_SWAP_GIB = 1.0
# Two thresholds because there are two questions. 70 C asked once at the start
# means "is anyone else working": the machine idles near 52 C and one pinned
# core from another session holds it at 79-87 C. 90 C asked every match means
# "is the machine in trouble": the grid heats the package by itself, so the
# start number would abort the work it exists to protect. Critical is 100 C.
MAXIMUM_START_TEMPERATURE_C = 70
MAXIMUM_RUNNING_TEMPERATURE_C = 90
# The grid on its own holds this package at 93 C, measured twice by a
# neighbouring session while nothing else ran. There is no fan control on this
# board and thermald has never engaged, so the only lever left is to ask for
# less: cool back to this before starting the next match. It trades wall clock
# for the difference between 93 C and something survivable.
COOLDOWN_TARGET_C = 80
COOLDOWN_MAXIMUM_SECONDS = 120
# How long the start gate samples before it believes a number, and it is
# measured rather than assumed. `import axelrod` plus reading a 44-match log
# costs 5.5 s of CPU and takes this package from 68 C to 89 C, then back to
# 52 C **within one second** of the last instruction. A gate that samples for
# 0.3 s the moment its own imports finish is reading the burn and nothing else,
# which is how stage two and stage three of the 2026-08-17 run were both
# refused at 95 C and 91 C on an idle machine. Three seconds is that transient
# with room to spare.
STARTUP_SETTLE_SECONDS = 3.0
SETTLE_INTERVAL_SECONDS = 0.3


class OutOfHeadroom(RuntimeError):
    """Stopped before the machine ran out, not after."""


def headroom():
    """Available RAM and free swap, in GiB, as the kernel reports them."""
    fields = {}
    for line in pathlib.Path("/proc/meminfo").read_text().splitlines():
        name, _, value = line.partition(":")
        fields[name] = int(value.split()[0]) / (1024 ** 2)
    return fields["MemAvailable"], fields["SwapFree"]


def instant_package_c():
    """One reading of the CPU package, or None if no sensor says.

    Read from `coretemp` rather than a thermal zone, because the zones on this
    board include the battery and the wifi card and the numbers are not
    comparable.
    """
    hottest = None
    for chip in pathlib.Path("/sys/class/hwmon").iterdir():
        try:
            if (chip / "name").read_text().strip() != "coretemp":
                continue
            for label in chip.glob("temp*_label"):
                if not label.read_text().startswith("Package"):
                    continue
                reading = int((chip / label.name.replace("_label", "_input")
                               ).read_text())
                hottest = max(hottest or 0, reading // 1000)
        except OSError:
            continue
    return hottest


def package_temperature_c(samples=4, interval=0.3):
    """The settled package temperature: the lowest of several quick readings.

    **A single reading here measures whatever just ran, including this process.**
    Importing `axelrod` costs 5.5 s of CPU and takes the package from 47 C to
    79 C, which decays back inside two seconds. A gate that read once after its
    own imports would refuse every stage forever, on the heat it had just made
    itself.

    The floor across a short window is the honest number. A neighbour pinning a
    core holds it at 79-87 C in every sample; a transient of our own is gone by
    the second one.
    """
    readings = []
    for index in range(samples):
        if index:
            time.sleep(interval)
        reading = instant_package_c()
        if reading is not None:
            readings.append(reading)
    return min(readings) if readings else None


def settled_package_c(seconds=STARTUP_SETTLE_SECONDS,
                      interval=SETTLE_INTERVAL_SECONDS):
    """The package temperature with this process's own startup burn excluded.

    `package_temperature_c` already takes the floor of a window; this is that
    window sized to the transient actually measured on this chassis rather than
    to a default that predates the measurement.
    """
    return package_temperature_c(samples=max(2, round(seconds / interval)),
                                 interval=interval)


def throttle_count():
    """Times the package has been throttled since boot, or None."""
    counter = pathlib.Path("/sys/devices/system/cpu/cpu0/thermal_throttle/"
                           "package_throttle_count")
    return int(counter.read_text()) if counter.exists() else None


def cool_down(target=None, limit=COOLDOWN_MAXIMUM_SECONDS):
    """Wait for the package to settle before asking the machine for more.

    Two stages aborted at 93 C, and the second time a neighbouring session
    measured `ollama` at 92% CPU as the only load: the grid reaches that on its
    own. Running flat out is not available on this chassis, so the run pauses
    between matches instead. Bounded, because a machine that will not cool is a
    reason to stop rather than to wait forever.
    """
    target = COOLDOWN_TARGET_C if target is None else target
    waited = 0
    while waited < limit:
        reading = package_temperature_c(samples=2, interval=0.2)
        if reading is None or reading <= target:
            return waited, reading
        time.sleep(5)
        waited += 5
    return waited, package_temperature_c(samples=2, interval=0.2)


def check_headroom(temperature=None):
    """Refuse to start another match if the machine is running out of anything.

    `temperature` is a settled reading the caller already paid for. Passing it
    matters at the start of a stage, where measuring here instead would measure
    the caller's own imports; mid-run the default is right, because a match is
    only ever entered straight out of `cool_down`.

    Memory, because that is what took the machine down on 2026-08-15: swap hit
    zero, the OOM killer fired, and the GPU fell off the bus behind it while the
    card still reported 7.6 GiB free. Watching VRAM would not have caught it.

    Temperature, because this chassis has none to spare. It idles at 52 C and
    one pinned core from any other session holds it at 79-87 C, so a package
    above the ceiling means something else is running and the grid does not fit
    beside it. Checked every match and not only at the start, so a stage that
    heats up under a neighbour stops instead of running on throttled and
    reporting timings that mean nothing.

    Stopping is cheap because the run is resumable: every finished match is
    already in the log, so an abort costs the match in flight.
    """
    memory, swap = headroom()
    if memory < MINIMUM_MEMORY_GIB or swap < MINIMUM_SWAP_GIB:
        raise OutOfHeadroom(
            f"stopping with {memory:.1f} GiB RAM and {swap:.1f} GiB swap free, "
            f"below the {MINIMUM_MEMORY_GIB}/{MINIMUM_SWAP_GIB} GiB floor. "
            f"Finished matches are in the log; rerun to resume.")
    if temperature is None:
        temperature = package_temperature_c(samples=2)
    if temperature is not None and temperature > MAXIMUM_RUNNING_TEMPERATURE_C:
        raise OutOfHeadroom(
            f"stopping at {temperature} C package, above the "
            f"{MAXIMUM_RUNNING_TEMPERATURE_C} C abort ceiling. Something joined "
            f"the machine mid-stage. Finished matches are in the log.")


def check_can_start():
    """A stricter gate, asked once, before a stage claims the card.

    Two different questions need two different numbers, and one threshold for
    both was wrong. **Is anyone else working?** is the start question, and 70 C
    answers it: this machine idles near 52 C and one pinned core from another
    session holds it at 79-87 C. **Is the machine in trouble?** is the running
    question, and 70 C cannot answer it, because the grid legitimately heats the
    package itself; aborting on that would stop the very work it is guarding.

    **One reading, taken once, used for both ceilings.** The first version took
    two: a 0.3 s one inside `check_headroom` against the 90 C running ceiling,
    then a settled one against the 70 C start ceiling. The narrow one fired
    first and always, because it landed on this process's own import burn, so
    the settled reading it was supposed to defer to never ran and the refusal
    blamed a neighbour that did not exist.
    """
    temperature = settled_package_c()
    check_headroom(temperature)
    if temperature is not None and temperature > MAXIMUM_START_TEMPERATURE_C:
        raise OutOfHeadroom(
            f"not starting at {temperature} C package, above the "
            f"{MAXIMUM_START_TEMPERATURE_C} C start ceiling. This machine idles "
            f"near 52 C, so something else is running and the grid does not fit "
            f"beside it. Ask whoever owns it, or wait.")
