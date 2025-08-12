import time
import logging
import asyncio
from bs4 import BeautifulSoup, Tag

from chapito.config import Config
from chapito.tools.tools import create_driver, transfer_prompt, wait_for_element, find_element, click_element, wait_for_element_visible, wait_for_element_clickable, navigate_to, get_page_source, close_browser, get_new_page
from pydoll.constants import By

URL: str = "https://chatgpt.com/"
TIMEOUT_SECONDS: int = 120
SUBMIT_CSS_SELECTOR: str = 'button[data-testid="send-button"]'
VOICE_CSS_SELECTOR: str = 'button[data-testid="composer-speech-button"]'
TEXTAREA_CSS_SELECTOR: str = 'div[contenteditable="true"]'
ANSWER_XPATH: str = '//div[@data-message-author-role="assistant"]'
PREFERED_RESPONSE_BUTTON_CSS_SELECTOR: str = 'button[data-testid="paragen-prefer-response-button"]'


async def check_if_chat_loaded(page) -> bool:
    try:
        button = await wait_for_element(page, By.CSS_SELECTOR, VOICE_CSS_SELECTOR, timeout=5)
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
        textarea = await wait_for_element_visible(page, By.CSS_SELECTOR, TEXTAREA_CSS_SELECTOR)
        if not textarea:
            logging.error("Textarea not found")
            return False
        
        # Transfer the prompt to the textarea
        await transfer_prompt(message, textarea)
        
        # Find and click the send button
        send_button = await wait_for_element_clickable(page, By.CSS_SELECTOR, SUBMIT_CSS_SELECTOR)
        if not send_button:
            logging.error("Send button not found")
            return False
        
        await click_element(send_button)
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
                # Check if the last response is from assistant
                last_response = response_elements[-1]
                if await last_response.get_attribute("data-message-author-role") == "assistant":
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
            response_text = await last_response.text
            return response_text.strip()
        return ""
        
    except Exception as e:
        logging.error(f"Error getting last response: {e}")
        return ""


async def check_for_preferred_response_button(page) -> bool:
    """Check if there's a preferred response button and click it if present."""
    try:
        button = await find_element(page, By.CSS_SELECTOR, PREFERED_RESPONSE_BUTTON_CSS_SELECTOR)
        if button:
            await click_element(button)
            logging.info("Clicked preferred response button")
            return True
        return False
        
    except Exception as e:
        logging.error(f"Error checking for preferred response button: {e}")
        return False


async def chat_with_gpt(page, message: str) -> str:
    """Main function to chat with GPT."""
    try:
        # Send the message
        if not await send_message(page, message):
            return "Error: Failed to send message"
        
        # Wait for response
        if not await wait_for_response(page):
            return "Error: Response timeout"
        
        # Get the response
        response = await get_last_response(page)
        
        # Check for preferred response button
        await check_for_preferred_response_button(page)
        
        return response
        
    except Exception as e:
        logging.error(f"Error in chat_with_gpt: {e}")
        return f"Error: {str(e)}"


async def main():
    """Main function to demonstrate the chat functionality."""
    browser = None
    try:
        # Create browser
        browser = await create_driver()
        page = await get_new_page(browser)
        
        # Navigate to ChatGPT
        if not await navigate_to(page, URL):
            logging.error("Failed to navigate to ChatGPT")
            return
        
        # Wait for chat to load
        if not await wait_for_chat_to_load(page):
            logging.error("Chat failed to load")
            return
        
        # Example chat
        message = "Hello! How are you today?"
        response = await chat_with_gpt(page, message)
        print(f"GPT Response: {response}")
        
    except Exception as e:
        logging.error(f"Error in main: {e}")
    finally:
        if browser:
            await close_browser(browser)


if __name__ == "__main__":
    asyncio.run(main())
