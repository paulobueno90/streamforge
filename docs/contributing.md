# Contributing to StreamForge

Thank you for your interest in contributing to StreamForge! This guide will help you get started.

---

## Ways to Contribute

### 1. Report Bugs

Found a bug? Please create an issue on GitHub:

- Use a clear, descriptive title
- Describe the expected behavior
- Describe the actual behavior
- Include steps to reproduce
- Include your environment (OS, Python version, StreamForge version)

[Report a Bug →](https://github.com/paulobueno90/streamforge/issues/new)

### 2. Suggest Features

Have an idea for a new feature?

- Check if it's already been suggested
- Clearly describe the feature and its use case
- Explain why it would be useful to other users

[Suggest a Feature →](https://github.com/paulobueno90/streamforge/issues/new)

### 3. Improve Documentation

Documentation improvements are always welcome:

- Fix typos or clarify unclear sections
- Add examples
- Improve API documentation
- Translate documentation

### 4. Submit Code

Ready to code? Here's how:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request


**Commit Message Format:**

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Adding tests
- `refactor:` - Code refactoring
- `style:` - Formatting changes
- `chore:` - Maintenance tasks


---

## Code Style

### Python Style

- Follow PEP 8
- Use black for formatting (line length: 100)
- Use type hints
- Write docstrings for public APIs

### Example

```python
from typing import List, Optional

def process_symbols(
    symbols: List[str],
    timeframe: str = "1m",
    limit: Optional[int] = None
) -> List[dict]:
    """
    Process cryptocurrency symbols.
    
    Args:
        symbols: List of trading pair symbols
        timeframe: Candle interval (default: "1m")
        limit: Maximum number of results (optional)
        
    Returns:
        List of processed data dictionaries
        
    Example:
        >>> process_symbols(["BTCUSDT"], timeframe="5m")
        [{'symbol': 'BTCUSDT', ...}]
    """
    results = []
    # Implementation...
    return results
```

### Docstring Format

Use Google-style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """
    Short description.
    
    Longer description if needed.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: If arg2 is negative
        
    Example:
        >>> function("test", 5)
        True
    """
    pass
```

---

## Documentation

### Building Docs Locally

```bash
# Install docs dependencies
pip install -r docs/requirements.txt

# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

Visit http://localhost:8000


---

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] Added tests for new features
- [ ] Updated documentation
- [ ] Commit messages are clear

### PR Description

Include in your PR:

- What problem does it solve?
- How does it solve it?
- Any breaking changes?
- Screenshots (if UI changes)

### Review Process

1. Submit PR
2. Automated checks run
3. Maintainer reviews code
4. Address feedback
5. PR is merged!

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism
- Focus on what's best for the community

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks
- Publishing private information
- Other unprofessional conduct

---

## Questions?

- **General Questions:** [GitHub Discussions](https://github.com/paulobueno90/streamforge/discussions)
- **Bug Reports:** [GitHub Issues](https://github.com/paulobueno90/streamforge/issues)
- **Email:** paulohmbueno@gmail.com

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Thank You!

Your contributions help make StreamForge better for everyone. Thank you for taking the time to contribute! 🎉

