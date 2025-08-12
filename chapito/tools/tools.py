import os
import platform
import time
import asyncio
from chapito.config import Config
from chapito.types import OsType
import pyperclip
import logging
import requests
import re
# Import pydoll instead of selenium
from pydoll.browser import Chrome
from pydoll.constants import By, Key


def get_os() -> OsType:
    os_name = os.name
    if os_name == "nt":
        return OsType.WINDOWS
    if os_name != "posix":
        return OsType.UNKNOWN
    return OsType.MACOS if platform.system() == "Darwin" else OsType.LINUX


async def create_driver() -> Chrome:
    """Create and return a pydoll Chrome browser instance."""
    browser = Chrome()
    await browser.start()
    return browser


async def get_new_page(browser: Chrome):
    """Return a new or existing page/tab for the given browser.

    Tries multiple method names to maintain compatibility across pydoll versions.
    """
    # Prefer explicit new tab/page creation methods if available
    if hasattr(browser, "new_tab") and callable(getattr(browser, "new_tab")):
        return await browser.new_tab()
    if hasattr(browser, "new_page") and callable(getattr(browser, "new_page")):
        return await browser.new_page()
    # Older API fallback
    if hasattr(browser, "get_page") and callable(getattr(browser, "get_page")):
        return await browser.get_page()
    # Property or callable attribute fallback
    if hasattr(browser, "page"):
        page_attr = getattr(browser, "page")
        return await page_attr() if callable(page_attr) else page_attr
    raise AttributeError("Browser has no method to create or get a page/tab")


async def paste(textarea):
    logging.debug("Paste prompt")
    await textarea.click()
    if get_os() == OsType.MACOS:
        await textarea.press_keyboard_key(Key.META, interval=0.1)
        await textarea.press_keyboard_key(Key.KEY_V, interval=0.1)
    else:
        await textarea.press_keyboard_key(Key.CONTROL, interval=0.1)
        await textarea.press_keyboard_key(Key.KEY_V, interval=0.1)


async def transfer_prompt(message, textarea) -> None:
    logging.debug("Transfering prompt to textarea")
    await textarea.click()
    await textarea.insert_text(message)


async def wait_for_element(page, by: By, value: str, timeout: int = 10):
    """Wait for an element to be present on the page."""
    try:
        element = await page.find_or_wait_element(by, value, timeout=timeout)
        return element
    except Exception as e:
        logging.error(f"Element not found: {e}")
        return None


async def find_element(page, by: By, value: str):
    """Find a single element on the page."""
    try:
        element = await page.find(by=by, value=value)
        return element
    except Exception as e:
        logging.error(f"Element not found: {e}")
        return None


async def find_elements(page, by: By, value: str):
    """Find multiple elements on the page."""
    try:
        elements = await page.find(by=by, value=value, find_all=True)
        return elements
    except Exception as e:
        logging.error(f"Elements not found: {e}")
        return []


async def click_element(element):
    """Click on an element."""
    try:
        await element.click()
        return True
    except Exception as e:
        logging.error(f"Failed to click element: {e}")
        return False


async def send_keys(element, text: str):
    """Send text to an element."""
    try:
        await element.insert_text(text)
        return True
    except Exception as e:
        logging.error(f"Failed to send keys: {e}")
        return False


async def get_text(element):
    """Get text from an element."""
    try:
        return await element.text
    except Exception as e:
        logging.error(f"Failed to get text: {e}")
        return ""


async def get_attribute(element, attribute: str):
    """Get attribute value from an element."""
    try:
        return element.get_attribute(attribute)
    except Exception as e:
        logging.error(f"Failed to get attribute: {e}")
        return None


async def is_element_present(page, by: By, value: str):
    """Check if an element is present on the page."""
    try:
        element = await page.find(by=by, value=value, raise_exc=False)
        return element is not None
    except Exception:
        return False


async def wait_for_page_load(page, timeout: int = 30):
    """Wait for the page to fully load."""
    try:
        # Wait for the page to be ready
        await asyncio.sleep(2)  # Basic wait
        return True
    except Exception as e:
        logging.error(f"Page load timeout: {e}")
        return False


