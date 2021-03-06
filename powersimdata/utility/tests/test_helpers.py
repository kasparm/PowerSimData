import pytest

from powersimdata.utility.helpers import (
    CommandBuilder,
    MemoryCache,
    PrintManager,
    cache_key,
)


def test_print_is_disabled(capsys):
    pm = PrintManager()
    pm.block_print()
    print("printout are disabled")
    captured = capsys.readouterr()
    assert captured.out == ""

    pm.enable_print()
    print("printout are enabled")
    captured = capsys.readouterr()
    assert captured.out == "printout are enabled\n"


def test_cache_key_valid_types():
    key1 = cache_key(["foo", "bar"], 4, "other")
    assert (("foo", "bar"), 4, "other") == key1

    key2 = cache_key(True)
    assert (True,) == key2

    key3 = cache_key({1, 2, 2, 3})
    assert ((1, 2, 3),) == key3

    key4 = cache_key(None)
    assert ("null",) == key4


def test_no_collision():
    key1 = cache_key([["foo"], ["bar"]])
    key2 = cache_key([[["foo"], ["bar"]]])
    key3 = cache_key([["foo"], "bar"])
    keys = [key1, key2, key3]
    assert len(keys) == len(set(keys))


def test_cache_key_unsupported_type():
    with pytest.raises(ValueError):
        cache_key(object())


def test_cache_key_distinct_types():
    assert cache_key(4) != cache_key("4")


def test_mem_cache_put_dict():
    cache = MemoryCache()
    key = cache_key(["foo", "bar"], 4, "other")
    obj = {"key1": 42}
    cache.put(key, obj)
    assert cache.get(key) == obj


def test_mem_cache_get_returns_copy():
    cache = MemoryCache()
    key = cache_key("foo", 4)
    obj = {"key1": 42}
    cache.put(key, obj)
    assert id(cache.get(key)) != id(obj)


def test_copy_command():
    expected = r"\cp -p source dest"
    command = CommandBuilder.copy("source", "dest")
    assert expected == command

    expected = r"\cp -Rp source dest"
    command = CommandBuilder.copy("source", "dest", recursive=True)
    assert expected == command

    expected = r"\cp -up source dest"
    command = CommandBuilder.copy("source", "dest", update=True)
    assert expected == command

    expected = r"\cp -Rup source dest"
    command = CommandBuilder.copy("source", "dest", recursive=True, update=True)
    assert expected == command


def test_remove_command():
    expected = "rm target"
    command = CommandBuilder.remove("target")
    assert expected == command

    expected = "rm -r target"
    command = CommandBuilder.remove("target", recursive=True)
    assert expected == command

    expected = "rm -rf target"
    command = CommandBuilder.remove("target", recursive=True, force=True)
    assert expected == command
