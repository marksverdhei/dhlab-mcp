"""FastMCP server for DHLAB (National Library of Norway Digital Humanities Lab)."""

from fastmcp import FastMCP
import dhlab

# Initialize FastMCP server
mcp = FastMCP("dhlab-mcp")


@mcp.tool()
def search_texts(
    query: str,
    limit: int = 10,
    from_year: int | None = None,
    to_year: int | None = None,
    media_type: str = "digavis",
) -> str:
    """Search for texts in the National Library's digital collection.

    Args:
        query: Search query string
        limit: Maximum number of results to return (default: 10)
        from_year: Start year for search period (optional)
        to_year: End year for search period (optional)
        media_type: Type of media to search. Options: 'digavis' (newspapers), 'digibok' (books),
                   'digitidsskrift' (journals). Default: 'digavis'

    Returns:
        JSON string containing search results with metadata
    """
    try:
        # Build search parameters using correct Corpus API
        params = {
            "fulltext": query,
            "limit": limit,
            "doctype": media_type
        }
        if from_year:
            params["from_year"] = from_year
        if to_year:
            params["to_year"] = to_year

        # Perform search using dhlab
        corpus = dhlab.Corpus(**params)

        # Return corpus information
        if hasattr(corpus, 'corpus') and corpus.corpus is not None:
            return corpus.corpus.to_json(orient='records', force_ascii=False)
        return "No results found"
    except Exception as e:
        return f"Error searching texts: {str(e)}"


@mcp.tool()
def ngram_frequencies(
    words: list[str],
    corpus: str = "bok",
    from_year: int = 1810,
    to_year: int = 2020,
    smooth: int = 1,
) -> str:
    """Get word frequency trends over time using NGram analysis.

    Args:
        words: List of words to analyze
        corpus: Corpus type. Options: 'bok' (books), 'avis' (newspapers). Default: 'bok'
        from_year: Start year (default: 1810)
        to_year: End year (default: 2020)
        smooth: Smoothing parameter for the frequency curve (default: 1)

    Returns:
        JSON string containing frequency data over time
    """
    try:
        if corpus == "avis":
            ng = dhlab.NgramNews(words, from_year=from_year, to_year=to_year, smooth=smooth)
        else:
            ng = dhlab.NgramBook(words, from_year=from_year, to_year=to_year, smooth=smooth)

        if hasattr(ng, 'frame') and ng.frame is not None:
            return ng.frame.to_json(orient='index', force_ascii=False)
        return "No frequency data available"
    except Exception as e:
        return f"Error getting ngram frequencies: {str(e)}"


@mcp.tool()
def find_concordances(
    urn: str,
    word: str,
    window: int = 25,
    limit: int = 100,
) -> str:
    """Find concordances (contexts) for a word in a specific document.

    Args:
        urn: URN identifier for the document
        word: Word to find concordances for
        window: Number of words before and after the match (default: 25)
        limit: Maximum number of concordances to return (default: 100)

    Returns:
        JSON string containing concordance results
    """
    try:
        # Create corpus from URN
        corpus = dhlab.Corpus.from_identifiers([urn])

        if len(corpus.corpus) == 0:
            return f"No document found for URN: {urn}"

        # Get concordances using corpus method
        concs = corpus.conc(words=word, window=window, limit=limit)

        if concs.concordance is not None and len(concs.concordance) > 0:
            return concs.concordance.to_json(orient='records', force_ascii=False)
        return "No concordances found"
    except Exception as e:
        return f"Error finding concordances: {str(e)}"


_WORD_CONCORDANCE_MAX_WINDOW = 24


@mcp.tool()
def word_concordance(
    urn: str,
    word: str,
    window: int = 12,
    limit: int = 100,
) -> str:
    """Find concordances with structured output (no HTML formatting).

    Returns clean format with separate before/target/after fields instead of HTML-formatted text.
    This is useful for programmatic analysis where you need the matched word separated from context.

    Args:
        urn: URN identifier for the document
        word: Word to find concordances for
        window: Number of words before and after the match (default: 12, max: 24)
        limit: Maximum number of concordances to return (default: 100)

    Returns:
        JSON string containing structured concordance results with fields:
        - dhlabid: Document identifier
        - before: Text before the matched word
        - target: The matched word itself
        - after: Text after the matched word

    Raises:
        ValueError: If window exceeds the maximum allowed value of 24.
    """
    if window > _WORD_CONCORDANCE_MAX_WINDOW:
        raise ValueError(
            f"window must be at most {_WORD_CONCORDANCE_MAX_WINDOW}, got {window}"
        )
    try:
        from dhlab.api.dhlab_api import word_concordance as dhlab_word_concordance

        # Call dhlab's word_concordance method directly
        # Note: urn parameter expects a list, words parameter expects a list
        result = dhlab_word_concordance(
            urn=[urn],
            words=[word],
            before=window,
            after=window,
            limit=limit
        )

        if result is not None and len(result) > 0:
            return result.to_json(orient='records', force_ascii=False)
        return "No concordances found"
    except Exception as e:
        return f"Error finding word concordances: {str(e)}"


