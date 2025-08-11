import time
import logging
from bs4 import BeautifulSoup, Tag

from chapito.config import Config
from chapito.tools.tools import create_driver, transfer_prompt

URL: str = "https://chatgpt.com/"
TIMEOUT_SECONDS: int = 120
SUBMIT_CSS_SELECTOR: str = 'button[data-testid="send-button"]'
VOICE_CSS_SELECTOR: str = 'button[data-testid="composer-speech-button"]'
TEXTAREA_CSS_SELECTOR: str = 'div[contenteditable="true"]'
ANSWER_XPATH: str = '//div[@data-message-author-role="assistant"]'
PREFERED_RESPONSE_BUTTON_CSS_SELECTOR: str = 'button[data-testid="paragen-prefer-response-button"]'


def check_if_chat_loaded(driver) -> bool:
    driver.implicitly_wait(5)
    try:
        button = driver.find_element_by_css_selector(VOICE_CSS_SELECTOR)
    except Exception as e:
        logging.warning("Can't find submit button in chat interface. Maybe it's not loaded yet.")
        return False
    return button is not None


def initialize_driver(config: Config):
    logging.info("Initializing browser for OpenAI...")
    driver = create_driver(config)
    driver.get(URL)

    while not check_if_chat_loaded(driver):
        logging.info("Waiting for chat interface to load...")
        time.sleep(5)
    logging.info("Browser initialized")
    return driver


def send_request_and_get_response(driver, message):
    logging.debug("Send request to chatbot interface")
    driver.implicitly_wait(10)
    textarea = driver.find_element_by_css_selector(TEXTAREA_CSS_SELECTOR)
    transfer_prompt(message, textarea)
    
    # Wait for submit button to be available
    submit_button = driver.wait_for_element_by_css_selector(SUBMIT_CSS_SELECTOR, timeout=TIMEOUT_SECONDS)
    logging.debug("Push submit button")
    submit_button.click()

    # Wait a little time to avoid early fail.
    time.sleep(1)

    # Wait for submit button to be available. It means answer is finished.
    driver.wait_for_element_by_css_selector(VOICE_CSS_SELECTOR, timeout=TIMEOUT_SECONDS)

    time.sleep(1)  # OpenAI displays the button before the end of the answer.

    # Test if 2 solutions are available.
    driver.implicitly_wait(1)
    prefered_answer_buttons = driver.find_elements_by_css_selector(PREFERED_RESPONSE_BUTTON_CSS_SELECTOR)
    if len(prefered_answer_buttons) > 0:
        prefered_answer_buttons[0].click()
        time.sleep(1)
    driver.implicitly_wait(10)
    message_bubbles = driver.find_elements_by_xpath(ANSWER_XPATH)
    if not message_bubbles:
        logging.warning("No message found.")
        return ""
    last_message_bubble = message_bubbles[-1]
    html = last_message_bubble.get_attribute("outerHTML")
    clean_message = clean_chat_answer(html)
    logging.debug(f"Clean message ends with: {clean_message[-100:]}")
    return clean_message


def clean_chat_answer(html: str) -> str:
    """
    Find all DIVs containing code and remove unecessary decorations."
    """
    logging.debug("Clean chat answer")
    soup = BeautifulSoup(html, "html.parser")
    no_prose_divs = soup.find_all("pre", class_="!overflow-visible")
    for div in no_prose_divs:
        if isinstance(div, Tag):
            code_tags = div.find_all("code")
            div.clear()
            for code in code_tags:
                div.append(code)
        else:
            code_tags = []

    code_tags = soup.find_all("code")
    for code_tag in code_tags:
        code_tag.insert_before("```\n")
        code_tag.insert_after("\n```\n")
    return soup.get_text().strip()


def main():
    driver = initialize_driver(Config())
    try:
        while True:
            user_request = input("Ask something (or 'quit'): ")
            if user_request.lower() == "quit":
                break
            response = send_request_and_get_response(driver, user_request)
            print("Answer:", response)
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
