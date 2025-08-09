from scratchbot.commands import parse_slash_command


def test_parse_apply():
    assert parse_slash_command("/scratchbot apply all") == ("apply", "all")


def test_parse_dismiss():
    assert parse_slash_command("/scratchbot dismiss") == ("dismiss", "")


def test_parse_mode():
    assert parse_slash_command("/scratchbot mode batch") == ("mode", "batch")


def test_parse_none():
    assert parse_slash_command("hello") is None
