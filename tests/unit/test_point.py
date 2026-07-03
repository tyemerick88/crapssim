import pytest

from crapssim.point import Point


class DiceStub:
    def __init__(self, total: int):
        self.total = total


@pytest.mark.parametrize(
    ("number", "status"),
    [
        (None, "Off"),
        (4, "On"),
        (12, "On"),
    ],
)
def test_point_status(number, status):
    point = Point(number=number)
    assert point.status == status


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (None, "Point(number=None)"),
        (4, "Point(number=4)"),
        (12, "Point(number=12)"),
    ],
)
def test_point_repr(number, expected):
    assert repr(Point(number=number)) == expected


def test_point_hash_is_consistent_for_same_value():
    p1 = Point(number=8)
    p2 = Point(number=8)

    assert hash(p1) == hash(p2)


def test_point_hash_supports_hash_collections_for_off_and_on_states():
    points = {Point(), Point(number=5)}
    lookup = {Point(): "off", Point(number=5): "on"}

    assert Point() in points
    assert Point(number=5) in points
    assert lookup[Point()] == "off"
    assert lookup[Point(number=5)] == "on"


@pytest.mark.parametrize(
    ("number", "comparison"),
    [
        (2, 2),
        (12, 12),
        (6, "6"),
        (8, "On"),
        (8, "on"),
        (8, Point(8)),
    ],
)
def test_point_eq_supported_types(number, comparison):
    assert Point(number=number) == comparison


def test_point_eq_off_vs_int_is_false():
    assert not (Point() == 4)


@pytest.mark.parametrize("comparison", [[], {}, 1.5, object(), True])
def test_point_eq_raises_for_unsupported_types(comparison):
    with pytest.raises(NotImplementedError):
        _ = Point(number=8) == comparison


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (Point(8), 6, True),
        (Point(8), "6", True),
        (Point(8), Point(6), True),
        (Point(8), 8, False),
        (Point(8), "8", False),
        (Point(8), Point(8), False),
    ],
)
def test_point_gt_supported_paths(left, right, expected):
    assert (left > right) is expected


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (Point(4), 6, True),
        (Point(4), "10", True),
        (Point(4), Point(6), True),
        (Point(4), 4, False),
        (Point(4), "4", False),
        (Point(4), Point(4), False),
    ],
)
def test_point_lt_supported_paths(left, right, expected):
    assert (left < right) is expected


@pytest.mark.parametrize("comparison", [[], {}, 1.5, object()])
def test_point_gt_raises_for_unsupported_types(comparison):
    with pytest.raises(NotImplementedError):
        _ = Point(number=8) > comparison


@pytest.mark.parametrize("comparison", [[], {}, 1.5, object()])
def test_point_lt_raises_for_unsupported_types(comparison):
    with pytest.raises(NotImplementedError):
        _ = Point(number=8) < comparison


def test_point_gt_raises_when_self_is_off():
    with pytest.raises(NotImplementedError):
        _ = Point() > 5


def test_point_lt_raises_when_self_is_off():
    with pytest.raises(NotImplementedError):
        _ = Point() < 5


def test_point_gt_raises_when_other_point_is_off():
    with pytest.raises(NotImplementedError):
        _ = Point(8) > Point()


def test_point_lt_raises_when_other_point_is_off():
    with pytest.raises(NotImplementedError):
        _ = Point(4) < Point()


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (Point(6), 6, True),
        (Point(8), 4, True),
        (Point(4), 8, False),
        (Point(8), Point(8), True),
        (Point(8), Point(4), True),
        (Point(4), Point(8), False),
        (Point(8), "8", True),
    ],
)
def test_point_ge_supported_paths(left, right, expected):
    assert (left >= right) is expected


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [
        (Point(6), 6, True),
        (Point(4), 8, True),
        (Point(8), 4, False),
        (Point(8), Point(8), True),
        (Point(4), Point(8), True),
        (Point(8), Point(4), False),
        (Point(8), "8", True),
    ],
)
def test_point_le_supported_paths(left, right, expected):
    assert (left <= right) is expected


def test_point_ge_raises_when_self_is_off():
    with pytest.raises(NotImplementedError):
        _ = Point() >= 5


def test_point_le_raises_when_self_is_off():
    with pytest.raises(NotImplementedError):
        _ = Point() <= 5


def test_update_sets_point_when_off_and_roll_is_default_point_number():
    point = Point()
    point.update(DiceStub(4))

    assert point.number == 4
    assert point.status == "On"


def test_update_does_not_set_point_when_off_and_roll_is_not_default_point_number():
    point = Point()
    point.update(DiceStub(2))

    assert point.number is None
    assert point.status == "Off"


def test_update_clears_point_when_on_and_roll_matches_point():
    point = Point(number=6)
    point.update(DiceStub(6))

    assert point.number is None
    assert point.status == "Off"


def test_update_clears_point_when_on_and_roll_is_seven():
    point = Point(number=6)
    point.update(DiceStub(7))

    assert point.number is None
    assert point.status == "Off"


def test_update_leaves_point_when_on_and_roll_is_neither_point_nor_seven():
    point = Point(number=6)
    point.update(DiceStub(8))

    assert point.number == 6
    assert point.status == "On"


def test_update_supports_custom_point_numbers_for_crapless_like_tables():
    point = Point()
    point.update(DiceStub(2), point_numbers=[2, 3, 11, 12])

    assert point.number == 2
    assert point.status == "On"


def test_update_with_empty_custom_point_numbers_falls_back_to_default_point_numbers():
    point = Point()
    point.update(DiceStub(4), point_numbers=[])

    assert point.number == 4
    assert point.status == "On"


def test_update_multiple_rolls_sequence_transitions_between_on_and_off():
    point = Point()

    point.update(DiceStub(9))
    assert point.number == 9
    assert point.status == "On"

    point.update(DiceStub(5))
    assert point.number == 9
    assert point.status == "On"

    point.update(DiceStub(7))
    assert point.number is None
    assert point.status == "Off"
