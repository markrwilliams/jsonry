import pytest
import json
from jsonry import pointer


@pytest.mark.parametrize(
    'ok,expected', [
        ('~0', '~'),
        ('~1', '/'),
        ('~01', '~1'),
        ('~10', '/0'),
        ('~01', '~1'),
        ('~10', '/0'),
        ('~15', '/5'),
        ('A~0', 'A~'),
        ('A~1', 'A/'),
        ('~0A', '~A'),
        ('~1A', '/A'),
        ('A~0B', 'A~B'),
        ('A~1B', 'A/B'),
    ])
def test_unescape_succeeds(ok, expected):
    assert pointer.unescape(ok) == expected
    assert pointer.unescape(ok * 10) == expected * 10


@pytest.mark.parametrize(
    'bad', [
        ('~'),
        ('~a'),
        ('~5'),
    ])
def test_unescape_fails(bad):
    with pytest.raises(pointer.InvalidJSONPointer):
        pointer.unescape(bad)


@pytest.mark.parametrize(
    'input,number,expected', [
        (['A', 'B'], '0', 'A'),
        ({'1': 'A', 'something': 'B'}, '1', 'A'),
    ]
)
def test_numeric_accessor_succeeds(input, number, expected):
    assert pointer.numeric_accessor(input, number) == expected


EXAMPLE_OBJECT = json.loads(r'''
{
      "foo": ["bar", "baz"],
      "": 0,
      "a/b": 1,
      "c%d": 2,
      "e^f": 3,
      "g|h": 4,
      "i\\j": 5,
      "k\"l": 6,
      " ": 7,
      "m~n": 8
}
''')


@pytest.mark.parametrize(
    'path,expected', [
        ("", EXAMPLE_OBJECT),
    ])
def test_JSONPointer_succeeds(path, expected):
    ptr = pointer.JSONPointer(path)
    assert ptr.path == path
    assert ptr.get(EXAMPLE_OBJECT) == expected
