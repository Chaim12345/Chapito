import time
import logging
import asyncio
import pyperclip
from bs4 import BeautifulSoup, Tag

from chapito.config import Config
from chapito.tools.tools import create_driver, transfer_prompt, wait_for_element, find_element, click_element, wait_for_element_visible, wait_for_element_clickable, navigate_to, get_page_source, close_browser, execute_script
from pydoll.constants import By

URL: str = "https://duck.ai/"
TIMEOUT_SECONDS: int = 120
SUBMIT_CSS_SELECTOR: str = 'button[type="submit"][aria-label="Send"]'
ANSWER_XPATH: str = "//div[@heading]"


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


async def scroll_down(page):
    """Scroll down to see the latest response."""
    try:
        form_element = await page.find(by=By.XPATH, value="//form[@autocomplete='off']")
        if form_element:
            div_element = await form_element.find(by=By.XPATH, value="./ancestor::div[1]")
            if div_element:
                scrollable_div = await div_element.find(by=By.TAG_NAME, value="div")
                if scrollable_div:
                    await execute_script(page, "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
                else:
                    logging.warning("No scrollable div found.")
    except Exception as e:
        logging.warning(f"Error scrolling down: {e}")


async def get_answer_from_copy_button(page) -> str:
    """Get the answer by clicking the copy button and reading from clipboard."""
    try:
        message_bubbles = await page.find(by=By.XPATH, value=ANSWER_XPATH, find_all=True)
        if not message_bubbles:
            logging.warning("No message found.")
            return ""
        
        last_message_bubble = message_bubbles[-1]
        copy_button = await last_message_bubble.find(by=By.XPATH, value="//*[@data-copyairesponse='true']")
        
        if copy_button:
            await click_element(copy_button)
            await asyncio.sleep(0.5)  # Wait for clipboard to be updated
            return pyperclip.paste()
        else:
            logging.warning("Copy button not found")
            return ""
            
    except Exception as e:
        logging.warning(f"Error getting answer from copy button: {e}")
        return ""


async def get_last_response(page) -> str:
    """Get the last AI response text."""
    try:
        # Scroll down to see the latest response
        await scroll_down(page)
        
        # Try to get answer from copy button
        message = ""
        remaining_attempts = 5
        while not message and remaining_attempts > 0:
            await asyncio.sleep(1)
            message = await get_answer_from_copy_button(page)
            remaining_attempts -= 1

        if not message:
            logging.warning("No message found.")
            return ""
        
        clean_message = clean_chat_answer(message)
        return clean_message
        
    except Exception as e:
        logging.error(f"Error getting last response: {e}")
        return ""


def clean_chat_answer(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


async def chat_with_duckduckgo(page, message: str) -> str:
    """Main function to chat with DuckDuckGo AI."""
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
        logging.error(f"Error in chat_with_duckduckgo: {e}")
        return f"Error: {str(e)}"


async def main():
    """Main function to demonstrate the chat functionality."""
    browser = None
    try:
        # Create browser
        browser = await create_driver()
        page = await browser.get_page()
        
        # Navigate to DuckDuckGo AI
        if not await navigate_to(page, URL):
            logging.error("Failed to navigate to DuckDuckGo AI")
            return
        
        # Wait for chat to load
        if not await wait_for_chat_to_load(page):
            logging.error("Chat failed to load")
            return
        
        # Example chat
        message = "Hello! How are you today?"
        response = await chat_with_duckduckgo(page, message)
        print(f"DuckDuckGo AI Response: {response}")
        
    except Exception as e:
        logging.error(f"Error in main: {e}")
    finally:
        if browser:
            await close_browser(browser)


if __name__ == "__main__":
    asyncio.run(main())
