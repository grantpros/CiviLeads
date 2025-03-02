# config.py
import os

# Project paths - updated for package structure
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# Database settings
DATABASE_PATH = os.path.join(DATA_DIR, 'civileads.db')

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Web scraping settings
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Confidence score thresholds
MIN_CONFIDENCE_SCORE = 0.5
GOOD_CONFIDENCE_SCORE = 0.7
EXCELLENT_CONFIDENCE_SCORE = 0.9