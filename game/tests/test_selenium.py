import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time

class ConwayGameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.get("http://3.147.85.8:8000/login/")
        cls.driver.set_window_size(1920, 1080)

    def test_01_login_page_loads(self):
        self.assertIn("Login", self.driver.title)

    def test_02_can_login(self):
        self.driver.find_element(By.NAME, "username").send_keys("dillontest")
        self.driver.find_element(By.NAME, "password").send_keys("test12345")  # Replace with correct password
        self.driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(1)
        self.assertIn("Welcome", self.driver.page_source)

    def test_03_navigate_to_game(self):
        self.driver.find_element(By.LINK_TEXT, "Game").click()
        time.sleep(1)
        self.assertIn("Click cells to bring them to life", self.driver.page_source)

    def test_04_game_grid_exists(self):
        grid = self.driver.find_element(By.ID, "grid")
        self.assertIsNotNone(grid)

    def test_05_learn_more_link(self):
        self.driver.find_element(By.LINK_TEXT, "Learn More").click()
        time.sleep(1)
        self.assertIn("What is Conway’s Game of Life?", self.driver.page_source)

    def test_06_back_to_game_button(self):
        self.driver.find_element(By.LINK_TEXT, "← Back to the Game").click()
        time.sleep(1)
        self.assertIn("Click cells to bring them to life", self.driver.page_source)

    def test_07_account_page_displays(self):
        self.driver.find_element(By.LINK_TEXT, "Account").click()
        time.sleep(1)
        self.assertIn("dillontest's Hub", self.driver.page_source)

    def test_08_can_save_state_input_visible(self):
        self.driver.find_element(By.LINK_TEXT, "Game").click()
        time.sleep(1)
        input_field = self.driver.find_element(By.ID, "save-name-input")
        self.assertTrue(input_field.is_displayed())

    def test_09_status_indicator_present(self):
        status = self.driver.find_element(By.ID, "simulation-status")
        self.assertIn("Status: Paused", status.text)

    def test_10_logout_works(self):
        self.driver.find_element(By.LINK_TEXT, "Logout").click()
        time.sleep(1)
        self.assertIn("Login", self.driver.page_source)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main()

