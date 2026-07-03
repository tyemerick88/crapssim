"""End-to-end scenarios for SqueezePlay / PlaceHitProgression.

Each case runs a fixed sequence of dice through a real table and checks the
resulting bankroll and open bets, exercising the stage advancement, the press and
regress, the carry-across-made-points behavior, and the seven-out reset.
"""

import pytest

from crapssim.strategy import PlaceHitProgression
from crapssim.strategy.examples import SqueezePlay
from crapssim.table import Table

BUY_IN = 500.0


def run(strategy, rolls):
    """Run ``rolls`` through a fresh table and return (bankroll, sorted bets)."""
    table = Table()
    player = table.add_player(bankroll=BUY_IN, strategy=strategy)
    table.fixed_run(dice_outcomes=rolls, verbose=False)
    return player.bankroll, sorted(str(b) for b in player.bets)


@pytest.mark.parametrize(
    "rolls, expected_bankroll, expected_bets",
    [
        # Point 4 established, no numbers hit yet -> $66 inside working. (Bets for
        # the point established on the LAST roll appear next roll, hence a trailing
        # roll to realize the board.)
        (
            [(2, 2), (5, 6), (1, 3)],  # pt 4, come-out 11, pt 4 again
            BUY_IN - 66.0,
            ["$15 Place(5)", "$15 Place(9)", "$18 Place(6)", "$18 Place(8)"],
        ),
        # Three inside hits with an outside point (4) so hits never make the point:
        # 5, 9, 6 -> board regresses to $64 across, then a seven-out clears it.
        # Net: +21 +21 +28 - 64 = +6.
        (
            [(2, 2), (1, 4), (4, 5), (2, 4), (3, 4)],
            BUY_IN + 6.0,
            [],
        ),
        # Seven-out sweeps the initial $66 board and restarts the progression.
        (
            [(3, 3), (3, 4)],  # pt 6, then seven-out (nothing hit first)
            BUY_IN - 66.0,  # the initial $66 inside is lost
            [],
        ),
    ],
)
def test_squeezeplay_scenarios(rolls, expected_bankroll, expected_bets):
    bankroll, bets = run(SqueezePlay(), rolls)
    assert bankroll == expected_bankroll
    assert bets == expected_bets


def test_squeezeplay_carries_progression_across_made_point():
    """A made point banks winnings and rebuilds at the same stage, not stage 0."""
    # pt 6; hit the 8 (hit 1, adds 4 & 10); roll 6 -> Place(6) pays AND makes the
    # point (hit 2); new point 4; a non-scoring 2 realizes the rebuilt 2-hit board
    # ($88 inside + 4 & 10) instead of restarting at $66.
    rolls = [(3, 3), (4, 4), (3, 3), (2, 2), (1, 1)]
    _, bets = run(SqueezePlay(), rolls)
    assert bets == [
        "$10 Place(10)",
        "$10 Place(4)",
        "$20 Place(5)",
        "$20 Place(9)",
        "$24 Place(6)",
        "$24 Place(8)",
    ]


def test_independent_progressions_press_separately():
    """Two disjoint PlaceHitProgressions in an AggregateStrategy advance alone."""
    six = PlaceHitProgression([{6: 12.0}, {6: 18.0}, {6: 24.0}])
    eight = PlaceHitProgression([{8: 12.0}, {8: 18.0}, {8: 24.0}])
    strategy = six + eight

    # pt 4; 6 hits twice (press 6: 12 -> 18 -> 24), 8 never hits, trailing roll.
    _, bets = run(strategy, [(2, 2), (3, 3), (2, 4), (1, 4)])

    # The 6 pressed to $24 on its own hits; the untouched 8 stayed at $12.
    assert bets == ["$12 Place(8)", "$24 Place(6)"]
