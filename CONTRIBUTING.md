# Contributing to ModbustoWELD

Thank you for considering contributing to ModbustoWELD! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ModbustoWELD.git
   cd ModbustoWELD
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Running Tests

Run the integration test suite:
```bash
python test_integration.py
```

Run manual tests with the test client:
```bash
# Terminal 1: Start mock WLED server
python mock_wled_server.py

# Terminal 2: Start the bridge
python main.py --config config.test.yaml

# Terminal 3: Run test client
python test_client.py
```

### Testing with Real WLED Device

1. Edit `config.yaml` with your WLED device IP
2. Start the bridge:
   ```bash
   python main.py
   ```
3. Test with the client:
   ```bash
   python test_client.py
   ```

## Code Style

- Follow PEP 8 Python style guidelines
- Use meaningful variable and function names
- Add docstrings to classes and functions
- Keep functions focused and concise
- Add type hints where appropriate

## Making Changes

### Types of Contributions

- **Bug Fixes**: Fix issues in the existing code
- **Features**: Add new functionality
- **Documentation**: Improve or add documentation
- **Tests**: Add or improve test coverage
- **Examples**: Add usage examples

### Before Submitting

1. Test your changes thoroughly
2. Update documentation if needed
3. Add examples if adding new features
4. Ensure all tests pass
5. Check code style

### Commit Messages

Write clear, descriptive commit messages:
- Use present tense ("Add feature" not "Added feature")
- Keep first line under 50 characters
- Add detailed description if needed

Example:
```
Add support for WLED presets

- Implement preset loading via Modbus register
- Add preset register to documentation
- Update test suite with preset tests
```

## Submitting Changes

1. Push your changes to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
2. Open a Pull Request on GitHub
3. Describe your changes clearly in the PR description
4. Reference any related issues

## Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass
- Be responsive to feedback

## Feature Requests

Have an idea for a new feature? Great!

1. Check if it's already been suggested in Issues
2. Open a new issue with the "enhancement" label
3. Describe the feature and its use case
4. Discuss the implementation approach

## Bug Reports

Found a bug? Help us fix it!

1. Check if it's already reported in Issues
2. Open a new issue with the "bug" label
3. Include:
   - Description of the bug
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or error messages

## Areas for Contribution

Here are some areas where contributions would be especially welcome:

### High Priority
- Additional WLED features (presets, segments, effects)
- Performance optimizations
- Error handling improvements
- More comprehensive tests

### Medium Priority
- Support for multiple WLED devices
- Configuration validation
- Web UI for monitoring
- Metrics and monitoring

### Low Priority
- Additional protocol support (RTU, ASCII)
- GUI configuration tool
- Cloud integration
- Mobile app

## Questions?

If you have questions about contributing:
- Open an issue with the "question" label
- Check existing issues and discussions
- Review the README and examples

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Assume good intentions

### Unacceptable Behavior

- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing others' private information

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes for significant contributions
- Special mentions for major features

Thank you for contributing to ModbustoWELD! 🎉
