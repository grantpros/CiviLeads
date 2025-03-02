"""
Utility functions for the CiviLeads project.

This module contains helper functions for:
- URL discovery and validation
- Data cleaning and validation
- Error handling
"""

import re
import time
import logging
import requests
from typing import List, Dict, Tuple, Optional, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("civileads.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("civileads")

# Constants
DEFAULT_TIMEOUT = 5  # seconds
MAX_RETRIES = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml",
    "Accept-Language": "en-US,en;q=0.9",
}

# Non-official indicators (terms that suggest the entry is not a municipal official)
NON_OFFICIAL_INDICATORS = [
    "investor", "innovation", "support", "development", 
    "membership", "contractor", "vendor", "supplier", "partner"
]

# Common official titles for validation
COMMON_OFFICIAL_TITLES = [
    "mayor", "city manager", "administrator", "clerk", "director", 
    "council", "councilor", "councilmember", "treasurer", "attorney",
    "manager", "supervisor", "chief", "commissioner", "engineer"
]


def generate_url_patterns(municipality: str, state: str) -> List[str]:
    """
    Generate URL patterns to try for a given municipality.
    
    Args:
        municipality: Name of the municipality
        state: Two-letter state code
        
    Returns:
        List of URL patterns to try
    """
    # Clean municipality name
    muni_clean = municipality.lower().replace(' ', '')
    muni_clean_dash = municipality.lower().replace(' ', '-')
    muni_with_state = f"{muni_clean}-{state.lower()}"
    
    # Common URL patterns
    patterns = [
        # Add common abbreviations
        f"https://www.{muni_clean[:3]}.gov",  # e.g., dsm.gov for Des Moines
        f"https://{muni_clean[:3]}.gov",      # e.g., dsm.gov without www
        
        # Standard patterns
        f"https://www.{muni_clean}.gov",
        f"https://{muni_clean}.gov",
        f"https://www.{muni_clean}.org",
        f"https://{muni_clean}.org",
        f"https://www.{muni_clean}.com",
        f"https://www.cityof{muni_clean}.gov",
        f"https://www.cityof{muni_clean}.org",
        f"https://www.cityof{muni_clean}.com",
        f"https://{muni_clean_dash}.gov",
        f"https://www.{muni_clean_dash}.gov",
        f"https://{muni_clean_dash}.org",
        f"https://www.{muni_clean_dash}.org",
    ]
    
    # Des Moines specific patterns
    if municipality.lower() == "des moines":
        patterns.insert(0, "https://www.dsm.gov")  # Add at beginning to try first
        patterns.insert(1, "https://dsm.gov")
        patterns.insert(2, "https://www.dmgov.org")
        patterns.insert(3, "https://dmgov.org")
    
    # Add state-specific patterns
    state_lower = state.lower()
    
    if len(state) == 2:  # If it's a state code
        patterns.extend([
            f"https://{muni_clean}.{state_lower}.us",
            f"https://www.{muni_clean}.{state_lower}.us",
            f"https://{muni_clean_dash}.{state_lower}.us",
            f"https://www.{muni_clean_dash}.{state_lower}.us",
            f"https://{muni_clean}.{state_lower}.gov",
            f"https://www.{muni_clean}.{state_lower}.gov",
        ])
        
    return patterns


def is_likely_municipal_site(html_content: str, municipality: str, state: str) -> bool:
    """
    Check if a website is likely a municipal website based on content.
    
    Args:
        html_content: HTML content of the page
        municipality: Name of the municipality
        state: State code
        
    Returns:
        True if it's likely a municipal website, False otherwise
    """
    html_lower = html_content.lower()
    muni_lower = municipality.lower()
    
    # Keywords that suggest a municipal website
    municipal_indicators = [
        "city hall", "town hall", "municipal", "government", "mayor", 
        "city council", "town council", "city of", "town of", "public works",
        "elected officials", "clerk", "city services", "permits", "departments",
        "residents", "business", "visitors", "community", "zoning", "planning",
        "city manager", "fire department", "police department", "recreation",
        "meeting", "agenda", "minutes", "ordinance", "code", "parks",
        "water", "sewer", "trash", "recycling", "snow removal",
        "job", "employment", "parking", "library", "emergency", "payment"
    ]

    # Extra keywords for specific cities
    city_specific = {
        "des moines": ["dsm", "dmgov", "des moines city", "polk county"],
        "cedar rapids": ["cedar rapids city", "linn county"]
    }
    
    if muni_lower in city_specific:
        municipal_indicators.extend(city_specific[muni_lower])
    
    # Check for municipal name (allowing for variations)
    name_found = muni_lower in html_lower or muni_lower.replace(' ', '') in html_lower
    name_found = name_found or (muni_lower == "des moines" and "dsm" in html_lower)
    
    # Check for state name or abbreviation
    state_found = state.lower() in html_lower
    
    # Check for municipal indicators
    indicator_count = sum(1 for indicator in municipal_indicators if indicator in html_lower)
    
    # Decision logic - Less restrictive than before
    if name_found and state_found:
        return True
    elif name_found and indicator_count >= 1:
        return True
    elif indicator_count >= 2:
        return True
    
    return False


