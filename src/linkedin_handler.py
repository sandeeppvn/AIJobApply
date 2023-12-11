from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class LinkedInConnectorClass:
    def __init__(self, driver_path, username: str, password: str):
        # Verify driver path, username and password
        if driver_path is None:
            raise ValueError("Driver path not provided.")

        self.driver = webdriver.Chrome(driver_path)
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

            connect_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Connect')]")))
            connect_button.click()

            note_field = self.wait.until(EC.presence_of_element_located((By.XPATH, "//textarea[@name='message']")))
            note_field.send_keys(note)

            send_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Send')]")))
            send_button.click()

        except NoSuchElementException:
            print("Error: Unable to find an element on the page.")
        except TimeoutException:
            print("Error: Timed out waiting for page elements to load.")

    def close_browser(self):
        self.driver.quit()