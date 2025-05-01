from django.contrib.staticfiles.testing import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


class GameOfLifeSeleniumTests(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Remove to view the browser
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        cls.driver = webdriver.Chrome(options=chrome_options)
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.driver.get(self.live_server_url + "/game/")
        time.sleep(2)
        self.wait = WebDriverWait(self.driver, 10)

    def test_1_homepage_loads(self):
        """Page loads with the correct title"""
        self.assertIn("Conway", self.driver.title)

    def test_2_grid_is_visible(self):
        """Game grid is present"""
        cells = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "cell")))
        self.assertGreater(len(cells), 0)

    def test_3_toggle_cell_on_click(self):
        """Clicking a cell toggles its class"""
        cell = self.driver.find_element(By.CLASS_NAME, "cell")
        old_class = cell.get_attribute("class")
        cell.click()
        new_class = cell.get_attribute("class")
        self.assertNotEqual(old_class, new_class)

    def test_4_save_input_exists(self):
        """Check that save input box is visible"""
        input_box = self.driver.find_element(By.ID, "save-input")
        self.assertTrue(input_box.is_displayed())

    def test_5_save_button_works(self):
        """Clicking save does not throw error (mock test for now)"""
        self.driver.find_element(By.ID, "save-name-input").send_keys("test")
        save_btn = self.driver.find_element(By.ID, "save-button")
        save_btn.click()
        # Optional: Check for success message or no crash
        time.sleep(1)

    def test_6_load_dropdown_exists(self):
        """Dropdown for loading saved states appears"""
        dropdown = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "load-state-select"))
        )
        self.assertTrue(dropdown.is_displayed())

    def test_7_load_button_works(self):
        """Load button is enabled"""
        self.driver.get(self.live_server_url + "/game/")
        wait = WebDriverWait(self.driver, 10)
        load_btn = wait.until(EC.element_to_be_clickable((By.ID, "load-state-button")))
        self.assertTrue(load_btn.is_enabled())

    def test_8_start_requires_admin(self):
        """Only admin can see start button (assumes current user is not admin)"""
           # Try to find the element by class name instead of ID
        start_btns = self.driver.find_elements(By.CLASS_NAME, "start-button")
        # If user is not admin, they shouldn't see the button
        self.assertEqual(len(start_btns), 0)

    def test_9_multiple_cells_toggle(self):
        """Clicking multiple cells toggles them"""
        cells = self.driver.find_elements(By.CLASS_NAME, "cell")
        for cell in cells[:5]:
            cell.click()
            self.assertIn("alive", cell.get_attribute("class"))

    def test_10_clear_button_clears_grid(self):
        """Clear button resets the grid"""
        # First, toggle a cell
        cell = self.driver.find_element(By.CLASS_NAME, "cell")
        cell.click()
        self.assertIn("alive", cell.get_attribute("class"))
        # Then clear
        clear_btn = self.driver.find_element(By.ID, "clear-button")
        clear_btn.click()
        time.sleep(1)
        self.assertNotIn("alive", cell.get_attribute("class"))

