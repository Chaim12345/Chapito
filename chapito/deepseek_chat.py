import time
import logging
import asyncio
from bs4 import BeautifulSoup, Tag

from chapito.config import Config
from chapito.tools.tools import create_driver, transfer_prompt, wait_for_element, find_element, click_element, wait_for_element_visible, wait_for_element_clickable, navigate_to, get_page_source, close_browser, get_new_page
from pydoll.constants import By

URL: str = "https://chat.deepseek.com/"
TIMEOUT_SECONDS: int = 120
SUBMIT_CSS_SELECTOR: str = 'div[role="button"]'
SUBMIT_DISABLE_CSS_SELECTOR: str = 'div[role="button"][aria-disabled="true"]'
ANSWER_XPATH: str = "//div[contains(@class, 'ds-markdown') and contains(@class, 'ds-markdown--block')]"


async def check_if_chat_loaded(page) -> bool:
    try:
        button = await wait_for_element(page, By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR, timeout=5)
        return button is not None
    except Exception as e:
        logging.error(f"Error checking if chat loaded: {e}")
        return False


async def wait_for_chat_to_load(page) -> bool:
    """Wait for the chat interface to fully load."""
    start_time = time.time()
    while time.time() - start_time < TIMEOUT_SECONDS:
        if await check_if_chat_loaded(page):
            logging.info("Chat interface loaded successfully")
            return True
        await asyncio.sleep(1)
    
    logging.error("Chat interface failed to load within timeout")
    return False


async def send_message(page, message: str) -> bool:
    """Send a message to the chat interface."""
    try:
        # Find and click the textarea
        textarea = await page.find(by=By.TAG_NAME, value="textarea")
        if not textarea:
            logging.error("No textarea found")
            return False
        
        await textarea.click()
        await textarea.insert_text(message)
        
        # Find and click the submit button
        submit_buttons = await page.find(by=By.CSS_SELECTOR, value=SUBMIT_CSS_SELECTOR, find_all=True)
        if not submit_buttons:
            logging.error("Submit button not found")
            return False
        
        submit_button = submit_buttons[-1]  # Use the last submit button
        await click_element(submit_button)
        logging.info("Message sent successfully")
        return True
        
    except Exception as e:
        logging.error(f"Error sending message: {e}")
        return False


async def wait_for_response(page) -> bool:
    """Wait for the AI response to appear."""
    try:
        start_time = time.time()
        while time.time() - start_time < TIMEOUT_SECONDS:
            # Check if response has appeared
            response_elements = await page.find(by=By.XPATH, value=ANSWER_XPATH, find_all=True)
            if response_elements:
                logging.info("Response received")
                return True
            
            await asyncio.sleep(1)
        
        logging.error("Response timeout")
        return False
        
    except Exception as e:
        logging.error(f"Error waiting for response: {e}")
        return False


async def get_last_response(page) -> str:
    """Get the last AI response text."""
    try:
        response_elements = await page.find(by=By.XPATH, value=ANSWER_XPATH, find_all=True)
        if response_elements:
            last_response = response_elements[-1]
            html = await last_response.get_attribute("outerHTML")
            clean_message = clean_chat_answer(html)
            return clean_message
        return ""
        
    except Exception as e:
        logging.error(f"Error getting last response: {e}")
        return ""


def clean_chat_answer(html: str) -> str:
    """
    Find all DIVs containing code and remove unnecessary decorations.
    """
    logging.debug("Clean chat answer")
    soup = BeautifulSoup(html, "html.parser")
    no_prose_divs = soup.find_all("div", class_="md-code-block")
    for div in no_prose_divs:
        if isinstance(div, Tag):
            code_tags = div.find_all("pre")
            div.clear()
            for code in code_tags:
                div.append(code)
        else:
            code_tags = []

    code_tags = soup.find_all("pre")
    for code_tag in code_tags:
        code_tag.insert_before("\n```\n")
        code_tag.insert_after("\n```\n")
    return soup.get_text().strip()


async def chat_with_deepseek(page, message: str) -> str:
    """Main function to chat with DeepSeek."""
    try:
        # Send the message
        if not await send_message(page, message):
            return "Error: Failed to send message"
        
        # Wait for response
        if not await wait_for_response(page):
            return "Error: Response timeout"
        
        # Get the response
        response = await get_last_response(page)
        
        return response
        
    except Exception as e:
        logging.error(f"Error in chat_with_deepseek: {e}")
        return f"Error: {str(e)}"


async def main():
    """Main function to demonstrate the chat functionality."""
    browser = None
    try:
        # Create browser
        browser = await create_driver()
        page = await get_new_page(browser)
        
        # Navigate to DeepSeek
        if not await navigate_to(page, URL):
            logging.error("Failed to navigate to DeepSeek")
            return
        
        # Wait for chat to load
        if not await wait_for_chat_to_load(page):
            logging.error("Chat failed to load")
            return
        
        # Example chat
        message = "Hello! How are you today?"
        response = await chat_with_deepseek(page, message)
        print(f"DeepSeek Response: {response}")
        
    except Exception as e:
        logging.error(f"Error in main: {e}")
    finally:
        if browser:
            await close_browser(browser)


if __name__ == "__main__":
    asyncio.run(main())