def make_request(url: str, method: str = "GET", retry_count: int = 0, verify_ssl: bool = True) -> Optional[requests.Response]:
    """
    Make an HTTP request with retry logic.
    
    Args:
        url: URL to request
        method: HTTP method (GET, POST, etc.)
        retry_count: Current retry count
        verify_ssl: Whether to verify SSL certificates
        
    Returns:
        Response object if successful, None otherwise
    """
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=HEADERS,
            timeout=DEFAULT_TIMEOUT,
            verify=verify_ssl
        )
        return response
    except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
        # Check for SSL errors
        if isinstance(e, requests.exceptions.SSLError) and verify_ssl:
            logger.info(f"SSL error with {url}, retrying without verification")
            # Retry without SSL verification
            return make_request(url, method, retry_count, verify_ssl=False)
        elif retry_count < MAX_RETRIES:
            logger.info(f"Retrying {url} after error: {str(e)}")
            time.sleep(1)  # Wait before retrying
            return make_request(url, method, retry_count + 1, verify_ssl)
        else:
            logger.info(f"Max retries exceeded for {url}")
            return None


def find_municipal_website(municipality: str, state: str) -> Optional[str]:
    """
    Find a working municipal website by trying multiple URL patterns.
    
    Args:
        municipality: Name of the municipality
        state: Two-letter state code
        
    Returns:
        Working URL if found, None otherwise
    """
    patterns = generate_url_patterns(municipality, state)
    
    for url in patterns:
        logger.info(f"Trying URL: {url}")
        try:
            response = make_request(url)
            if response and response.status_code == 200:
                # Check if it's likely a municipal website
                if is_likely_municipal_site(response.text, municipality, state):
                    logger.info(f"Found working municipal URL: {url}")
                    return url
                else:
                    logger.info(f"URL {url} works but doesn't appear to be a municipal site")
        except Exception as e:
            logger.info(f"Error with URL {url}: {str(e)}")
    
    # Try known URLs for specific cities if the generic pattern approach failed
    if municipality.lower() == "des moines" and state.lower() == "ia":
        direct_urls = [
            "https://www.dsm.city",
            "https://dsm.city",
            "https://www.dmgov.org",
            "https://dmgov.org"
        ]
        
        for url in direct_urls:
            logger.info(f"Trying known URL for Des Moines: {url}")
            try:
                response = make_request(url)
                if response and response.status_code == 200:
                    logger.info(f"Found working URL for Des Moines: {url}")
                    return url
            except Exception as e:
                logger.info(f"Error with URL {url}: {str(e)}")
    
    logger.warning(f"No working municipal website found for {municipality}, {state}")
    return None


def find_contact_pages(base_url: str) -> List[str]:
    """
    Find contact pages on a municipal website.
    
    Args:
        base_url: Base URL of the municipal website
        
    Returns:
        List of URLs for potential contact pages
    """
    contact_pages = []
    
    # Common patterns for contact pages
    contact_paths = [
        "/contact", "/directory", "/staff", "/officials", "/elected-officials", 
        "/government", "/departments", "/administration", "/city-hall", "/about", 
        "/leadership", "/city-council", "/mayor", "/clerk", "/team",
        "/council", "/city-manager", "/contact-us", "/phone-directory",
        "/employee-directory", "/city-departments"
    ]
    
    # Check each path
    for path in contact_paths:
        url = base_url.rstrip('/') + path
        try:
            response = make_request(url)
            if response and response.status_code == 200:
                contact_pages.append(url)
                logger.info(f"Found potential contact page: {url}")
        except Exception as e:
            logger.info(f"Error checking contact page {url}: {str(e)}")
    
    return contact_pages


