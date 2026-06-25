"""Extra tests for dhlab_mcp.server — find_concordances, word_concordance,
find_collocations, search_images, get_corpus_statistics."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch


# ---------------------------------------------------------------------------
# find_concordances
# ---------------------------------------------------------------------------

class TestFindConcordances:
    def test_returns_json_on_success(self):
        from dhlab_mcp.server import find_concordances

        mock_concs = MagicMock()
        mock_concs.concordance = MagicMock()
        mock_concs.concordance.to_json.return_value = '[{"word": "oslo"}]'
        mock_concs.concordance.__len__ = lambda s: 1

        mock_corpus = MagicMock()
        mock_corpus.corpus.__len__ = lambda s: 1
        mock_corpus.conc.return_value = mock_concs

        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.from_identifiers.return_value = mock_corpus
            result = find_concordances.fn("urn:NBN:123", "oslo")

        assert "oslo" in result

    def test_empty_corpus_returns_message(self):
        from dhlab_mcp.server import find_concordances

        mock_corpus = MagicMock()
        mock_corpus.corpus.__len__ = lambda s: 0

        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.from_identifiers.return_value = mock_corpus
            result = find_concordances.fn("urn:NBN:999", "word")

        assert "No document found" in result

    def test_no_concordances_returns_message(self):
        from dhlab_mcp.server import find_concordances

        mock_concs = MagicMock()
        mock_concs.concordance = None

        mock_corpus = MagicMock()
        mock_corpus.corpus.__len__ = lambda s: 1
        mock_corpus.conc.return_value = mock_concs

        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.from_identifiers.return_value = mock_corpus
            result = find_concordances.fn("urn:NBN:123", "missingword")

        assert "No concordances found" in result

    def test_exception_returns_error_string(self):
        from dhlab_mcp.server import find_concordances

        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.from_identifiers.side_effect = RuntimeError("api down")
            result = find_concordances.fn("urn:NBN:x", "word")

        assert "Error" in result

    def test_passes_window_and_limit(self):
        from dhlab_mcp.server import find_concordances

        mock_concs = MagicMock()
        mock_concs.concordance = MagicMock()
        mock_concs.concordance.to_json.return_value = '[]'
        mock_concs.concordance.__len__ = lambda s: 0

        mock_corpus = MagicMock()
        mock_corpus.corpus.__len__ = lambda s: 1
        mock_corpus.conc.return_value = mock_concs

        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.from_identifiers.return_value = mock_corpus
            find_concordances.fn("urn:NBN:123", "oslo", window=10, limit=50)

        mock_corpus.conc.assert_called_once_with(words="oslo", window=10, limit=50)


# ---------------------------------------------------------------------------
# word_concordance
# ---------------------------------------------------------------------------

class TestWordConcordance:
    def test_returns_json_on_success(self):
        from dhlab_mcp.server import word_concordance

        mock_df = MagicMock()
        mock_df.to_json.return_value = '[{"before":"hello","target":"oslo","after":"world"}]'
        mock_df.__len__ = lambda s: 1

        with patch("dhlab.api.dhlab_api.word_concordance", return_value=mock_df):
            result = word_concordance.fn("urn:NBN:123", "oslo")

        assert "oslo" in result

    def test_no_results_returns_message(self):
        from dhlab_mcp.server import word_concordance

        with patch("dhlab.api.dhlab_api.word_concordance", return_value=None):
            result = word_concordance.fn("urn:NBN:123", "word")

        assert "No concordances found" in result

    def test_exception_returns_error_string(self):
        from dhlab_mcp.server import word_concordance

        with patch("dhlab.api.dhlab_api.word_concordance", side_effect=Exception("fail")):
            result = word_concordance.fn("urn:NBN:x", "word")

        assert "Error" in result

    def test_passes_urn_as_list(self):
        from dhlab_mcp.server import word_concordance

        mock_df = MagicMock()
        mock_df.__len__ = lambda s: 0

        with patch("dhlab.api.dhlab_api.word_concordance", return_value=mock_df) as mock_fn:
            word_concordance.fn("urn:NBN:42", "test", window=8, limit=20)

        call_kwargs = mock_fn.call_args
        assert call_kwargs.kwargs["urn"] == ["urn:NBN:42"]


# ---------------------------------------------------------------------------
# find_collocations
# ---------------------------------------------------------------------------

class TestFindCollocations:
    def test_returns_json_on_success(self):
        from dhlab_mcp.server import find_collocations

        mock_colls = MagicMock()
        mock_colls.coll = MagicMock()
        mock_colls.coll.to_json.return_value = '[{"word": "fjord", "freq": 42}]'
        mock_colls.coll.__len__ = lambda s: 1

        mock_corpus = MagicMock()
        mock_corpus.corpus.__len__ = lambda s: 1
        mock_corpus.coll.return_value = mock_colls

        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.from_identifiers.return_value = mock_corpus
            result = find_collocations.fn("urn:NBN:123", "norge")

        assert "fjord" in result

    def test_empty_corpus_returns_message(self):
        from dhlab_mcp.server import find_collocations

        mock_corpus = MagicMock()
        mock_corpus.corpus.__len__ = lambda s: 0

        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.from_identifiers.return_value = mock_corpus
            result = find_collocations.fn("urn:NBN:999", "word")

        assert "No document found" in result

    def test_no_collocations_returns_message(self):
        from dhlab_mcp.server import find_collocations

        mock_colls = MagicMock()
        mock_colls.coll = None

        mock_corpus = MagicMock()
        mock_corpus.corpus.__len__ = lambda s: 1
        mock_corpus.coll.return_value = mock_colls

        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.from_identifiers.return_value = mock_corpus
            result = find_collocations.fn("urn:NBN:123", "rareword")

        assert "No collocations found" in result

    def test_exception_returns_error_string(self):
        from dhlab_mcp.server import find_collocations

        with patch("dhlab_mcp.server.dhlab") as mock_dhlab:
            mock_dhlab.Corpus.from_identifiers.side_effect = Exception("boom")
            result = find_collocations.fn("urn:NBN:x", "word")

        assert "Error" in result


# ---------------------------------------------------------------------------
# search_images
# ---------------------------------------------------------------------------

class TestSearchImages:
    def test_returns_json_on_success(self):
        from dhlab_mcp.server import search_images

        with patch("dhlab.images.nbpictures.find_urls", return_value=["http://example.com/img.jpg"]):
            result = search_images.fn("fjord")

        data = json.loads(result)
        assert len(data) == 1
        assert "example.com" in data[0]

    def test_empty_results_returns_message(self):
        from dhlab_mcp.server import search_images

        with patch("dhlab.images.nbpictures.find_urls", return_value=[]):
            result = search_images.fn("xyzabc123")

        assert "No images found" in result

    def test_none_result_returns_message(self):
        from dhlab_mcp.server import search_images

        with patch("dhlab.images.nbpictures.find_urls", return_value=None):
            result = search_images.fn("xyzabc123")

        assert "No images found" in result

    def test_exception_returns_error_string(self):
        from dhlab_mcp.server import search_images

        with patch("dhlab.images.nbpictures.find_urls", side_effect=Exception("api error")):
            result = search_images.fn("fjord")

        assert "Error" in result

    def test_passes_query_and_limit(self):
        from dhlab_mcp.server import search_images

        with patch("dhlab.images.nbpictures.find_urls", return_value=[]) as mock_fn:
            search_images.fn("oslo", limit=5)

        mock_fn.assert_called_once_with(term="oslo", number=5, mediatype="bilder")

    def test_signature_does_not_accept_year_params(self):
        """Regression: from_year / to_year were previously declared on the
        tool but silently ignored by the underlying find_urls (which has no
        date filter). The signature now omits them so MCP clients see the
        accurate API surface instead of dead parameters."""
        import inspect
        from dhlab_mcp.server import search_images
        sig = inspect.signature(search_images.fn)
        assert "from_year" not in sig.parameters
        assert "to_year" not in sig.parameters


# ---------------------------------------------------------------------------
# get_corpus_statistics
# ---------------------------------------------------------------------------

class TestGetCorpusStatistics:
    def test_returns_json_on_success(self):
        from dhlab_mcp.server import get_corpus_statistics

        mock_meta = MagicMock()
        mock_meta.to_json.return_value = '[{"urn":"urn:NBN:1","title":"book"}]'
        mock_meta.__len__ = lambda s: 1

        with patch("dhlab.api.dhlab_api.get_metadata", return_value=mock_meta):
            result = get_corpus_statistics.fn(["urn:NBN:1"])

        assert "urn:NBN:1" in result

    def test_empty_metadata_returns_message(self):
        from dhlab_mcp.server import get_corpus_statistics

        mock_meta = MagicMock()
        mock_meta.__len__ = lambda s: 0

        with patch("dhlab.api.dhlab_api.get_metadata", return_value=mock_meta):
            result = get_corpus_statistics.fn(["urn:NBN:999"])

        assert "No metadata available" in result

    def test_none_result_returns_message(self):
        from dhlab_mcp.server import get_corpus_statistics

        with patch("dhlab.api.dhlab_api.get_metadata", return_value=None):
            result = get_corpus_statistics.fn([])

        assert "No metadata available" in result

    def test_exception_returns_error_string(self):
        from dhlab_mcp.server import get_corpus_statistics

        with patch("dhlab.api.dhlab_api.get_metadata", side_effect=Exception("timeout")):
            result = get_corpus_statistics.fn(["urn:NBN:x"])

        assert "Error" in result
