"""Tests for dhlab_mcp.server — MCP tool functions and CLI argument parser."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_corpus(records: list[dict] | None = None):
    """Return a mock dhlab.Corpus with a .corpus DataFrame-like."""
    corpus = MagicMock()
    if records is None:
        corpus.corpus = None
    else:
        df = MagicMock()
        df.to_json.return_value = json.dumps(records)
        df.__len__ = lambda self: len(records)
        corpus.corpus = df
    return corpus


# ---------------------------------------------------------------------------
# search_texts
# ---------------------------------------------------------------------------

class TestSearchTexts:
    def test_returns_json_on_success(self):
        from dhlab_mcp.server import search_texts
        mock_corpus = _make_corpus([{"title": "Aftenposten"}])
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.return_value = mock_corpus
            result = search_texts.fn("oslo")
        assert isinstance(result, str)
        assert "Aftenposten" in result

    def test_no_results_returns_message(self):
        from dhlab_mcp.server import search_texts
        mock_corpus = _make_corpus(None)
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.return_value = mock_corpus
            result = search_texts.fn("xyz")
        assert "No results found" in result

    def test_passes_query_to_corpus(self):
        from dhlab_mcp.server import search_texts
        mock_corpus = _make_corpus([])
        mock_corpus.corpus = None
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.return_value = mock_corpus
            search_texts.fn("søk her", limit=5, media_type="digibok")
        call_kwargs = mock_dhlab.Corpus.call_args.kwargs
        assert call_kwargs["fulltext"] == "søk her"
        assert call_kwargs["limit"] == 5
        assert call_kwargs["doctype"] == "digibok"

    def test_exception_returns_error_string(self):
        from dhlab_mcp.server import search_texts
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.side_effect = RuntimeError("API down")
            result = search_texts.fn("test")
        assert "Error" in result
        assert "API down" in result

    def test_year_range_passed_when_provided(self):
        from dhlab_mcp.server import search_texts
        mock_corpus = _make_corpus(None)
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.return_value = mock_corpus
            search_texts.fn("krig", from_year=1940, to_year=1945)
        call_kwargs = mock_dhlab.Corpus.call_args.kwargs
        assert call_kwargs["from_year"] == 1940
        assert call_kwargs["to_year"] == 1945

    def test_year_omitted_when_none(self):
        from dhlab_mcp.server import search_texts
        mock_corpus = _make_corpus(None)
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.return_value = mock_corpus
            search_texts.fn("fred")
        call_kwargs = mock_dhlab.Corpus.call_args.kwargs
        assert "from_year" not in call_kwargs
        assert "to_year" not in call_kwargs


# ---------------------------------------------------------------------------
# ngram_frequencies
# ---------------------------------------------------------------------------

class TestNgramFrequencies:
    def _make_ng(self, data: dict | None = None):
        ng = MagicMock()
        if data is None:
            ng.frame = None
        else:
            df = MagicMock()
            df.to_json.return_value = json.dumps(data)
            ng.frame = df
        return ng

    def test_book_corpus_uses_ngrambook(self):
        from dhlab_mcp.server import ngram_frequencies
        ng = self._make_ng({"1900": 0.001})
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.NgramBook.return_value = ng
            result = ngram_frequencies.fn(["bok"])
        mock_dhlab.NgramBook.assert_called_once()
        assert "1900" in result

    def test_avis_corpus_uses_ngramnews(self):
        from dhlab_mcp.server import ngram_frequencies
        ng = self._make_ng({"1950": 0.002})
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.NgramNews.return_value = ng
            ngram_frequencies.fn(["avis"], corpus="avis")
        mock_dhlab.NgramNews.assert_called_once()

    def test_no_data_returns_message(self):
        from dhlab_mcp.server import ngram_frequencies
        ng = self._make_ng(None)
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.NgramBook.return_value = ng
            result = ngram_frequencies.fn(["ghost"])
        assert "No frequency data" in result

    def test_exception_returns_error_string(self):
        from dhlab_mcp.server import ngram_frequencies
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.NgramBook.side_effect = ConnectionError("timeout")
            result = ngram_frequencies.fn(["word"])
        assert "Error" in result


# ---------------------------------------------------------------------------
# lookup_word_forms
# ---------------------------------------------------------------------------

class TestLookupWordForms:
    def test_returns_json_on_success(self):
        from dhlab_mcp.server import lookup_word_forms
        forms_df = MagicMock()
        forms_df.to_json.return_value = '[{"form": "løpe"}]'
        word_form = MagicMock()
        word_form.forms = forms_df
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.WordForm.return_value = word_form
            result = lookup_word_forms.fn("løper")
        assert "løpe" in result

    def test_no_forms_returns_message(self):
        from dhlab_mcp.server import lookup_word_forms
        word_form = MagicMock()
        word_form.forms = None
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.WordForm.return_value = word_form
            result = lookup_word_forms.fn("xyz")
        assert "No forms found" in result

    def test_exception_returns_error_string(self):
        from dhlab_mcp.server import lookup_word_forms
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.WordForm.side_effect = ValueError("bad word")
            result = lookup_word_forms.fn("??")
        assert "Error" in result


# ---------------------------------------------------------------------------
# lookup_word_lemma
# ---------------------------------------------------------------------------

class TestLookupWordLemma:
    def test_returns_json_on_success(self):
        from dhlab_mcp.server import lookup_word_lemma
        lemmas_df = MagicMock()
        lemmas_df.to_json.return_value = '[{"lemma": "løpe"}]'
        word_lemma = MagicMock()
        word_lemma.lemmas = lemmas_df
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.WordLemma.return_value = word_lemma
            result = lookup_word_lemma.fn("løper")
        assert "løpe" in result

    def test_no_lemmas_returns_message(self):
        from dhlab_mcp.server import lookup_word_lemma
        word_lemma = MagicMock()
        word_lemma.lemmas = None
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.WordLemma.return_value = word_lemma
            result = lookup_word_lemma.fn("xyz")
        assert "No lemma found" in result

    def test_exception_returns_error_string(self):
        from dhlab_mcp.server import lookup_word_lemma
        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.WordLemma.side_effect = RuntimeError("oops")
            result = lookup_word_lemma.fn("word")
        assert "Error" in result


# ---------------------------------------------------------------------------
# main() argument parser
# ---------------------------------------------------------------------------

class TestMainArgParser:
    def _build_parser(self):
        # Use the real production parser — tests previously mirrored the
        # argparse setup inline, which drifted from main() silently when
        # flags were added or defaults changed.
        from dhlab_mcp.server import _make_parser
        return _make_parser()

    def test_default_transport_is_stdio(self):
        parser = self._build_parser()
        args = parser.parse_args([])
        assert args.transport == "stdio"

    def test_http_transport_accepted(self):
        parser = self._build_parser()
        args = parser.parse_args(["--transport", "http"])
        assert args.transport == "http"

    def test_sse_transport_accepted(self):
        parser = self._build_parser()
        args = parser.parse_args(["--transport", "sse"])
        assert args.transport == "sse"

    def test_invalid_transport_rejected(self):
        parser = self._build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--transport", "websocket"])

    def test_default_host(self):
        parser = self._build_parser()
        args = parser.parse_args([])
        assert args.host == "127.0.0.1"

    def test_custom_host_accepted(self):
        parser = self._build_parser()
        args = parser.parse_args(["--host", "0.0.0.0"])
        assert args.host == "0.0.0.0"

    def test_default_port(self):
        parser = self._build_parser()
        args = parser.parse_args([])
        assert args.port == 8000

    def test_custom_port_accepted(self):
        parser = self._build_parser()
        args = parser.parse_args(["--port", "9090"])
        assert args.port == 9090

    def test_main_dispatches_http_with_host_and_port(self):
        # End-to-end main() dispatch — covers the http/sse branch which
        # passes transport+host+port through to mcp.run.
        from dhlab_mcp.server import main
        from unittest.mock import patch
        with patch("sys.argv", ["dhlab-mcp", "--transport", "http",
                                 "--host", "0.0.0.0", "--port", "9090"]), \
             patch("dhlab_mcp.server.mcp.run") as mock_run:
            main()
        mock_run.assert_called_once_with(transport="http", host="0.0.0.0", port=9090)

    def test_main_dispatches_stdio_with_no_args(self):
        # End-to-end main() dispatch — covers the stdio branch which is
        # the default and takes no transport/host/port kwargs.
        from dhlab_mcp.server import main
        from unittest.mock import patch
        with patch("sys.argv", ["dhlab-mcp"]), \
             patch("dhlab_mcp.server.mcp.run") as mock_run:
            main()
        mock_run.assert_called_once_with()
