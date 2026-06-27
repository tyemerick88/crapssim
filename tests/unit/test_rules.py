import pytest

from crapssim.point import Point
from crapssim.rules import BaseRules, ClassicRules, CraplessRules


class DummyDice:
    def __init__(self, total: int):
        self.total = total


@pytest.fixture
def base_rules():
    return BaseRules()


@pytest.fixture
def classic_rules():
    return ClassicRules()


@pytest.fixture
def crapless_rules():
    return CraplessRules()


def test_base_point_numbers(base_rules):
    assert base_rules.point_numbers() == []


def test_base_valid_point_bet_numbers_delegates_to_point_numbers():
    class CustomRules(BaseRules):
        def point_numbers(self) -> list[int]:
            return [4, 6]

    rules = CustomRules()
    assert rules.valid_point_bet_numbers() == [4, 6]


def test_base_come_out_pushers(base_rules):
    assert base_rules.come_out_pushers() == []


def test_base_point_winners_none_returns_empty(base_rules):
    assert base_rules.point_winners(None) == []


@pytest.mark.parametrize("point", [2, 4, 10, 12])
def test_base_point_winners_number_returns_number(base_rules, point):
    assert base_rules.point_winners(point) == [point]


@pytest.mark.parametrize("point", [None, 4, 6, 10])
def test_base_point_losers_always_seven(base_rules, point):
    assert base_rules.point_losers(point) == [7]


@pytest.mark.parametrize("point", [None, 2, 4, 12])
def test_base_point_pushers_always_empty(base_rules, point):
    assert base_rules.point_pushers(point) == []


def test_should_set_point_true_when_off_and_total_is_point_number(classic_rules):
    assert classic_rules.should_set_point(Point(), DummyDice(4)) is True


def test_should_set_point_false_when_off_and_total_not_point_number(classic_rules):
    assert classic_rules.should_set_point(Point(), DummyDice(7)) is False


def test_should_set_point_false_when_already_on(classic_rules):
    assert classic_rules.should_set_point(Point(number=4), DummyDice(4)) is False


def test_should_reset_shooter_true_when_on_and_seven(base_rules):
    assert base_rules.should_reset_shooter(Point(number=6), DummyDice(7)) is True


def test_should_reset_shooter_false_when_on_and_not_seven(base_rules):
    assert base_rules.should_reset_shooter(Point(number=6), DummyDice(6)) is False


def test_should_reset_shooter_false_when_off(base_rules):
    assert base_rules.should_reset_shooter(Point(), DummyDice(7)) is False


def test_base_allow_dont_pass(base_rules):
    assert base_rules.allow_dont_pass() is True


def test_base_allow_dont_come(base_rules):
    assert base_rules.allow_dont_come() is True


def test_classic_point_numbers(classic_rules):
    assert classic_rules.point_numbers() == [4, 5, 6, 8, 9, 10]


def test_classic_come_out_winners(classic_rules):
    assert classic_rules.come_out_winners() == [7, 11]


def test_classic_come_out_losers(classic_rules):
    assert classic_rules.come_out_losers() == [2, 3, 12]


def test_classic_inherits_dont_side_allowed(classic_rules):
    assert classic_rules.allow_dont_pass() is True
    assert classic_rules.allow_dont_come() is True


def test_classic_inherits_come_out_pushers(classic_rules):
    assert classic_rules.come_out_pushers() == []


def test_crapless_point_numbers(crapless_rules):
    assert crapless_rules.point_numbers() == [2, 3, 4, 5, 6, 8, 9, 10, 11, 12]


def test_crapless_come_out_winners(crapless_rules):
    assert crapless_rules.come_out_winners() == [7]


def test_crapless_come_out_losers(crapless_rules):
    assert crapless_rules.come_out_losers() == []


def test_crapless_disallows_dont_side(crapless_rules):
    assert crapless_rules.allow_dont_pass() is False
    assert crapless_rules.allow_dont_come() is False


def test_crapless_should_set_point_with_craps_numbers(crapless_rules):
    assert crapless_rules.should_set_point(Point(), DummyDice(2)) is True
    assert crapless_rules.should_set_point(Point(), DummyDice(11)) is True


def test_cross_variant_differences(classic_rules, crapless_rules):
    assert 11 in classic_rules.come_out_winners()
    assert 11 not in crapless_rules.come_out_winners()
    assert {2, 3, 11, 12}.issubset(set(crapless_rules.point_numbers()))
    assert {2, 3, 11, 12}.isdisjoint(set(classic_rules.point_numbers()))
