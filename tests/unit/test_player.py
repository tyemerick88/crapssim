from crapssim import Table
from crapssim.bet import PassLine
from crapssim.strategy import BetPassLine


def test_default_strategy():
    table = Table()
    table.add_player()
    assert table.players[0].strategy == BetPassLine(5)


def test_is_removable_bet():
    bet = PassLine(50)
    table = Table()
    table.add_player(500)
    table.fixed_run([(2, 2)])
    assert bet.is_removable(table) is False


def test_existing_bet():
    table = Table()
    table.add_player()
    bet_one = PassLine(50)
    table.players[0].add_bet(bet_one)
    bet_two = PassLine(50)
    table.players[0].add_bet(bet_two)

    bet_count = len(table.players[0].bets)
    bet_amount = table.players[0].bets[0].amount
    bankroll = table.players[0].bankroll
    total_bet_amount = table.players[0].total_bet_amount

    assert (bet_count, bet_amount, bankroll, total_bet_amount) == (1, 100, 0, 100)


def test_valid_bet_removal():
    table = Table()
    player = table.add_player(500)
    bet = PassLine(50)
    player.add_bet(bet)
    player.remove_bet(bet)

    bet_count = len(player.bets)
    bankroll = player.bankroll
    total_bet_amount = player.total_bet_amount

    assert (bet_count, bankroll, total_bet_amount) == (0, 500, 0)


def test_invalid_bet_removal():
    table = Table()
    player = table.add_player(500)
    bet = PassLine(50)
    player.add_bet(bet)
    table.point.number = 4
    player.remove_bet(PassLine(50))

    bet_count = len(player.bets)
    bankroll = player.bankroll
    total_bet_amount = player.total_bet_amount

    assert (bet_count, bankroll, total_bet_amount) == (1, 450, 50)


def test_add_strategy_bets_no_strategy_noop():
    table = Table()
    player = table.add_player(500)
    player.strategy = None

    bankroll_before = player.bankroll
    player.add_strategy_bets()

    assert player.bankroll == bankroll_before
    assert player.bets == []


def test_add_strategy_bets_calls_strategy_update_bets():
    class DummyStrategy:
        def __init__(self):
            self.called = False
            self.called_with = None

        def update_bets(self, player):
            self.called = True
            self.called_with = player

    table = Table()
    player = table.add_player(500)
    strategy = DummyStrategy()
    player.strategy = strategy

    player.add_strategy_bets()

    assert strategy.called is True
    assert strategy.called_with is player
