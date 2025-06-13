from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

class JobAgent:
    def __init__(self):
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def apply_to_job(self, job_url):
        self.driver.get(job_url)
        time.sleep(2)  # wait for page to load

        try:
            # Example: Fill out form (update these as per actual form)
            self.driver.find_element(By.NAME, "name").send_keys("Your Name")
            self.driver.find_element(By.NAME, "email").send_keys("your@email.com")
            self.driver.find_element(By.NAME, "mobile").send_keys("1234567890")
            
            # Resume upload
            resume_path = "/absolute/path/to/your/resume.pdf"
            self.driver.find_element(By.NAME, "resume").send_keys(resume_path)

            # Click submit button
            self.driver.find_element(By.XPATH, "//button[contains(text(),'Submit')]").click()

            print("✅ Application submitted.")

        except Exception as e:
            print("❌ Failed to apply:", str(e))

        time.sleep(3)
        self.driver.quit()
