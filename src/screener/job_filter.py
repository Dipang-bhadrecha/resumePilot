"""
Job filtering logic
Contains methods to determine if a job is relevant based on criteria
"""

import re
from typing import Dict, List

class JobFilter:
    def __init__(self, filter_criteria: Dict):
        self.target_keywords = [kw.lower() for kw in filter_criteria['target_keywords']]
        self.avoid_keywords = [kw.lower() for kw in filter_criteria['avoid_keywords']]
        self.experience_keywords = [kw.lower() for kw in filter_criteria['experience_keywords']]
        self.preferred_company_sizes = filter_criteria['preferred_company_sizes']
    
    def is_job_relevant(self, job_data: Dict) -> bool:
        """
        Determine if a job is relevant based on filtering criteria
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            bool: True if job is relevant, False otherwise
        """
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        company_size = job_data.get('company_size', '').lower()
        
        # Combine title and description for analysis
        job_text = f"{title} {description}"
        
        # Check 1: Must have target keywords
        has_target_keywords = self._has_target_keywords(job_text)
        
        # Check 2: Should not have avoid keywords (senior roles)
        has_avoid_keywords = self._has_avoid_keywords(job_text)
        
        # Check 3: Should match experience level
        matches_experience = self._matches_experience_level(job_text)
        
        # Check 4: Company size preference
        good_company_size = self._is_good_company_size(company_size)
        
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(
            has_target_keywords, has_avoid_keywords, 
            matches_experience, good_company_size
        )
        
        # Job is relevant if score is above threshold
        return relevance_score >= 0.6
    
    def _has_target_keywords(self, job_text: str) -> bool:
        """Check if job text contains target keywords"""
        return any(keyword in job_text for keyword in self.target_keywords)
    
    def _has_avoid_keywords(self, job_text: str) -> bool:
        """Check if job text contains keywords to avoid"""
        return any(keyword in job_text for keyword in self.avoid_keywords)
    
    def _matches_experience_level(self, job_text: str) -> bool:
        """Check if job matches desired experience level"""
        # Look for junior/entry level indicators
        has_entry_level = any(keyword in job_text for keyword in self.experience_keywords)
        
        # Look for specific year requirements that are too high
        year_patterns = [
            r'(\d+)\+?\s*years?\s*(?:of\s*)?(?:experience|exp)',
            r'(\d+)\+?\s*yrs?\s*(?:of\s*)?(?:experience|exp)',
            r'minimum\s*(\d+)\s*years?',
            r'at\s*least\s*(\d+)\s*years?'
        ]
        
        for pattern in year_patterns:
            matches = re.findall(pattern, job_text, re.IGNORECASE)
            for match in matches:
                try:
                    years = int(match)
                    if years > 2:  # More than 2 years experience required
                        return False
                except ValueError:
                    continue
        
        return True  # If no high experience requirements found
    
    def _is_good_company_size(self, company_size: str) -> bool:
        """Check if company size matches preferences"""
        if not company_size or company_size == "size not available":
            return True  # Don't filter out if size unknown
        
        return any(size.lower() in company_size for size in self.preferred_company_sizes)
    
    def _calculate_relevance_score(self, has_target: bool, has_avoid: bool, 
                                 matches_exp: bool, good_size: bool) -> float:
        """Calculate overall relevance score"""
        score = 0.0
        
        # Target keywords are mandatory
        if has_target:
            score += 0.4
        
        # Avoid keywords are heavily penalized
        if not has_avoid:
            score += 0.3
        
        # Experience match is important
        if matches_exp:
            score += 0.2
        
        # Company size is a nice-to-have
        if good_size:
            score += 0.1
        
        return score