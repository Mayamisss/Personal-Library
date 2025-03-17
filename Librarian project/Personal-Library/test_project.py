import pytest
from project import get_title, get_rating, get_progress, main
from unittest.mock import patch, MagicMock

#######
@pytest.mark.parametrize("input_value,expected",[
    ("HoneyBee", "HoneyBee"),
    ("/", None)
])

def test_get_title(input_value,expected):
    with patch("builtins.input", side_effect =[input_value]):
        result = get_title()
        assert result == expected
#######
@pytest.mark.parametrize("input_value,expected",[
    ("5", 5),
    ("/", None),
])

def test_get_rating(input_value,expected):
    with patch("builtins.input", side_effect =[input_value]):
         result = get_rating()
         assert result == expected

#######
@pytest.mark.parametrize("input_value,expected",[
    ("1", "Not started"),
    ("2", "In-progress"),
    ("3", "DNF"),
    ("/", None),
])

def test_get_progress(input_value,expected):
     with patch("builtins.input", side_effect=[input_value]):
        result = get_progress("Sample Title")
        assert result == expected

#######