@mcp.tool()
def find_collocations(
    urn: str,
    word: str,
    window: int = 5,
    limit: int = 100,
) -> str:
    """Find collocations (words that appear near the target word) in a document.

    Args:
        urn: URN identifier for the document
        word: Target word to find collocations for
        window: Size of context window (default: 5)
        limit: Maximum number of collocations to return (default: 100)

    Returns:
        JSON string containing collocation statistics
    """
    try:
        # Create corpus from URN
        corpus = dhlab.Corpus.from_identifiers([urn])

        if len(corpus.corpus) == 0:
            return f"No document found for URN: {urn}"

        # Get collocations using corpus method
        colls = corpus.coll(words=word, before=window, after=window)

        if colls.coll is not None and len(colls.coll) > 0:
            return colls.coll.to_json(orient='records', force_ascii=False)
        return "No collocations found"
    except Exception as e:
        return f"Error finding collocations: {str(e)}"


@mcp.tool()
def lookup_word_forms(word: str) -> str:
    """Look up different forms of a Norwegian word.

    Args:
        word: The word to look up

    Returns:
        JSON string containing different word forms
    """
    try:
        word_form = dhlab.WordForm(word)

        if hasattr(word_form, 'forms') and word_form.forms is not None:
            return word_form.forms.to_json(orient='records', force_ascii=False)
        return f"No forms found for word: {word}"
    except Exception as e:
        return f"Error looking up word forms: {str(e)}"


@mcp.tool()
def lookup_word_lemma(word: str) -> str:
    """Look up the lemma (base form) of a Norwegian word.

    Args:
        word: The word to look up

    Returns:
        JSON string containing lemma information
    """
    try:
        word_lemma = dhlab.WordLemma(word)

        if hasattr(word_lemma, 'lemmas') and word_lemma.lemmas is not None:
            return word_lemma.lemmas.to_json(orient='records', force_ascii=False)
        return f"No lemma found for word: {word}"
    except Exception as e:
        return f"Error looking up word lemma: {str(e)}"


@mcp.tool()
def search_images(
    query: str,
    limit: int = 10,
) -> str:
    """Search for images in the National Library's digital collection.

    Args:
        query: Search query string
        limit: Maximum number of results (default: 10)

    Returns:
        JSON string containing image search results with URLs

    Note:
        The underlying ``dhlab.images.nbpictures.find_urls`` API does not
        currently support year filtering. If date scoping is added upstream,
        ``from_year`` / ``to_year`` parameters can be re-added here.
    """
    try:
        from dhlab.images.nbpictures import find_urls

        # find_urls returns a list of URLs
        results = find_urls(term=query, number=limit, mediatype="bilder")

        if results is not None and len(results) > 0:
            import json
            return json.dumps(results, ensure_ascii=False)
        return "No images found"
    except Exception as e:
        return f"Error searching images: {str(e)}"


@mcp.tool()
def get_corpus_statistics(urns: list[str]) -> str:
    """Get statistical information about a corpus of documents.

    Args:
        urns: List of URN identifiers for documents

    Returns:
        JSON string containing corpus statistics
    """
    try:
        from dhlab.api.dhlab_api import get_metadata

        metadata = get_metadata(urns=urns)

        if metadata is not None and len(metadata) > 0:
            return metadata.to_json(orient='records', force_ascii=False)
        return "No metadata available"
    except Exception as e:
        return f"Error getting corpus statistics: {str(e)}"


def _make_parser():
    """Build the CLI argument parser. Factored out so tests can exercise the
    actual production parser instead of re-declaring it (which is drift-prone:
    any new flag added here must also be added to the test mirror, and the
    test passes regardless of whether main() ever wires the flag through)."""
    import argparse

    parser = argparse.ArgumentParser(description="DHLAB MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "http", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind to when using http/sse transport (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to when using http/sse transport (default: 8000)",
    )
    return parser


def main():
    """Run the MCP server."""
    args = _make_parser().parse_args()

    if args.transport in ("http", "sse"):
        mcp.run(transport=args.transport, host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
