# Chapito - Ported to Pydoll

This project has been successfully ported from Selenium to Pydoll, a modern Python web automation library that provides better performance, reliability, and features.

## What is Pydoll?

Pydoll is a Python library for web automation that uses the Chrome DevTools Protocol (CDP) for communication with browsers. It offers:

- **Better Performance**: Direct CDP communication instead of WebDriver protocol
- **More Reliable**: Native browser integration with better error handling
- **Advanced Features**: Built-in Cloudflare bypass, network interception, and more
- **Async Support**: Full async/await support for better concurrency
- **Modern API**: Clean, intuitive API design

## Installation

### Prerequisites

- Python 3.12+
- Google Chrome browser installed
- Git (for installing pydoll from source)

### Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install manually
pip install beautifulsoup4 fastapi pyperclip requests uvicorn pydantic aiofiles
pip install pydoll @ git+https://github.com/autoscrape-labs/pydoll.git
```

## Project Structure

```
chapito/
├── tools/
│   └── tools.py          # Pydoll utility functions
├── openai_chat.py        # ChatGPT integration
├── anthropic_chat.py     # Claude integration
├── grok_chat.py          # Grok integration
├── config.py             # Configuration
├── types.py              # Type definitions
└── ...                   # Other chatbot integrations
├── main.py               # FastAPI server
├── test_pydoll.py        # Integration tests
└── requirements.txt       # Dependencies
```

## Key Changes from Selenium

### 1. Async/Await Pattern

All functions are now async and use the `await` keyword:

```python
# Old Selenium (synchronous)
def send_message(driver, message):
    textarea = driver.find_element(By.CSS_SELECTOR, "textarea")
    textarea.send_keys(message)

# New Pydoll (asynchronous)
async def send_message(page, message):
    textarea = await page.find(by=By.CSS_SELECTOR, value="textarea")
    await textarea.insert_text(message)
```

### 2. Browser Management

```python
# Old Selenium
from selenium import webdriver
driver = webdriver.Chrome()

# New Pydoll
from pydoll.browser import Chrome
browser = Chrome()
await browser.start()
page = await browser.get_page()
```

### 3. Element Finding

```python
# Old Selenium
element = driver.find_element(By.CSS_SELECTOR, "button")
elements = driver.find_elements(By.CSS_SELECTOR, "button")

# New Pydoll
element = await page.find(by=By.CSS_SELECTOR, value="button")
elements = await page.find(by=By.CSS_SELECTOR, value="button", find_all=True)
```

### 4. Element Interaction

```python
# Old Selenium
element.click()
element.send_keys("text")
element.clear()

# New Pydoll
await element.click()
await element.insert_text("text")
await element.clear()
```

## Usage Examples

### Basic Chatbot Usage

```python
import asyncio
from chapito.tools.tools import create_driver, close_browser
from chapito.openai_chat import chat_with_gpt

async def main():
    browser = await create_driver()
    page = await browser.get_page()
    
    try:
        response = await chat_with_gpt(page, "Hello! How are you?")
        print(f"GPT Response: {response}")
    finally:
        await close_browser(browser)

asyncio.run(main())
```

### FastAPI Server

```python
# Start the server
python main.py

# Or with uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

- `POST /chat` - Send a message to any supported AI model
- `GET /health` - Check server and browser status
- `GET /models` - List available AI models
- `POST /restart` - Restart the browser instance

### Example API Request

```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "What is the capital of France?",
       "model": "gpt"
     }'
```

## Testing

Run the integration tests to verify pydoll is working correctly:

```bash
python test_pydoll.py
```

This will test:
- Browser startup and navigation
- Element finding and interaction
- Screenshot capabilities
- Basic page operations

## Supported AI Models

Currently ported to pydoll:
- ✅ **OpenAI GPT** (chatgpt.com)
- ✅ **Anthropic Claude** (claude.ai)
- ✅ **xAI Grok** (grok.com)

## Configuration

The `Config` class in `chapito/config.py` can be extended to support pydoll-specific options:

```python
class Config:
    def __init__(self):
        self.browser_user_agent = "Mozilla/5.0..."
        self.use_browser_profile = False
        self.browser_profile_path = "./browser_profile"
        # Add pydoll-specific options here
```

## Troubleshooting

### Common Issues

1. **Chrome not found**: Ensure Google Chrome is installed and accessible
2. **Permission errors**: Run with appropriate permissions for browser automation
3. **Network issues**: Check firewall and proxy settings

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Browser Restart

If the browser becomes unresponsive:

```bash
curl -X POST "http://localhost:8000/restart"
```

## Performance Benefits

- **Faster Execution**: Direct CDP communication reduces overhead
- **Better Memory Management**: Native browser integration
- **Reduced Flakiness**: More reliable element detection
- **Concurrent Operations**: Async support enables better resource utilization

## Migration Guide

If you have existing Selenium code, here's how to migrate:

1. **Replace imports**:
   ```python
   # Old
   from selenium import webdriver
   from selenium.webdriver.common.by import By
   
   # New
   from pydoll.browser import Chrome
   from pydoll.constants import By
   ```

2. **Make functions async**:
   ```python
   # Old
   def my_function():
       pass
   
   # New
   async def my_function():
       pass
   ```

3. **Update element operations**:
   ```python
   # Old
   element.click()
   element.send_keys("text")
   
   # New
   await element.click()
   await element.insert_text("text")
   ```

4. **Update browser management**:
   ```python
   # Old
   driver = webdriver.Chrome()
   driver.quit()
   
   # New
   browser = Chrome()
   await browser.start()
   await browser.stop()
   ```

## Contributing

To add support for new AI models:

1. Create a new file (e.g., `new_model_chat.py`)
2. Implement the required functions using pydoll
3. Add the model to the main API router
4. Update the models endpoint

## License

This project maintains its original license while using pydoll for web automation.

## Support

For pydoll-specific issues, refer to the [pydoll documentation](https://github.com/autoscrape-labs/pydoll).

For project-specific issues, check the project's issue tracker.