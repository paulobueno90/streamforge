# Testing Documentation Locally

This guide shows you how to build and test the StreamForge documentation on your local machine.

---

## Quick Start

### 1. Install Dependencies

From the project root:

```bash
pip install -r docs/requirements.txt
```

This installs:
- `mkdocs` - Documentation generator
- `mkdocs-material` - Material theme
- `mkdocstrings[python]` - API documentation generator
- `pymdown-extensions` - Markdown extensions

### 2. Serve Locally

```bash
mkdocs serve
```

Open your browser to: **http://localhost:8000**

The site will automatically reload when you save changes to any documentation file!

### 3. Build Static Site

```bash
mkdocs build
```

Output is in the `site/` directory.

---

## Development Workflow

### Edit Documentation

1. Open a documentation file in `docs/`
2. Make your changes
3. Save the file
4. Browser auto-refreshes (if `mkdocs serve` is running)

### Preview Changes

With `mkdocs serve` running:

1. Edit file
2. Save
3. Refresh browser (or wait for auto-reload)
4. See changes instantly

### Build for Production

```bash
mkdocs build --clean
```

The `--clean` flag removes the old site directory first.

---

## File Structure

```
docs/
├── index.md                    # Home page
├── getting-started/            # Installation & quick start
│   ├── installation.md
│   ├── quick-start.md
│   └── core-concepts.md
├── user-guide/                 # Feature guides
│   ├── emitters.md
│   ├── transformers.md
│   ├── aggregation.md
│   ├── backfilling.md
│   └── multi-exchange.md
├── exchanges/                  # Exchange-specific docs
│   ├── binance.md
│   ├── kraken.md
│   └── okx.md
├── examples/                   # Code examples
│   ├── index.md
│   ├── basic-streaming.md
│   ├── data_emitters.md
│   ├── data-transformation.md
│   └── advanced-patterns.md
├── api-reference/              # Auto-generated API docs
│   ├── index.md
│   ├── runners.md
│   ├── emitters.md
│   ├── data-models.md
│   └── backfilling.md
├── contributing.md
├── changelog.md
└── stylesheets/
    └── extra.css
```

---

## Common Tasks

### Add a New Page

1. Create the markdown file in `docs/`
2. Add it to `mkdocs.yml` navigation:

```yaml
nav:
  - Section Name:
      - Page Title: path/to/page.md
```

3. Link to it from other pages:

```markdown
[Link text](path/to/page.md)
```

### Add Code Examples

Use fenced code blocks with language:

````markdown
```python
import streamforge as sf

runner = sf.BinanceRunner(...)
```
````

### Add Admonitions

```markdown
!!! note "Optional Title"
    This is a note.

!!! warning
    This is a warning.

!!! tip
    This is a tip.

!!! info
    This is info.
```

### Add Tabs

```markdown
=== "Option 1"
    Content for option 1

=== "Option 2"
    Content for option 2
```

### Add Tables

```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
```

---

## Markdown Extensions

The documentation uses these extensions:

- **Admonitions** - `!!! note`, `!!! warning`, etc.
- **Code Highlighting** - Syntax highlighting for code blocks
- **Superfences** - Advanced code blocks
- **Tabbed** - Tabbed content sections
- **Tables** - GitHub-flavored tables
- **TOC** - Table of contents with permalinks
- **Emoji** - :material-rocket: icons

---

## Testing Checklist

Before submitting changes:

- [ ] `mkdocs serve` runs without errors
- [ ] `mkdocs build` completes successfully
- [ ] All links work (no 404s)
- [ ] Code examples are syntactically correct
- [ ] No spelling/grammar errors
- [ ] Navigation structure makes sense
- [ ] Mobile responsive (check browser dev tools)

---

## Troubleshooting

### Build Errors

**Problem:** `mkdocs build` fails

**Solutions:**

1. Check YAML syntax in `mkdocs.yml`
2. Verify all nav paths exist
3. Check for invalid markdown syntax

### Serve Not Working

**Problem:** `mkdocs serve` doesn't start

**Solutions:**

1. Check if port 8000 is already in use
2. Try a different port: `mkdocs serve -a localhost:8001`
3. Reinstall dependencies: `pip install -r docs/requirements.txt`

### Broken Links

**Problem:** Links don't work

**Solutions:**

1. Use relative paths: `../user-guide/emitters.md`
2. Ensure file exists at that path
3. Check for typos in path

### API Docs Not Generating

**Problem:** mkdocstrings not working

**Solutions:**

1. Verify package is installed: `pip install -e .`
2. Check import paths in API docs
3. Ensure docstrings exist in source code

---

## Deployment

Documentation deploys automatically via GitHub Actions:

- **Trigger:** Push to `main` or `master` branch
- **Destination:** GitHub Pages (gh-pages branch)
- **URL:** `https://paulobueno90.github.io/streamforge/`

See `.github/workflows/docs.yml` for the workflow configuration.

---

## Resources

- [MkDocs Documentation](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [mkdocstrings](https://mkdocstrings.github.io/)
- [PyMdown Extensions](https://facelessuser.github.io/pymdown-extensions/)

---

## Getting Help

If you encounter issues:

1. Check the error message carefully
2. Verify file paths in `mkdocs.yml`
3. Test in a fresh virtual environment
4. Open an issue on GitHub

