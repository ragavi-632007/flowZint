# Contributing to Fixbot

We love your input! We want to make contributing to Fixbot as easy and transparent as possible. Whether it's bug reports, feature requests, code improvements, or documentation, your contributions are welcome!

## Code of Conduct

- Be respectful and inclusive
- Welcome new contributors
- Focus on constructive feedback
- Report issues privately if needed

## Development Process

We use GitHub to host code, track issues and feature requests, and accept pull requests. Here's our workflow:

### Getting Started

1. **Fork the repository**

   ```bash
   # Click "Fork" on GitHub
   ```

2. **Clone locally**

   ```bash
   git clone https://github.com/your-username/fixbot.git
   cd fixbot
   ```

3. **Create feature branch**

   ```bash
   git checkout -b feature/amazing-feature
   # or for bug fixes:
   git checkout -b bugfix/issue-description
   ```

4. **Set up development environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. **Make your changes**
   - Write clean, documented code
   - Follow PEP 8 style guide
   - Add tests for new functionality

6. **Test thoroughly**

   ```bash
   pytest
   ```

7. **Commit with clear messages**

   ```bash
   git commit -m 'Add amazing feature: brief description'
   ```

8. **Push to your fork**

   ```bash
   git push origin feature/amazing-feature
   ```

9. **Open a Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Add detailed description
   - Click "Create Pull Request"

## Pull Request Process

1. Update documentation to reflect any new features or changes
2. Update CHANGELOG.md with details of changes
3. Ensure tests pass locally
4. Update README.md if needed
5. Provide clear description of changes in PR
6. Link any related issues

## Reporting Bugs

Before reporting, check if the issue already exists. When reporting bugs, please include:

**Required Information:**

- Python version: `python --version`
- Operating system and version
- Fixbot version
- Steps to reproduce (numbered list)
- Expected behavior
- Actual behavior
- Complete error message/traceback
- Screenshots (if applicable)

**Example Bug Report:**

```
Title: Chat API returns 500 error with special characters

Description:
When sending a message containing emoji or special characters,
the chat API returns a 500 error.

Steps to reproduce:
1. Send POST to /api/chat
2. Message body: {"message": "Hello 👋 How are you?"}
3. Observe 500 error response

Expected:
- Successful response with bot reply

Actual:
- 500 Internal Server Error

Environment:
- Python 3.9.5
- Windows 10
- Fixbot v1.0.0
```

**To create an issue:**

1. Go to [Issues](https://github.com/fixbot/fixbot/issues)
2. Click "New Issue"
3. Fill in template
4. Click "Submit new issue"

## Feature Requests

Feature requests are welcome! Please include:

- Clear description of the feature
- Use case and motivation
- Possible implementation approach
- Any potential challenges

## Code Style

We follow strict PEP 8 guidelines. Use these tools:

```bash
# Check code style
flake8 sysdoc/

# Auto-format code
black sysdoc/

# Sort imports
isort sysdoc/
```

**Guidelines:**

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) strictly
- Use meaningful variable names (no single letters except `i`, `j`, `k`)
- Maximum line length: 100 characters
- Use type hints where possible
- Add docstrings to all functions and classes (Google style)
- Keep functions focused and under 50 lines
- Add comments for complex logic (why, not what)
- Use f-strings for string formatting

**Function Example:**

```python
def get_system_health(verbose: bool = False) -> dict:
    """
    Analyze and return complete system health information.

    Args:
        verbose: If True, include detailed metrics

    Returns:
        Dictionary containing system health data with keys:
        - cpu_usage: CPU usage percentage
        - memory_usage: Memory usage percentage
        - healthy: Boolean indicating overall health

    Raises:
        PermissionError: If access denied to system info
    """
    # Implementation here
    pass
```

## Testing

**Test Requirements:**

- Write tests for all new features
- All existing tests must pass
- Aim for >80% code coverage
- Test edge cases and error conditions
- Use pytest framework

**Running Tests:**

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=sysdoc

# Run specific test file
pytest tests/test_chat.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

**Test File Structure:**

```
tests/
├── __init__.py
├── test_core/
│   ├── test_gemini_client.py
│   ├── test_executor.py
│   └── test_permission_gate.py
└── test_api/
    ├── test_health.py
    ├── test_chat.py
    └── test_system_info.py
```

## Documentation

**Documentation Updates Required For:**

| Change Type | Files to Update                     |
| ----------- | ----------------------------------- |
| New feature | README.md, docstrings, CHANGELOG.md |
| API changes | API docs, examples, CHANGELOG.md    |
| Deployment  | VERCEL_DEPLOYMENT.md, README.md     |
| Bug fix     | CHANGELOG.md, relevant docstrings   |
| Performance | README.md performance section       |

**Documentation Standards:**

- Use clear, concise language
- Include code examples for features
- Add links to related documentation
- Use proper Markdown formatting
- Keep examples up-to-date
- Document breaking changes prominently
- Include troubleshooting tips

**Docstring Format (Google Style):**

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief one-line description.

    Longer description if needed, explaining the function's
    purpose and behavior in detail.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When validation fails
        TypeError: When wrong type provided

    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

## License

By contributing, you agree that your contributions will be licensed under its MIT License.

## Questions?

Feel free to open an issue for any questions!