def validate_official_name(name: str) -> bool:
    """
    Validate if a string is likely a person's name.
    
    Args:
        name: Name to validate
        
    Returns:
        True if it's likely a person's name, False otherwise
    """
    # Check for minimum length
    if len(name) < 4:
        return False
    
    # Check for non-official indicators
    for indicator in NON_OFFICIAL_INDICATORS:
        if indicator.lower() in name.lower():
            return False
    
    # Check for typical name pattern (First Last)
    name_pattern = r'^[A-Z][a-z]+( [A-Z][a-z]+)+$'
    if re.match(name_pattern, name):
        return True
    
    # Detect suspicious names with non-name-like parts
    suspicious_parts = ['event', 'investor', 'support', 'development', 'innovation']
    for part in suspicious_parts:
        if part.lower() in name.lower():
            return False
    
    # More lenient check for names with unusual capitalization
    words = name.split()
    if len(words) >= 2 and all(len(word) >= 2 for word in words):
        return True
    
    return False


def validate_official_title(title: str) -> bool:
    """
    Validate if a string is likely an official title.
    
    Args:
        title: Title to validate
        
    Returns:
        True if it's likely an official title, False otherwise
    """
    if not title:
        return False
    
    title_lower = title.lower()
    
    # Check against common official titles
    for common_title in COMMON_OFFICIAL_TITLES:
        if common_title in title_lower:
            return True
    
    # Check for department director pattern
    if "director" in title_lower or "chief" in title_lower:
        return True
    
    # Check for non-official indicators
    for indicator in NON_OFFICIAL_INDICATORS:
        if indicator in title_lower:
            return False
    
    return len(title) >= 4  # Minimum length check


def validate_email(email: str) -> bool:
    """
    Validate if a string is a properly formatted email.
    
    Args:
        email: Email to validate
        
    Returns:
        True if it's a valid email, False otherwise
    """
    if not email:
        return False
    
    # Basic email validation pattern
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))


def validate_phone(phone: str) -> Optional[str]:
    """
    Validate and format a phone number.
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Formatted phone number if valid, None otherwise
    """
    if not phone:
        return None
    
    # Remove non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Check if it's a valid US phone number
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
    
    return None


def calculate_confidence_score(official: Dict[str, Any]) -> float:
    """
    Calculate a confidence score for an official based on data quality.
    
    Args:
        official: Dictionary with official information
        
    Returns:
        Confidence score between 0 and 1
    """
    score = 0.0
    total_weight = 0.0
    
    # Name validation (highest weight)
    if validate_official_name(official.get('name', '')):
        score += 0.4
    total_weight += 0.4
    
    # Title validation
    if validate_official_title(official.get('title', '')):
        score += 0.2
    total_weight += 0.2
    
    # Email validation
    if validate_email(official.get('email', '')):
        score += 0.2
    total_weight += 0.2
    
    # Phone validation
    if official.get('phone'):
        formatted_phone = validate_phone(official.get('phone', ''))
        if formatted_phone:
            score += 0.1
            # Update with formatted phone
            official['phone'] = formatted_phone
    total_weight += 0.1
    
    # LinkedIn profile
    if official.get('linkedin_url'):
        score += 0.1
    total_weight += 0.1
    
    # Adjust if total_weight is not 1.0
    if total_weight > 0:
        return score / total_weight
    
    return 0.0


def filter_officials(officials: List[Dict[str, Any]], min_confidence: float = 0.6) -> List[Dict[str, Any]]:
    """
    Filter and validate a list of officials.
    
    Args:
        officials: List of official dictionaries
        min_confidence: Minimum confidence score to include
        
    Returns:
        Filtered list of officials
    """
    filtered_officials = []
    
    for official in officials:
        # Calculate confidence score
        confidence = calculate_confidence_score(official)
        official['confidence_score'] = confidence
        
        # Include only if confidence is above threshold
        if confidence >= min_confidence:
            filtered_officials.append(official)
        else:
            logger.info(f"Filtered out {official.get('name', 'Unknown')} with score {confidence}")
    
    return filtered_officials