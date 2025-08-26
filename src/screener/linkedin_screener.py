"""
LinkedIn Job Screener Class
Main class for scraping and screening LinkedIn jobs
"""

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
import os

from config.settings import FILTER_CRITERIA, OUTPUT_SETTINGS, SELENIUM_SETTINGS
from screener.job_filter import JobFilter
from utils.file_handler import FileHandler

class LinkedInJobScreener:
    def __init__(self):
        self.setup_driver()
        self.relevant_jobs = []
        self.all_jobs = []
        self.job_filter = JobFilter(FILTER_CRITERIA)
        self.file_handler = FileHandler()
        
    def setup_driver(self):
        """Setup Firefox driver with optimized options"""
        firefox_options = FirefoxOptions()
        firefox_options.set_preference("dom.webdriver.enabled", False)
        firefox_options.set_preference("useAutomationExtension", False)
        firefox_options.set_preference("media.volume_scale", "0.0")

        if SELENIUM_SETTINGS.get("headless", False):
            firefox_options.add_argument("--headless")

        try:
            self.driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=firefox_options
            )

            # Firefox does not support `navigator.webdriver = undefined` override
            self.driver.implicitly_wait(SELENIUM_SETTINGS.get("implicit_wait", 5))
            self.driver.set_page_load_timeout(SELENIUM_SETTINGS.get("page_load_timeout", 20))

        except Exception as e:
            print(f"❌ Failed to setup Firefox driver: {e}")
            print("💡 Make sure Firefox browser is installed")
            raise

        self.wait = WebDriverWait(self.driver, 10)
    
    def login_linkedin(self, email, password):
        """Login to LinkedIn with error handling"""
        try:
            print("🌐 Opening LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for and fill email
            email_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.clear()
            email_field.send_keys(email)
            
            # Fill password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.clear()
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for successful login
            self.wait.until(EC.url_contains("linkedin.com/feed"))
            print("✅ Successfully logged into LinkedIn")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Login failed: {e}")
            print("💡 Please check your credentials and try again")
            raise
    
    def search_jobs(self, keywords, location="India"):
        """Search for jobs with given keywords and location"""
        try:
            # Navigate to jobs page
            self.driver.get("https://www.linkedin.com/jobs/")
            time.sleep(3)
            
            # Find and fill search keyword box
            search_box = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//input[contains(@aria-label, 'Search by title')]")
            ))
            search_box.clear()
            search_box.send_keys(keywords)
            
            # Find and fill location box
            location_box = self.driver.find_element(
                By.XPATH, "//input[contains(@aria-label, 'City')]"
            )
            location_box.clear()
            location_box.send_keys(location)
            
            # Click search button
            search_button = self.driver.find_element(
                By.XPATH, "//button[contains(@aria-label, 'Search')]"
            )
            search_button.click()
            
            # Wait for results to load
            self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//ul[contains(@class, 'jobs-search__results-list')]")
            ))
            
            print(f"🔍 Search completed for: {keywords} in {location}")
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Job search failed: {e}")
            raise
    
    def screen_jobs(self, max_jobs=20):
        """Screen jobs and filter relevant ones"""
        try:
            # Find all job cards
            job_cards = self.driver.find_elements(
                By.XPATH, "//li[contains(@class, 'jobs-search-results__list-item')]"
            )
            
            print(f"📋 Found {len(job_cards)} jobs to screen...")
            
            for i, job_card in enumerate(job_cards[:max_jobs]):
                try:
                    print(f"📝 Screening job {i+1}/{min(max_jobs, len(job_cards))}")
                    
                    # Scroll job card into view
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", job_card)
                    time.sleep(1)
                    
                    # Click on job card
                    job_card.click()
                    time.sleep(2)
                    
                    # Extract job details
                    job_data = self.extract_job_details()
                    job_data['screening_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Filter the job
                    is_relevant = self.job_filter.is_job_relevant(job_data)
                    
                    if is_relevant:
                        job_data['screening_status'] = '✅ RELEVANT'
                        self.relevant_jobs.append(job_data)
                        print(f"  ✅ RELEVANT: {job_data['title']} at {job_data['company']}")
                    else:
                        job_data['screening_status'] = '❌ NOT RELEVANT'
                        print(f"  ❌ SKIP: {job_data['title']} at {job_data['company']}")
                    
                    # Store all jobs if configured
                    if OUTPUT_SETTINGS['save_all_jobs']:
                        self.all_jobs.append(job_data)
                    
                    # Small delay to avoid detection
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"  ⚠️  Error processing job {i+1}: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Job screening failed: {e}")
    
    def extract_job_details(self):
        """Extract detailed job information from current job page"""
        job_data = {}
        
        try:
            # Job title
            title_element = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(@class, 'job-title') or contains(@class, 't-24')]")
            ))
            job_data['title'] = title_element.text.strip()
        except:
            job_data['title'] = "Title not found"
        
        try:
            # Company name
            company_element = self.driver.find_element(
                By.XPATH, "//a[contains(@class, 'job-details-jobs-unified-top-card__company-name')]"
            )
            job_data['company'] = company_element.text.strip()
        except:
            job_data['company'] = "Company not found"
        
        try:
            # Location
            location_element = self.driver.find_element(
                By.XPATH, "//span[contains(@class, 'job-details-jobs-unified-top-card__bullet')]"
            )
            job_data['location'] = location_element.text.strip()
        except:
            job_data['location'] = "Location not found"
        
        try:
            # Job description
            desc_element = self.driver.find_element(
                By.XPATH, "//div[contains(@class, 'job-details-jobs-unified-top-card__job-description')]"
            )
            job_data['description'] = desc_element.text.strip()
        except:
            job_data['description'] = "Description not found"
        
        try:
            # Company size (might not always be available)
            size_elements = self.driver.find_elements(
                By.XPATH, "//span[contains(text(), 'employee') or contains(text(), 'Employee')]"
            )
            if size_elements:
                job_data['company_size'] = size_elements[0].text.strip()
            else:
                job_data['company_size'] = "Size not available"
        except:
            job_data['company_size'] = "Size not available"
        
        # Job URL
        job_data['job_url'] = self.driver.current_url
        
        return job_data
    
    def save_results(self):
        """Save screening results to files"""
        try:
            if self.relevant_jobs:
                # Save relevant jobs
                self.file_handler.save_to_csv(
                    self.relevant_jobs, 
                    OUTPUT_SETTINGS['csv_filename']
                )
                print(f"💾 Saved {len(self.relevant_jobs)} relevant jobs")
                
                # Save all jobs if configured
                if OUTPUT_SETTINGS['save_all_jobs'] and self.all_jobs:
                    all_jobs_filename = OUTPUT_SETTINGS['csv_filename'].replace('.csv', '_all_jobs.csv')
                    self.file_handler.save_to_csv(self.all_jobs, all_jobs_filename)
                    print(f"💾 Saved {len(self.all_jobs)} total jobs screened")
            else:
                print("❌ No relevant jobs found to save")
                
        except Exception as e:
            print(f"❌ Failed to save results: {e}")
    
    def show_top_jobs(self, count=5):
        """Display top relevant jobs"""
        if not self.relevant_jobs:
            print("❌ No relevant jobs to display")
            return
            
        print(f"\n🔥 TOP {min(count, len(self.relevant_jobs))} RELEVANT JOBS:")
        print("=" * 60)
        
        for i, job in enumerate(self.relevant_jobs[:count]):
            print(f"\n{i+1}. 📍 {job['title']}")
            print(f"   🏢 {job['company']}")
            print(f"   📍 {job['location']}")
            print(f"   🔗 {job['job_url']}")
            if len(job.get('description', '')) > 100:
                print(f"   📝 {job['description'][:100]}...")
    
    def close(self):
        """Close browser and cleanup"""
        try:
            self.driver.quit()
            print("🔒 Browser closed successfully")
        except:
            pass