async def execute_script(page, script: str):
    """Execute JavaScript on the page."""
    try:
        result = await page.execute_script(script)
        return result
    except Exception as e:
        logging.error(f"Failed to execute script: {e}")
        return None


async def take_screenshot(page, path: str = None):
    """Take a screenshot of the current page."""
    try:
        if path:
            await page.take_screenshot(path=path)
        else:
            return await page.take_screenshot(as_base64=True)
    except Exception as e:
        logging.error(f"Failed to take screenshot: {e}")
        return None


async def close_browser(browser):
    """Close the browser."""
    try:
        await browser.stop()
    except Exception as e:
        logging.error(f"Failed to close browser: {e}")


async def get_page_source(page):
    """Get the page source."""
    try:
        return await page.page_source
    except Exception as e:
        logging.error(f"Failed to get page source: {e}")
        return ""


async def get_current_url(page):
    """Get the current URL."""
    try:
        return await page.current_url
    except Exception as e:
        logging.error(f"Failed to get current URL: {e}")
        return ""


async def navigate_to(page, url: str):
    """Navigate to a URL. Tries multiple method names for compatibility."""
    try:
        if hasattr(page, "go_to") and callable(getattr(page, "go_to")):
            await page.go_to(url)
            return True
        if hasattr(page, "goto") and callable(getattr(page, "goto")):
            await page.goto(url)
            return True
        if hasattr(page, "navigate_to") and callable(getattr(page, "navigate_to")):
            await page.navigate_to(url)
            return True
        if hasattr(page, "navigate") and callable(getattr(page, "navigate")):
            await page.navigate(url)
            return True
        # Last resort: try execute_script to change location
        if hasattr(page, "execute_script"):
            await page.execute_script(f"window.location.href='{url}'")
            return True
        raise AttributeError("No known navigation method found on page object")
    except Exception as e:
        logging.error(f"Failed to navigate to {url}: {e}")
        return False


async def refresh_page(page):
    """Refresh the current page."""
    try:
        await page.refresh()
        return True
    except Exception as e:
        logging.error(f"Failed to refresh page: {e}")
        return False


async def wait_for_element_visible(page, by: By, value: str, timeout: int = 10):
    """Wait for an element to be visible."""
    try:
        element = await page.find_or_wait_element(by, value, timeout=timeout)
        await element.wait_until(is_visible=True, timeout=timeout)
        return element
    except Exception as e:
        logging.error(f"Element not visible: {e}")
        return None


async def wait_for_element_clickable(page, by: By, value: str, timeout: int = 10):
    """Wait for an element to be clickable."""
    try:
        element = await page.find_or_wait_element(by, value, timeout=timeout)
        await element.wait_until(is_interactable=True, timeout=timeout)
        return element
    except Exception as e:
        logging.error(f"Element not clickable: {e}")
        return None


def check_official_version(version: str) -> bool:
    try:
        official_version = get_last_version()
        if version == official_version:
            return True
        logging.info(f"Official version: {official_version}")
        logging.info("Please update to the latest version.")
        logging.info("More infos: https://github.com/Yajusta/Chapito")
        return False
    except Exception as e:
        logging.error(f"Error checking version: {e}")
        return False


def get_last_version() -> str:
    response = requests.get("https://raw.githubusercontent.com/Yajusta/Chapito/refs/heads/main/pyproject.toml")
    response.raise_for_status()
    if match := re.search(r'version\s*=\s*"([^"]+)"', response.text):
        return match[1]
    return "0.0.0"


def greeting(version: str) -> None:
    text = rf"""
  /██████  /██                           /██   /██              
 /██__  ██| ██                          |__/  | ██              
| ██  \__/| ███████   /██████   /██████  /██ /██████    /██████ 
| ██      | ██__  ██ |____  ██ /██__  ██| ██|_  ██_/   /██__  ██
| ██      | ██  \ ██  /███████| ██  \ ██| ██  | ██    | ██  \ ██
| ██    ██| ██  | ██ /██__  ██| ██  | ██| ██  | ██  | ██ /██| ██  | ██
|  ██████/| ██  | ██|  ███████| ███████/| ██  |  ████/|  ██████/
 \______/ |__/  |__/ \_______/| ██____/ |__/   \___/   \______/ 
                              | ██                              
                              | ██                              
                              |__/        Version {version}
"""

    print(text)
