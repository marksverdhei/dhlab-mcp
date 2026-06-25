"""Tests for input validation in server.py tools."""

import inspect
import pytest
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dhlab_mcp.server import word_concordance, _WORD_CONCORDANCE_MAX_WINDOW

# The @mcp.tool() decorator wraps the function into a FunctionTool object.
# Access the underlying callable via .fn for direct testing.
_word_concordance_fn = word_concordance.fn


class TestWordConcordanceWindowValidation:
    def test_window_at_max_does_not_raise(self):
        """window == 24 should not raise — it's exactly at the limit."""
        mock_result = MagicMock()
        mock_result.__len__ = lambda self: 0
        with patch("dhlab.api.dhlab_api.word_concordance", return_value=mock_result):
            try:
                _word_concordance_fn("urn:123", "word", window=24)
            except ValueError:
                pytest.fail("window=24 should not raise ValueError")

    def test_window_over_max_raises_value_error(self):
        """window > 24 must raise ValueError before the API is called."""
        with pytest.raises(ValueError, match="24"):
            _word_concordance_fn("urn:123", "word", window=25)

    def test_window_zero_does_not_raise(self):
        """window=0 is at the low end and should not raise."""
        mock_result = MagicMock()
        mock_result.__len__ = lambda self: 0
        with patch("dhlab.api.dhlab_api.word_concordance", return_value=mock_result):
            try:
                _word_concordance_fn("urn:123", "word", window=0)
            except ValueError:
                pytest.fail("window=0 should not raise ValueError")

    def test_default_window_within_limit(self):
        """The default window value (12) must be within the allowed limit."""
        sig = inspect.signature(_word_concordance_fn)
        default_window = sig.parameters["window"].default
        assert default_window <= _WORD_CONCORDANCE_MAX_WINDOW

    def test_max_window_constant_value(self):
        assert _WORD_CONCORDANCE_MAX_WINDOW == 24

    def test_error_message_includes_limit(self):
        """The ValueError message should state the maximum allowed value."""
        with pytest.raises(ValueError) as exc_info:
            _word_concordance_fn("urn:123", "word", window=100)
        assert "24" in str(exc_info.value)

    def test_error_message_includes_actual_value(self):
        """The ValueError message should include the bad value that was passed."""
        with pytest.raises(ValueError) as exc_info:
            _word_concordance_fn("urn:123", "word", window=100)
        assert "100" in str(exc_info.value)

    def test_large_window_raises(self):
        with pytest.raises(ValueError):
            _word_concordance_fn("urn:123", "word", window=999)
