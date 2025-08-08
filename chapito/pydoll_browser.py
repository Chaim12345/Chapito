from pydoll import Browser
from typing import Optional
from .config import Config
import logging

class PydollBrowser:
    def __init__(self, config: Config):
        self.config = config
        self.browser: Optional[Browser] = None

    async def initialize(self) -> Browser:
        """Initialize pydoll browser with configuration"""
        try:
            self.browser = await Browser.launch(
                headless=self.config.headless,
                proxy=self.config.proxy if self.config.proxy else None
            )
            return self.browser
        except Exception as e:
            logging.error(f"Failed to initialize pydoll browser: {e}")
            raise

    async def close(self):
        """Close browser instance"""
        if self.browser:
            await self.browser.close()
            self.browser = None

    async def new_page(self):
        """Create new page in browser"""
        if not self.browser:
            await self.initialize()
        return await self.browser.new_page()

    @staticmethod
    async def wait_for_selector(page, selector: str, timeout: int = 30000):
        """Wait for element to be present on page"""
        try:
            return await page.wait_for_selector(selector, timeout=timeout)
        except Exception as e:
            logging.error(f"Timeout waiting for selector {selector}: {e}")
            raise

    @staticmethod
    async def type_text(element, text: str):
        """Type text into element"""
        await element.type(text)

    @staticmethod
    async def click(element):
        """Click on an element"""
        await element.click()

    @staticmethod
    async def get_text(element):
        """Get text content of an element"""
        return await element.inner_text()