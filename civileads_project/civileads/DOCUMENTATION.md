# CiviLeads Project Documentation

## Overview
CiviLeads is a tool to gather and organize information about municipal officials and upcoming municipal projects. It helps consultants and vendors find opportunities with municipalities by collecting contact information and tracking projects.

## Current Status
- Successfully created a structured Python package
- Implemented database operations using SQLite
- Created web scraping functionality for official contact information
- Added LinkedIn profile discovery
- Import/export functionality with Excel

## Project Structure
```
├── civileads/
│   ├── __init__.py  
│   ├── config.py    (Configuration settings)
│   ├── database.py  (Database operations)
│   ├── scraper.py   (Web scraping functionality)
│   └── utils.py     (To be created: Helper functions)
├── scripts/
│   └── run.py       (Main script)
├── tests/           (For future test cases)
├── data/            (Database and sample files)
└── requirements.txt (Dependencies)
```

## Current Issues
1. **URL Discovery Problems**: 
   - Failing to find correct municipal websites
   - Falling back to sample data too often
   
2. **Data Quality Issues**:
   - Extracting non-official entities as officials
   - Inconsistent data quality from different sources
   
3. **Structure Improvements Needed**:
   - Need better modularity and separation of concerns
   - Need improved error handling

## Development Plan

### Phase 1: Project Structure Refinement (CURRENT)
- [x] Create package structure
- [x] Set up database operations
- [x] Implement basic scraping
- [ ] Create utils.py for helper functions
- [ ] Add proper documentation
- [ ] Improve error handling

### Phase 2: Scraper Enhancement
- [ ] Improve URL discovery algorithm
- [ ] Implement better data validation
- [ ] Add more robust error handling
- [ ] Enhance LinkedIn integration

### Phase 3: Database & Data Management
- [ ] Implement data version control
- [ ] Add data cleaning tools
- [ ] Improve export functionality
- [ ] Add data quality metrics

### Phase 4: Project Opportunity Tracking
- [ ] Design database schema for projects
- [ ] Create scrapers for project documents
- [ ] Implement scoring for opportunity quality

## Current Development Task
Creating utils.py to improve URL discovery and data validation.

## Last Updated
March 2, 2025

## Development Notes
- Need to improve municipal website identification
- Need to implement better data validation to filter out non-officials
- Consider using additional sources for official data validation