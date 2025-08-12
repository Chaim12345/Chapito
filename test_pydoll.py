#!/usr/bin/env python3
"""
Test script to verify pydoll integration.
This script tests basic browser functionality without requiring actual chatbot websites.
"""

import asyncio
import logging
from pydoll.browser import Chrome
from pydoll.constants import By
from chapito.tools.tools import get_new_page

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_basic_browser_functionality():
    """Test basic browser functionality with pydoll."""
    browser = None
    try:
        logger.info("Starting pydoll browser test...")
        
        # Create browser
        browser = Chrome()
        await browser.start()
        logger.info("Browser started successfully")
        
        # Get page
        page = await get_new_page(browser)
        logger.info("Page created successfully")
        
        # Navigate to a simple page
        await page.go_to("https://httpbin.org/html")
        logger.info("Navigated to test page successfully")
        
        # Get page title
        page_source = await page.page_source
        if "Herman Melville" in page_source:  # This should be in the test page
            logger.info("Page content loaded correctly")
        else:
            logger.warning("Page content may not have loaded as expected")
        
        # Take a screenshot
        screenshot = await page.take_screenshot(as_base64=True)
        if screenshot:
            logger.info("Screenshot taken successfully")
        else:
            logger.warning("Screenshot failed")
        
        # Test element finding
        elements = await page.find(by=By.TAG_NAME, value="h1", find_all=True)
        if elements:
            logger.info(f"Found {len(elements)} h1 elements")
            for i, element in enumerate(elements):
                text = await element.text
                logger.info(f"H1 {i+1}: {text}")
        else:
            logger.warning("No h1 elements found")
        
        logger.info("All basic tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False
        
    finally:
        if browser:
            await browser.stop()
            logger.info("Browser stopped")


async def test_element_interaction():
    """Test element interaction capabilities."""
    browser = None
    try:
        logger.info("Starting element interaction test...")
        
        # Create browser
        browser = Chrome()
        await browser.start()
        page = await get_new_page(browser)
        
        # Navigate to a form page
        await page.go_to("https://httpbin.org/forms/post")
        logger.info("Navigated to form page")
        
        # Find form elements
        input_elements = await page.find(by=By.TAG_NAME, value="input", find_all=True)
        if input_elements:
            logger.info(f"Found {len(input_elements)} input elements")
            
            # Test typing in the first text input
            for element in input_elements:
                input_type = await element.get_attribute("type")
                if input_type == "text":
                    await element.insert_text("Test input from pydoll")
                    logger.info("Successfully typed text into input field")
                    break
        else:
            logger.warning("No input elements found")
        
        logger.info("Element interaction test completed!")
        return True
        
    except Exception as e:
        logger.error(f"Element interaction test failed: {e}")
        return False
        
    finally:
        if browser:
            await browser.stop()


async def main():
    """Run all tests."""
    logger.info("=" * 50)
    logger.info("PYDOLL INTEGRATION TEST SUITE")
    logger.info("=" * 50)
    
    # Test 1: Basic browser functionality
    test1_result = await test_basic_browser_functionality()
    
    # Test 2: Element interaction
    test2_result = await test_element_interaction()
    
    # Summary
    logger.info("=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    logger.info(f"Basic browser functionality: {'PASS' if test1_result else 'FAIL'}")
    logger.info(f"Element interaction: {'PASS' if test2_result else 'FAIL'}")
    
    if test1_result and test2_result:
        logger.info("All tests passed! Pydoll integration is working correctly.")
    else:
        logger.error("Some tests failed. Please check the logs above.")
    
    logger.info("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())