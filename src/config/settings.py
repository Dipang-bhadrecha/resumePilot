"""
Configuration settings for LinkedIn Job Screener
Modify these settings according to your preferences
"""

# Search Settings
SEARCH_SETTINGS = {
    'keywords': [
        'software engineer nodejs',
        'backend developer javascript',
        'full stack developer node.js',
        'software engineer I',
        'junior software engineer'
    ],
    'location': 'India',
    'max_jobs_per_search': 20
}

# Job Filtering Criteria
FILTER_CRITERIA = {
    'target_keywords': [
        'software engineer', 'backend developer', 'node.js', 'nodejs',
        'javascript', 'python', 'api development', 'full stack',
        'react', 'express', 'mongodb', 'sql'
    ],
    
    'avoid_keywords': [
        'senior', '5+ years', '4+ years', '3+ years', 'lead', 
        'principal', 'architect', 'manager', 'director', 'head',
        '5 years', '4 years', '3 years'
    ],
    
    'experience_keywords': [
        '0-1 years', '1-2 years', 'fresher', 'entry level',
        'junior', '1 year', 'graduate', 'new grad'
    ],
    
    'preferred_company_sizes': [
        '11-50 employees', '51-200 employees', '201-500 employees',
        '501-1000 employees', '1001-5000 employees'
    ]
}

# Output Settings
OUTPUT_SETTINGS = {
    'csv_filename': 'data/output/relevant_jobs.csv',
    'log_filename': 'data/output/logs/screening_log.txt',
    'save_all_jobs': False  # Set True to save both relevant and irrelevant jobs
}

# Selenium Settings
SELENIUM_SETTINGS = {
    'headless': False,  # Set to False to see browser window
    'page_load_timeout': 30,
    'implicit_wait': 10
}

firefox_options = FirefoxOptions()
firefox_options.add_argument("-profile")
firefox_options.add_argument("/tmp/selenium_profile")