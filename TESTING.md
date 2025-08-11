# Chapito Testing Guide

This guide explains how to test Chapito chat providers both locally and in CI/CD environments.

## 🧪 Testing Tools Overview

Chapito provides several testing tools for different purposes:

1. **`test_runner.py`** - Comprehensive test runner for local and browser testing
2. **`test_api_endpoints.py`** - API endpoint testing with real HTTP requests
3. **`test_all_providers.py`** - Tests all chat providers with actual browser automation
4. **GitHub Actions** - Automated testing in CI/CD environment

## 🚀 Local Testing

### Prerequisites

- Python 3.9+
- Chrome or Firefox browser installed
- All dependencies installed: `pip install -r requirements.txt`

### Quick Local Tests (No Browser Required)

Run structural and import tests without requiring a browser:

```bash
python test_runner.py --local-only
```

This will test:
- ✅ Module imports
- ✅ Code structure
- ✅ Async function definitions
- ✅ Pydantic models

### Full Local Tests (With Browser)

Run comprehensive tests including browser functionality:

```bash
python test_runner.py --browser
```

This will test everything above plus:
- 🌐 Browser functionality
- 🔌 API structure validation

### API Endpoint Testing

Test all API endpoints with real HTTP requests:

```bash
# Start the API server first
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &

# Then test the endpoints
python test_api_endpoints.py

# Or test against a different URL
python test_api_endpoints.py --base-url http://localhost:8000
```

### Chat Provider Testing

Test all chat providers with actual browser automation:

```bash
python test_all_providers.py

# Custom test message
python test_all_providers.py --test-message "Explain quantum computing in simple terms"
```

## 🔄 CI/CD Testing (GitHub Actions)

The GitHub Actions workflow automatically runs on:
- Push to `main` or `develop` branches
- Pull requests
- Daily at 2 AM UTC
- Manual triggers

### What Gets Tested

1. **Multiple Python versions**: 3.9, 3.10, 3.11
2. **Multiple browsers**: Chrome, Firefox
3. **Code quality**: Linting, formatting, type checking
4. **Security**: Bandit, Safety scans
5. **Functionality**: Browser automation, API endpoints, chat providers

### Test Matrix

The workflow runs tests across different combinations:
- Python 3.9 + Chrome
- Python 3.9 + Firefox
- Python 3.10 + Chrome
- Python 3.10 + Firefox
- Python 3.11 + Chrome
- Python 3.11 + Firefox

## 📊 Test Results

### Local Test Output

```
🚀 Starting Chapito Tests
==================================================

🧪 Running: Module Imports
🔍 Testing module imports...
✅ pydoll imports successful
✅ chapito.tools imports successful
✅ chapito.config and types imports successful
✅ deepseek_chat import and function check successful
✅ duckduckgo_chat import and function check successful
...

🧪 Module Imports: ✅ PASS
🧪 Code Structure: ✅ PASS
🧪 Async Functions: ✅ PASS
🧪 Pydantic Models: ✅ PASS

==================================================
📊 LOCAL TEST RESULTS SUMMARY
==================================================
Total Tests: 4
✅ Successful: 4
❌ Failed: 0
Success Rate: 100.0%

🎉 ALL LOCAL TESTS PASSED! Code structure is correct.
```

### API Test Output

```
🚀 Starting API Endpoint Tests
==================================================

🔌 Testing Main API endpoints...
GET /: ✅ PASS (200) (0.045s)
GET /health: ✅ PASS (200) (0.032s)
GET /models: ✅ PASS (200) (0.038s)
POST /chat: ✅ PASS (200) (0.156s)
GET /openapi.json: ✅ PASS (200) (0.029s)

🔌 Testing Proxy API endpoints...
GET /: ✅ PASS (200) (0.031s)
GET /health: ✅ PASS (200) (0.028s)
GET /v1/health: ✅ PASS (200) (0.030s)
...

🎉 ALL API TESTS PASSED! API is working correctly.
```

### Provider Test Output

```
🚀 Starting Chat Provider Tests
==================================================

🧪 Testing deepseek_chat...
✅ deepseek_chat: Success (45 chars, 12.34s)
🧪 Testing duckduckgo_chat...
✅ duckduckgo_chat: Success (52 chars, 8.76s)
🧪 Testing gemini_chat...
✅ gemini_chat: Success (38 chars, 15.23s)
...

==================================================
📊 CHAT PROVIDER TEST RESULTS
==================================================
Total Tests: 11
✅ Successful: 11
❌ Failed: 0
Success Rate: 100.0%

🎉 ALL PROVIDER TESTS PASSED! All chat providers are working.
```

## 🛠️ Troubleshooting

### Common Issues

1. **Browser not found**
   - Install Chrome: `sudo apt-get install google-chrome-stable`
   - Install Firefox: `sudo apt-get install firefox`

2. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Browser automation failures**
   - Ensure browser is properly installed
   - Check if running in headless environment
   - Verify browser permissions

4. **API test failures**
   - Ensure API server is running
   - Check port availability
   - Verify firewall settings

### Debug Mode

For more detailed output, you can modify the logging level in the test scripts:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Timeout Issues

If tests are timing out:
- Increase timeout values in test scripts
- Check network connectivity
- Verify service availability

## 📈 Performance Metrics

The tests provide performance metrics:
- Response times for API endpoints
- Chat provider response times
- Browser automation performance
- Overall test execution time

## 🔒 Security Testing

The GitHub Actions workflow includes:
- **Bandit**: Python security linter
- **Safety**: Known vulnerability checker
- **Code quality**: Linting and formatting checks

## 📝 Adding New Tests

### Adding a New Chat Provider Test

1. Add the provider to the `providers` list in `test_all_providers.py`
2. Ensure the chat function follows the expected signature
3. Update the test matrix if needed

### Adding a New API Endpoint Test

1. Add the endpoint test to `test_api_endpoints.py`
2. Follow the existing test pattern
3. Update expected status codes and response formats

### Adding a New Test Category

1. Create a new test method in the appropriate test class
2. Add it to the test execution flow
3. Update result reporting

## 🎯 Best Practices

1. **Test locally first**: Always test changes locally before pushing
2. **Use appropriate timeouts**: Set realistic timeouts for different test types
3. **Handle failures gracefully**: Use `continue-on-error` for non-critical tests
4. **Clean up resources**: Always clean up browser drivers and connections
5. **Log everything**: Comprehensive logging helps with debugging
6. **Test edge cases**: Include error conditions and boundary cases

## 📚 Additional Resources

- [Chapito API Documentation](API_DOCUMENTATION.md)
- [OpenAPI Specification](openapi.yaml)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pydoll Documentation](https://github.com/autoscrape-labs/pydoll)