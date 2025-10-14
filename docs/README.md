# StreamForge Documentation

This directory contains the source files for StreamForge's documentation, built with [MkDocs](https://www.mkdocs.org/) and the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme.

---

## Local Development

### Prerequisites

- Python 3.8+
- pip

### Installation

Install documentation dependencies:

```bash
pip install -r docs/requirements.txt
```

Or install StreamForge with docs extras:

```bash
pip install -e ".[docs]"
```

### Serve Locally

Run a local development server with live reload:

```bash
mkdocs serve
```

Then open http://localhost:8000 in your browser.

The documentation will automatically reload when you save changes.

### Build Static Site

Build the documentation as static HTML:

```bash
mkdocs build
```

Output is in the `site/` directory.

---

## Structure

```
docs/
├── index.md                    # Home page
├── getting-started/            # Installation, quick start, concepts
├── user-guide/                 # Feature guides
├── exchanges/                  # Exchange-specific guides
├── examples/                   # Code examples
├── api-reference/              # Auto-generated API docs
├── contributing.md             # Contribution guide
├── changelog.md                # Version history
├── stylesheets/                # Custom CSS
└── requirements.txt            # Python dependencies
```

---

## Writing Documentation

### Markdown

Documentation is written in Markdown with extensions:

- **Admonitions:** `!!! note`, `!!! warning`, `!!! tip`
- **Code blocks:** With syntax highlighting
- **Tabs:** For multi-option examples
- **Tables:** GitHub-flavored markdown tables

### Code Examples

Use fenced code blocks with language:

````markdown
```python
import streamforge as sf

runner = sf.BinanceRunner(...)
```
````

### Admonitions

```markdown
!!! note "Optional Title"
    This is a note admonition.

!!! warning
    This is a warning.

!!! tip
    This is a tip.
```

### Tabs

```markdown
=== "Option 1"
    Content for option 1

=== "Option 2"
    Content for option 2
```

### API Documentation

API docs use mkdocstrings for auto-generation:

```markdown
::: streamforge.BinanceRunner
    options:
      show_root_heading: true
      show_source: false
```

---

## Deployment

Documentation is automatically deployed to GitHub Pages when pushed to the main branch.

The deployment workflow is in `.github/workflows/docs.yml`.

---

## Custom Theme

Custom styling is in `docs/stylesheets/extra.css`.

Theme configuration is in `mkdocs.yml`.

---

## Contributing

When contributing to documentation:

1. Check for typos and grammar
2. Ensure code examples work
3. Test locally with `mkdocs serve`
4. Follow the existing style
5. Update navigation in `mkdocs.yml` if adding new pages

---

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [Markdown Guide](https://www.markdownguide.org/)

---

## Questions?

For documentation-related questions, please open an issue on GitHub.

