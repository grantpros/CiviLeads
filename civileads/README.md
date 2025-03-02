# CiviLeads

A tool for finding municipal officials and tracking project opportunities.

## Overview

CiviLeads helps consultants and vendors find opportunities with municipalities by:
- Collecting and organizing municipal official contact information
- Finding and tracking upcoming municipal projects
- Analyzing vendor history and project opportunities
- Exporting leads to Excel for easy use

## Features

Current features include:
- **Municipality Database**: Store information about cities including population and location
- **Officials Tracking**: Find and store contact information for municipal officials
- **LinkedIn Integration**: Connect with officials via their professional profiles
- **Data Export**: Export all data to Excel with confidence scores

Planned features:
- Project opportunity tracking
- Vendor history analysis
- Simple GUI interface

## Project Structure

CiviLeads_Project/
├── civileads/           # Main package directory
│   ├── init.py      # Package initialization
│   ├── config.py        # Configuration settings
│   ├── database.py      # Database operations
│   └── scraper.py       # Web scraping functionality
├── scripts/             # Executable scripts
│   └── run.py           # Main execution script
├── tests/               # Test directory
├── data/                # Data storage directory
├── README.md            # This file
└── requirements.txt     # Required Python packages

## Installation

1. Clone or download this repository
2. Install required packages

pip install -r requirements.txt

## Usage

Run the main script to start collecting and organizing municipal data:

python scripts/run.py

## Roadmap

- Enhanced municipality search algorithm
- Project opportunity tracking from capital improvement plans
- Vendor history analysis
- Simple GUI interface

