import logging
import re

from selenium import webdriver
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class LinkedInConnectorClass:
    """
    A class to automate LinkedIn connection requests.

    Methods:
    - __init__: Initializes the class with driver, username, and password.
    - validate_input: Validates input parameters.
    - initialize_driver: Initializes the WebDriver.
    - login: Logs into LinkedIn.
    - send_connection_request: Sends a connection request to a specified LinkedIn profile.
    - click_connect_button: Clicks the "Connect" button on a LinkedIn profile.
    - add_note_and_send: Adds a note and sends the connection request.
    - enter_text: Enters text into a web element.
    - click: Clicks a web element identified by the given XPath.
    - close_browser: Closes the WebDriver browser.
    """

    def __init__(self, driver_path: str, interactive: bool = False):
        """Initializes the LinkedInConnectorClass with the given WebDriver path"""
        if not driver_path:
            raise ValueError("Driver path not provided.")
        self.logger = logging.getLogger(__name__)
        self.driver = self.initialize_driver(driver_path, interactive)
        self.wait = WebDriverWait(self.driver, 10)

    @staticmethod
    def initialize_driver(driver_path: str, interactive: bool = False):
        """Initializes the Selenium WebDriver with Chrome options."""
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if not interactive:
            options.add_argument("--headless")
        prefs = {"profile.managed_default_content_settings.images": 5,}
        options.add_experimental_option("prefs", prefs)
        service = webdriver.ChromeService(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        return driver

    def login(self, username: str, password: str):
        """Logs into LinkedIn using the provided username and password."""
        if not username or not password:
            raise ValueError("Linkedin Username or password not provided.")
        try:
            self.driver.get('https://www.linkedin.com/login')
            self.enter_text(By.ID, 'username', username)
            self.enter_text(By.ID, 'password', password)
            if not self.click("//button[@type='submit']"):
                self.logger.error("Login button click failed")
        except (NoSuchElementException, TimeoutException) as e:
            self.logger.error(f"Error while logging in: {e}")

    def send_connection_request(self, profile_url, note):
        """
        Sends a connection request to the given LinkedIn profile URL.
        Adds a note if provided.
        """
        self.click_connect_button(profile_url)
        self.add_note_and_send(note)

    def get_name_from_url(self, profile_url):
        """Extracts the name from the given LinkedIn profile URL."""
        # Extract the first name from the URL
        profile_identifier = re.search(r'/in/(.+?)/', profile_url).group(1)
        name_xpath = f"//a[contains(@href, '/in/{profile_identifier}/')]/h1[contains(@class, 'text-heading-xlarge')]"
        try:
            name_element = self.driver.find_element(By.XPATH, name_xpath)
        except NoSuchElementException:
            self.logger.error("Error while getting name from URL")
            return None
        name = name_element.text
        return name


    def click_connect_button(self, profile_url):
        """
        Navigates to the given profile URL and clicks the "Connect" button.
        If the button is within a dropdown, expands the dropdown first.
        """
        self.driver.get(profile_url)

        # Get the name from the profile URL
        name = self.get_name_from_url(profile_url)
        if not name:
            raise Exception("Error while getting name from URL")


        try:    
            xpath = (
                f"[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'invite') "
                f"and contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{name.lower()}') "
                f"and contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'to connect') "
                f"and (@role='button' or self::button)]"
            )
            
            connect_buttons_xpath = f"//button{xpath}"
                
            if not self.click(connect_buttons_xpath):
                raise Exception("No Direct clickable connect buttons found, trying dropdowns")

        except:
            
            self.logger.error("No Direct clickable connect buttons found, trying dropdowns")
                
            try:
                more_actions_buttons_xpath = f"//button[contains(@aria-label, 'More actions')]"
                if not self.click(more_actions_buttons_xpath):
                    raise Exception("No more actions buttons found")
                
                connect_divs_xpath = f"//div{xpath}"  # Assuming 'xpath' is defined earlier
                if not self.click(connect_divs_xpath):
                    raise Exception("No dropdown connect buttons found")
                
            except Exception as e:
                self.logger.error(f"Error while clicking more actions and dropdown connect buttons: {e}")
                raise Exception("Error while clicking more actions and dropdown connect buttons")

                

    def add_note_and_send(self, note):
        """Adds a note to the connection request and sends it."""
        try:
            if not self.click("//button[@aria-label='Add a note']"):
                raise Exception("No Add a note button found")
            self.enter_text(By.ID, "custom-message", note)
            
            if not self.click("//button[@aria-label='Send now']"):
                raise Exception("No Send now button found")
            
        except (NoSuchElementException, TimeoutException, ElementNotInteractableException) as e:
            self.logger.error(f"Error while adding note or sending request: {e}")

    def enter_text(self, by, locator, text):
        """Enters text into a web element identified by the given locator."""
        element = self.wait.until(EC.presence_of_element_located((by, locator)))
        element.send_keys(text)

    def click(self, xpath: str) -> bool:
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, xpath)))
            for element in elements:
                if element.is_displayed() and element.is_enabled():
                    element.click()
                    return True
        except (ElementNotInteractableException, TimeoutException, NoSuchElementException) as e:
            self.logger.error(f"Error clicking element with XPath {xpath}: {e}")
        return False

    def close_browser(self):
        """Closes the WebDriver browser."""
        self.driver.quit()
