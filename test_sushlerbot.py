from main import VoteCounter
import unittest.mock as mock


def test_is_option_lowered():
    voter = VoteCounter(["TEST", "test2"])
    assert voter.is_option("test")
    assert voter.is_option("test2")
    assert voter.is_option("TEST")
    assert not voter.is_option("LOLSWAG")


def test_clear_on_no_votes():
    voter = VoteCounter(["test2"])
    assert voter.select_winner() == "clear"


def test_pick_winner_single_option():
    voter = VoteCounter(["option_1", "option_2", "option_3"])
    voter.vote("user_1", "option_1")
    assert voter.select_winner() == "option_1"


def test_pick_winner_more_votes():
    voter = VoteCounter(["option_1", "option_2", "option_3"])
    voter.vote("user_1", "option_1")
    voter.vote("user_2", "option_1")
    voter.vote("user_3", "option_2")
    assert voter.select_winner() == "option_1"


def test_pick_element_using_random():
    voter = VoteCounter(["option_1", "option_2", "option_3"])
    voter.vote("user_1", "option_1")
    voter.vote("user_2", "option_2")

    def assert_options_and_pick(options):
        assert "option_1" in options
        assert "option_2" in options
        return "option_1"
    with mock.patch('random.choice', assert_options_and_pick):
        assert voter.select_winner() == "option_1"


def test_clear():
    voter = VoteCounter(["option_1", "option_2", "option_3"])
    voter.vote("user_1", "option_1")
    voter.clear_votes()
    assert voter.select_winner() == "clear"
