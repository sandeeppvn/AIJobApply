from selenium import webdriver
from selenium.common.exceptions import (ElementNotInteractableException,
                                        NoSuchElementException,
                                        TimeoutException)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class LinkedInConnectorClass:
    def __init__(self, driver_path, username: str, password: str):
        # Verify driver path, username and password
        if driver_path is None:
            raise ValueError("Driver path not provided.")
        
        options = webdriver.ChromeOptions()
        options.add_argument("--incognito")
        
        cService = webdriver.ChromeService(executable_path=driver_path)

        self.driver = webdriver.Chrome(service=cService, options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 10)

        self.login(username, password)


    def login(self, username: str, password: str):
        try:
            if username is None:
                raise ValueError("LinkedIn username not provided.")
            if password is None:
                raise ValueError("LinkedIn password not provided.")
            self.driver.get('https://www.linkedin.com/login')

            username_field = self.wait.until(EC.presence_of_element_located((By.ID, 'username')))
            username_field.send_keys(username)

            password_field = self.wait.until(EC.presence_of_element_located((By.ID, 'password')))
            password_field.send_keys(password)

            login_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Sign in')]")))
            login_button.click()

        except NoSuchElementException:
            print("Error: Unable to find an element on the page.")
        except TimeoutException:
            print("Error: Timed out waiting for page elements to load.")

    def send_connection_request(self, profile_url, note):
        try:
            if profile_url is None:
                raise ValueError("LinkedIn profile URL not provided.")
            self.driver.get(profile_url)

            try:
                more_button = self.find_elements_by_text("button", "More")
                if more_button:
                    more_button[0].click()
                    connect_button = self.find_elements_by_text("span", "Connect")
                    if connect_button:
                        connect_button[0].click()
                    else:
                        print("Error: Unable to find the Connect button.")
                else:
                    print("Error: Unable to find the More button.")
            except ElementNotInteractableException:
                print("Error: Unable to click the Connect button.")

            
            add_note_button = self.find_elements_by_text("button", "Add a note")
            if add_note_button:
                add_note_button[0].click()
            else:
                print("Error: Unable to find the Add a note button.")

            note_field = self.driver.find_elements(By.ID, "custom-message")
            if note_field:
                note_field[0].send_keys(note)
            else:
                print("Error: Unable to find the note field.")

            send_button = self.find_elements_by_text("button", "Send")
            if send_button:
                send_button[0].click()
            else:
                print("Error: Unable to find the Send now button.")

        except NoSuchElementException:
            print("Error: Unable to find an element on the page.")
        except TimeoutException:
            print("Error: Timed out waiting for page elements to load.")

    def close_browser(self):
        self.driver.quit()

    def click_with_javascript(self, element):
        """
        Clicks on a given web element using JavaScript.
        """
        try:
            self.driver.execute_script("arguments[0].click();", element)
        except ElementNotInteractableException as e:
            print(f"Error while clicking element: {e}")

    def find_elements_by_text(self, tag, text):
        """
        Finds elements based on tag and text content.
        """
        elements = self.driver.find_elements(By.TAG_NAME, tag)
        return [element for element in elements if text in element.text]
