#!/usr/bin/env python3
"""
LinkedIn Profile Scraper
Usage: python3 linkedin_scraper.py
"""

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import json
import time
import csv
import sys
import os


class LinkedInScraper:
    def __init__(self, headless=False):
        """Initialize the scraper with Firefox options"""
        self.firefox_options = Options()
        self.firefox_options.add_argument("--disable-dev-shm-usage")
        self.firefox_options.add_argument("--no-sandbox")
        self.firefox_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        if headless:
            self.firefox_options.add_argument("--headless")
        
        # Initialize driver (will be set when scraper starts)
        self.driver = None
        
    def start_driver(self):
        """Start the Firefox WebDriver"""
        try:
            # Use geckodriver (Firefox driver)
            # Make sure geckodriver is in your PATH or specify the path
            self.driver = webdriver.Firefox(options=self.firefox_options)
            self.driver.implicitly_wait(10)
            return True
        except Exception as e:
            print(f"Error starting Firefox driver: {e}")
            print("Make sure you have geckodriver installed and in your PATH")
            print("Download from: https://github.com/mozilla/geckodriver/releases")
            return False
    
    def login(self, email, password):
        """Login to LinkedIn"""
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(2)
            
            # Find and fill email
            email_field = self.driver.find_element(By.ID, "username")
            email_field.send_keys(email)
            
            # Find and fill password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                print("Login successful!")
                return True
            else:
                print("Login failed. Check credentials.")
                return False
                
        except Exception as e:
            print(f"Login error: {e}")
            return False
    
    def search_profiles(self, search_query, max_results=10):
        """Search for LinkedIn profiles"""
        try:
            # Navigate to people search
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}"
            self.driver.get(search_url)
            time.sleep(3)
            
            profiles = []
            profile_links = set()
            
            # Scroll and collect profile links
            last_height = self.driver.execute_script("return document.body.scrollHeight")
            
            while len(profile_links) < max_results:
                # Scroll down
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Find profile links
                elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/in/')]")
                
                for element in elements:
                    href = element.get_attribute('href')
                    if '/in/' in href and '?' not in href:
                        profile_links.add(href)
                        
                    if len(profile_links) >= max_results:
                        break
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height
            
            print(f"Found {len(profile_links)} profile links")
            return list(profile_links)[:max_results]
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def scrape_profile(self, profile_url):
        """Scrape individual LinkedIn profile"""
        try:
            self.driver.get(profile_url)
            time.sleep(3)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pv-text-details__left-panel"))
            )
            
            # Get page source for BeautifulSoup parsing
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            profile_data = {}
            
            # Extract basic information
            try:
                # Name
                name_element = soup.find('h1', class_='text-heading-xlarge')
                profile_data['name'] = name_element.get_text().strip() if name_element else "N/A"
                
                # Title
                title_element = soup.find('div', class_='text-body-medium')
                profile_data['title'] = title_element.get_text().strip() if title_element else "N/A"
                
                # Location
                location_elements = soup.find_all('span', class_='text-body-small')
                location = "N/A"
                for elem in location_elements:
                    if elem.get_text().strip() and ',' in elem.get_text():
                        location = elem.get_text().strip()
                        break
                profile_data['location'] = location
                
                # About section
                about_section = soup.find('div', class_='pv-shared-text-with-see-more')
                if about_section:
                    about_text = about_section.find('span', {'aria-hidden': 'true'})
                    profile_data['about'] = about_text.get_text().strip() if about_text else "N/A"
                else:
                    profile_data['about'] = "N/A"
                
                # Profile URL
                profile_data['profile_url'] = profile_url
                
                print(f"Scraped: {profile_data['name']}")
                return profile_data
                
            except Exception as e:
                print(f"Error parsing profile data: {e}")
                return None
                
        except Exception as e:
            print(f"Error scraping profile {profile_url}: {e}")
            return None
    
    def save_to_csv(self, profiles, filename="linkedin_profiles.csv"):
        """Save profiles to CSV file"""
        if not profiles:
            print("No profiles to save")
            return
            
        fieldnames = ['name', 'title', 'location', 'about', 'profile_url']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for profile in profiles:
                if profile:
                    writer.writerow(profile)
        
        print(f"Saved {len(profiles)} profiles to {filename}")
    
    def save_to_json(self, profiles, filename="linkedin_profiles.json"):
        """Save profiles to JSON file"""
        if not profiles:
            print("No profiles to save")
            return
            
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(profiles, jsonfile, indent=2, ensure_ascii=False)
        
        print(f"Saved {len(profiles)} profiles to {filename}")
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()


def main():
    """Main function to run the scraper"""
    print("LinkedIn Profile Scraper")
    print("=" * 50)
    
    # Initialize scraper
    scraper = LinkedInScraper(headless=False)  # Set to True for headless mode
    
    if not scraper.start_driver():
        sys.exit(1)
    
    try:
        # Get credentials
        print("\nLogin to LinkedIn:")
        email = input("Email: ")
        password = input("Password: ")
        
        # Login
        if not scraper.login(email, password):
            sys.exit(1)
        
        # Get search parameters
        search_query = input("\nEnter search query (e.g., 'python developer'): ")
        max_results = int(input("Number of profiles to scrape (default 5): ") or "5")
        
        # Search for profiles
        print(f"\nSearching for '{search_query}'...")
        profile_links = scraper.search_profiles(search_query, max_results)
        
        if not profile_links:
            print("No profiles found")
            return
        
        # Scrape profiles
        print(f"\nScraping {len(profile_links)} profiles...")
        profiles = []
        
        for i, link in enumerate(profile_links, 1):
            print(f"Scraping profile {i}/{len(profile_links)}")
            profile_data = scraper.scrape_profile(link)
            if profile_data:
                profiles.append(profile_data)
            time.sleep(2)  # Be respectful with delays
        
        # Save results
        if profiles:
            scraper.save_to_csv(profiles)
            scraper.save_to_json(profiles)
            print(f"\nScraping completed! Found {len(profiles)} profiles.")
        else:
            print("No profiles were successfully scraped")
    
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
