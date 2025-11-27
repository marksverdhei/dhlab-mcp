# dhlab-mcp

MCP server providing access to [DHLAB](https://github.com/NationalLibraryOfNorway/DHLAB) (National Library of Norway Digital Humanities Lab) functionality through the Model Context Protocol.

## Overview

This server exposes tools for:
- **Text search**: Search the National Library's digital text collection
- **NGram analysis**: Analyze word frequency trends over time
- **Concordance**: Find word contexts in documents
- **Collocations**: Discover words that appear together
- **Word lookup**: Look up Norwegian word forms and lemmas
- **Image search**: Search for images in the digital collection
- **Corpus statistics**: Get information about document collections

## Installation

This project uses [`uv`](https://github.com/astral-sh/uv), which can be installed with:
```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone and install:
```bash
git clone https://github.com/marksverdhei/dhlab-mcp.git
cd dhlab-mcp
uv sync --dev
```

Or install directly:
```bash
pip install git+https://github.com/marksverdhei/dhlab-mcp.git
```

## Usage

### Configuring in Claude Code CLI

Add the MCP server to your Claude Code configuration:

```bash
# inside the repo directory:
claude mcp add --transport stdio dhlab -- uv --directory $PWD run dhlab-mcp
```
or under user scope:

```bash
claude mcp add --scope user --transport stdio dhlab -- uv --directory $PWD run dhlab-mcp
```

Verify the server is added:
```bash
claude mcp list
```

The DHLAB tools will then be available in your Claude Code sessions.

### Running the MCP Server Standalone

You can also run the server directly for testing:

```bash
dhlab-mcp
```

Or in development mode:
```bash
uv run dhlab-mcp
```

### Running as a Local HTTP API

To run the MCP server as a local HTTP API on a custom port:

```bash
# Run on default port 8000
dhlab-mcp --transport http

# Run on a custom port
dhlab-mcp --transport http --port 9000

# Run on a specific host and port
dhlab-mcp --transport http --host 0.0.0.0 --port 8080
```

The server supports the following transport options:
- `stdio` (default): Standard input/output for CLI integration
- `http`: Streamable HTTP transport (recommended for network access)
- `sse`: Server-Sent Events transport (legacy, for backward compatibility)

Once running, the HTTP server will be available at `http://<host>:<port>/mcp/`.

### Available Tools

#### 1. `search_texts`
Search for texts in the digital collection.
```python
{
  "query": "ibsen",
  "limit": 10,
  "from_year": 1900,
  "to_year": 1950,
  "media_type": "aviser"  # or "bøker", "tidsskrift"
}
```

#### 2. `ngram_frequencies`
Get word frequency trends over time.
```python
{
  "words": ["frihet", "demokrati"],
  "corpus": "bok",  # or "avis"
  "from_year": 1810,
  "to_year": 2020
}
```

#### 3. `find_concordances`
Find word contexts in a document (returns HTML-formatted text).
```python
{
  "urn": "URN:NBN:no-nb_digibok_2008051404065",
  "word": "Norge",
  "window": 25
}
```

**Output format**: HTML-formatted concordance with `<b>` tags highlighting matches.

#### 4. `word_concordance`
Find word contexts with structured output (no HTML formatting).
```python
{
  "urn": "URN:NBN:no-nb_digibok_2008051404065",
  "word": "Norge",
  "window": 12
}
```

**Output format**: Clean structured data with separate fields:
- `dhlabid`: Document identifier
- `before`: Text before the matched word
- `target`: The matched word itself
- `after`: Text after the matched word

**Use cases**:
- Use `find_concordances` for display/UI (HTML-formatted)
- Use `word_concordance` for analysis/processing (structured data)

#### 5. `find_collocations`
Find words that appear near the target word.
```python
{
  "urn": "URN:NBN:no-nb_digibok_2008051404065",
  "word": "frihet",
  "window": 5
}
```

#### 6. `lookup_word_forms`
Look up different forms of a Norwegian word.
```python
{
  "word": "løpe"
}
```

#### 7. `lookup_word_lemma`
Look up the lemma (base form) of a word.
```python
{
  "word": "løper"
}
```

#### 8. `search_images`
Search for images in the collection.
```python
{
  "query": "Oslo",
  "limit": 10,
  "from_year": 1900,
  "to_year": 1950
}
```

#### 9. `get_corpus_statistics`
Get statistics about a set of documents.
```python
{
  "urns": ["URN:NBN:no-nb_digibok_2008051404065"]
}
```

## Development

For development, install with:
```bash
uv sync --dev
uv pip install -e .
```

Run tests:
```bash
pytest
```

Format code:
```bash
ruff format src/ tests/
```

## About DHLAB

DHLAB is a Python library for qualitative and quantitative analyses of digital texts from the National Library of Norway's collection. For more information, visit:
- [DHLAB GitHub](https://github.com/NationalLibraryOfNorway/DHLAB)
- [DHLAB Documentation](https://nationallibraryofnorway.github.io/DHLAB/)

## License

See LICENSE file.
